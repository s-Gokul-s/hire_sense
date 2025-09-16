# train_hybrid_model.py
# This is the final, definitive training script for HireSense.
# It creates a hybrid dataset by combining the logical foundation of the
# synthetic data with the real-world nuance of our best clean dataset.
# This approach is designed to produce a robust, generalizable model.

import pandas as pd
import numpy as np
import torch
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    EarlyStoppingCallback,
)
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
import os

# --- 1. MODEL CONFIGURATION ---
MODEL_NAME = "roberta-base"
MAX_LENGTH = 512
OUTPUT_DIR = "./hiresense_hybrid_model" # Final model will be saved here

print(f"--- Training Final Hybrid Model with {MODEL_NAME} ---")

# --- 2. DATA PREPARATION (HYBRID DATASET) ---
print("Step 1: Creating a hybrid dataset...")
try:
    # --- Load Synthetic Data ---
    synthetic_path = "check/synthetic_resume_dataset.csv"
    synthetic_df = pd.read_csv(synthetic_path)
    synthetic_df.dropna(inplace=True)
    label_mapping_synth = {"No Fit": 0, "Fit": 1}
    synthetic_df['label'] = synthetic_df['label'].map(label_mapping_synth)
    print(f"Loaded {len(synthetic_df)} rows from synthetic data.")

    # --- Load and Clean Real-World Data ("Golden" Set) ---
    from datasets import load_dataset
    real_dataset = load_dataset("cnamuangtoun/resume-job-description-fit")
    real_df = pd.concat([pd.DataFrame(real_dataset['train']), pd.DataFrame(real_dataset['test'])])
    real_df.dropna(subset=['resume_text', 'job_description_text', 'label'], inplace=True)
    label_mapping_real = {"no fit": 0, "potential fit": 1, "good fit": 2}
    real_df['label'] = real_df['label'].astype(str).str.strip().str.lower().map(label_mapping_real)
    clean_real_df = real_df[real_df['label'] != 1].copy()
    clean_real_df['label'] = clean_real_df['label'].apply(lambda x: 1 if x == 2 else 0)
    print(f"Loaded and cleaned {len(clean_real_df)} rows from real-world data.")

    # --- Combine and Shuffle ---
    hybrid_df = pd.concat([synthetic_df, clean_real_df], ignore_index=True)
    # Shuffle the dataset thoroughly to mix synthetic and real examples
    hybrid_df = hybrid_df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    print(f"Created hybrid dataset with a total of {len(hybrid_df)} rows.")

    # --- Split the final hybrid data ---
    train_df, test_df = train_test_split(
        hybrid_df,
        test_size=0.2,
        random_state=42,
        stratify=hybrid_df['label']
    )

    train_dataset = Dataset.from_pandas(train_df.reset_index(drop=True))
    test_dataset = Dataset.from_pandas(test_df.reset_index(drop=True))

    print(f"Final Train size: {len(train_dataset)}, Final Test size: {len(test_dataset)}")

except Exception as e:
    print(f"Data preparation failed: {e}")
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


# --- 4. MODEL TRAINING ---
print(f"\nStep 3: Loading and Fine-Tuning {MODEL_NAME}...")
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    return {
        'accuracy': accuracy_score(labels, preds),
        'f1': f1_score(labels, preds, average='binary'),
        'precision': precision_score(labels, preds, average='binary'),
        'recall': recall_score(labels, preds, average='binary'),
    }

training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    num_train_epochs=3,
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
    seed=42,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train_dataset,
    eval_dataset=tokenized_test_dataset,
    compute_metrics=compute_metrics,
    callbacks=[EarlyStoppingCallback(early_stopping_patience=1)],
)

trainer.train()

# --- 5. FINAL EVALUATION AND SAVING ---
print("\n--- Final Evaluation on Hybrid Test Set ---")
predictions_output = trainer.predict(tokenized_test_dataset)
y_true = predictions_output.label_ids
y_pred = np.argmax(predictions_output.predictions, axis=1)
print(classification_report(y_true, y_pred, target_names=["No Fit (0)", "Fit (1)"]))

print(f"\nStep 4: Saving the final, robust hybrid model to '{OUTPUT_DIR}'...")
trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print("\n--- Process Finished ---")

