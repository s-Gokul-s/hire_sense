# fine_tune_model_optimized.py

import pandas as pd
import numpy as np
import torch
from datasets import load_dataset, ClassLabel
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    EarlyStoppingCallback,
)
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix
from collections import Counter

# --- We will still use Longformer, as it is the correct architecture ---
MODEL_NAME = "allenai/longformer-base-4096" 
OUTPUT_DIR = "./longformer_resume_screener_fastest"

print(f"--- Starting Model Fine-Tuning with {MODEL_NAME} ---")

# --- 1. LOAD AND PREPARE DATASET ---
print("Step 1: Loading and preparing dataset...")
try:
    dataset = load_dataset("AzharAli05/Resume-Screening-Dataset")
    dataset = dataset.filter(lambda example: example['Resume'] is not None and example['Job_Description'] is not None)
    
    def create_label(example):
        example['label'] = 1 if example['Decision'] == 'select' else 0
        return example
    
    dataset = dataset.map(create_label)
    
    dataset['train'] = dataset['train'].cast_column('label', ClassLabel(num_classes=2, names=['reject', 'select']))
    train_test_split = dataset['train'].train_test_split(test_size=0.2, seed=42, stratify_by_column='label')
    train_dataset = train_test_split['train']
    test_dataset = train_test_split['test']
    print("Dataset prepared successfully.")

except Exception as e:
    print(f"Failed to load or prepare dataset. Error: {e}")
    exit()

# --- 2. TOKENIZE THE DATA ---
print("\nStep 2: Tokenizing text data...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

# --- FINAL SPEED OPTIMIZATION: Reduce max_length to hit ~2-hour target ---
# This is a significant compromise for speed. 768 is 1.5x more than BERT (512),
# but will be much faster than 1024. This is our best bet to get under 3 hours.
MAX_LENGTH = 768 

def tokenize_function(examples):
    return tokenizer(
        examples['Resume'], 
        examples['Job_Description'], 
        padding="max_length", 
        truncation=True, 
        max_length=MAX_LENGTH 
    )

tokenized_train_dataset = train_dataset.map(tokenize_function, batched=True)
tokenized_test_dataset = test_dataset.map(tokenize_function, batched=True)
print(f"Tokenization complete with max_length = {MAX_LENGTH}.")

# --- 3. LOAD PRE-TRAINED MODEL ---
print(f"\nStep 3: Loading pre-trained {MODEL_NAME} model...")
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)
print("Model loaded successfully.")

# --- 4. DEFINE METRICS ---
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    
    return {
        'accuracy': accuracy_score(labels, predictions),
        'f1': f1_score(labels, predictions, average='binary'),
        'precision': precision_score(labels, predictions, average='binary'),
        'recall': recall_score(labels, predictions, average='binary')
    }

# --- 5. DEFINE TRAINING ARGUMENTS ---
print("\nStep 4: Defining optimized training arguments...")
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    # Further reduce epochs, relying on early stopping
    num_train_epochs=4, 
    per_device_train_batch_size=1,
    per_device_eval_batch_size=1,
    gradient_accumulation_steps=8,
    warmup_ratio=0.1,
    weight_decay=0.01,
    logging_strategy="epoch",
    eval_strategy="epoch",
    save_strategy="epoch",
    fp16=True, 
    load_best_model_at_end=True, 
    metric_for_best_model="f1",
    greater_is_better=True,
)

# --- 6. CREATE AND RUN THE TRAINER ---
print("\nStep 5: Creating and running the Trainer...")
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train_dataset,
    eval_dataset=tokenized_test_dataset,
    compute_metrics=compute_metrics,
    callbacks=[EarlyStoppingCallback(early_stopping_patience=2)] 
)

trainer.train()
print("Model fine-tuning complete.")

# --- 7. EVALUATE AND SAVE ---
print(f"\nStep 6: Saving the best model and tokenizer to '{OUTPUT_DIR}'...")
trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print("\n--- Step 7: Final Evaluation with Classification Report ---")
predictions_output = trainer.predict(tokenized_test_dataset)
y_true = predictions_output.label_ids
y_pred = np.argmax(predictions_output.predictions, axis=1)

report = classification_report(y_true, y_pred, target_names=["Reject (0)", "Select (1)"])
print(report)

print("\n--- Confusion Matrix ---")
print(confusion_matrix(y_true, y_pred))

print("--- Process Finished ---")

