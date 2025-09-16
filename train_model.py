# train_synthetic_model.py
# This script trains the definitive HireSense model on the clean, logically-sound
# synthetic dataset to ensure its core logic is correct and trustworthy.

import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    EarlyStoppingCallback,
)
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)
from sklearn.model_selection import train_test_split

# --- 1. MODEL CONFIGURATION ---
MODEL_NAME = "roberta-base"
MAX_LENGTH = 512
# Save the new model to a distinct directory
OUTPUT_DIR = "./hiresense_synthetic_model" 

print(f"--- Training Definitive Model on Synthetic Data with {MODEL_NAME} ---")

# --- 2. DATA PREPARATION (from local synthetic file) ---
print("Step 1: Loading and preparing the synthetic dataset...")
try:
    # --- KEY CHANGE: Load the local CSV file ---
    # The path is relative to the project root where this script will be run.
    dataset_path = "check/synthetic_resume_dataset.csv"
    full_df = pd.read_csv(dataset_path)
    
    full_df.dropna(inplace=True)

    # Map string labels to integers
    label_mapping = {"No Fit": 0, "Fit": 1}
    full_df['label'] = full_df['label'].map(label_mapping)

    print(f"Loaded {len(full_df)} rows from {dataset_path}")

    # Split the clean data into training and testing sets
    train_df, test_df = train_test_split(
        full_df,
        test_size=0.2,
        random_state=42,
        stratify=full_df['label']
    )

    train_dataset = Dataset.from_pandas(train_df.reset_index(drop=True))
    test_dataset = Dataset.from_pandas(test_df.reset_index(drop=True))

    print(f"Train size: {len(train_dataset)}, Test size: {len(test_dataset)}")
    print("Label distribution in train:\n", train_df['label'].value_counts())

except FileNotFoundError:
    print(f"ERROR: Dataset not found at '{dataset_path}'")
    print("Please ensure you have run 'generate_dataset.py' and the file is in the 'check' folder.")
    exit()
except Exception as e:
    print(f"Dataset load failed: {e}")
    exit()

# --- 3. TOKENIZATION ---
print("\nStep 2: Tokenizing...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

def tokenize_function(examples):
    return tokenizer(
        examples['resume_text'],
        examples['job_description_text'],
        padding="max_length",
        truncation=True,
        max_length=MAX_LENGTH
    )

tokenized_train_dataset = train_dataset.map(tokenize_function, batched=True)
tokenized_test_dataset = test_dataset.map(tokenize_function, batched=True)
print("Tokenization complete.")

# --- 4. MODEL ---
print(f"\nStep 3: Loading {MODEL_NAME}...")
model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME, num_labels=2
)
print("Model loaded.")

# --- 5. METRICS ---
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    # Simple argmax is sufficient here, as we'll tune the threshold later
    preds = np.argmax(logits, axis=-1)
    return {
        'accuracy': accuracy_score(labels, preds),
        'f1': f1_score(labels, preds, average='binary'),
        'precision': precision_score(labels, preds, average='binary'),
        'recall': recall_score(labels, preds, average='binary'),
    }

# --- 6. TRAINING ---
print("\nStep 4: Training setup...")
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    num_train_epochs=3, # Fewer epochs needed for clean, synthetic data
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    warmup_ratio=0.1,
    weight_decay=0.01,
    logging_strategy="epoch",
    eval_strategy="epoch",
    save_strategy="epoch",
    fp16=torch.cuda.is_available(),
    load_best_model_at_end=True,
    metric_for_best_model="f1",
    greater_is_better=True,
    seed=42, # For reproducibility
)

# --- KEY CHANGE: Use the standard Trainer ---
# The synthetic data is balanced, so a custom weighted trainer is not needed.
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train_dataset,
    eval_dataset=tokenized_test_dataset,
    compute_metrics=compute_metrics,
    callbacks=[EarlyStoppingCallback(early_stopping_patience=1)], # Stop early if it learns fast
)

trainer.train()
print("Training complete.")

# --- 7. SAVE MODEL ---
print(f"\nSaving fine-tuned model to {OUTPUT_DIR}")
trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

# --- 8. FINAL EVALUATION WITH THRESHOLD TUNING ---
print("\nFinal Evaluation with threshold tuning...")
predictions_output = trainer.predict(tokenized_test_dataset)
y_true = predictions_output.label_ids
probs = torch.softmax(torch.tensor(predictions_output.predictions), dim=1)[:, 1].numpy()

# Scan thresholds to find the one that maximizes F1 score
best_f1, best_thresh = 0, 0.5
for thresh in np.linspace(0.01, 0.99, 50):
    preds = (probs >= thresh).astype(int)
    f1 = f1_score(y_true, preds)
    if f1 > best_f1:
        best_f1, best_thresh = f1, thresh

print(f"Best threshold = {best_thresh:.2f} with F1 = {best_f1:.4f}")

# Apply the best threshold to get the final predictions
y_pred = (probs >= best_thresh).astype(int)

report = classification_report(
    y_true, y_pred, target_names=["No Fit (0)", "Fit (1)"]
)
print(report)

print("\nConfusion Matrix:")
print(confusion_matrix(y_true, y_pred))

print("\n--- Finished ---")
