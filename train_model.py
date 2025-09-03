import sys
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.decomposition import PCA  # <-- 1. IMPORT PCA
import joblib
from datasets import load_dataset
from tqdm import tqdm

# Add the 'backend' folder to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.embedding_service import generate_embedding
from app.services.scoring_service import calculate_similarity

print("--- Starting Model Training ---")

# 1. Load and Prepare Dataset
print("Step 1: Loading and preparing dataset from Hugging Face...")
try:
    dataset = load_dataset("AzharAli05/Resume-Screening-Dataset")
    df = pd.DataFrame(dataset["train"])
    df['label'] = df['Decision'].apply(lambda d: 1 if d == 'select' else 0)
    df = df[['Resume', 'Job_Description', 'label']]
    print("Dataset prepared successfully.")
except Exception as e:
    print(f"Failed to load dataset. Error: {e}")
    sys.exit(1)

# 2. Feature Engineering (Initial Generation)
print("\nStep 2: Generating initial features from text...")
initial_features = []
labels = []

for index, row in tqdm(df.iterrows(), total=df.shape[0]):
    try:
        jd_text = str(row['Job_Description'])
        resume_text = str(row['Resume'])
        
        jd_embedding = generate_embedding(jd_text)
        resume_embedding = generate_embedding(resume_text)
        
        cosine_score = calculate_similarity(jd_embedding, resume_embedding)
        vector_diff = np.array(jd_embedding) - np.array(resume_embedding)
        
        # We separate the score and the vector to process the vector with PCA
        initial_features.append({'score': cosine_score, 'diff': vector_diff})
        labels.append(row['label'])
    except Exception as e:
        print(f"\nSkipping row {index} due to error: {e}")

print("Initial feature generation complete.")

# --- 2.5 NEW STEP: Apply PCA for Dimensionality Reduction ---
print("\nStep 2.5: Applying PCA to reduce feature dimensions...")

# Separate the scores and the high-dimensional vectors
cosine_scores = np.array([f['score'] for f in initial_features]).reshape(-1, 1)
vector_diffs = np.array([f['diff'] for f in initial_features])

# Initialize PCA to reduce the 384 dimensions down to 50
n_components = 50
pca = PCA(n_components=n_components, random_state=42)

# Fit PCA on the vectors and transform them
vector_diffs_pca = pca.fit_transform(vector_diffs)

# Combine the cosine score with the new, lower-dimensional PCA features
features = np.hstack([cosine_scores, vector_diffs_pca])
print(f"Feature engineering complete. Final feature shape: {features.shape}")


# 3. Train the Model
print("\nStep 3: Training Random Forest model...")
X_train, X_test, y_train, y_test = train_test_split(
    features, labels, test_size=0.2, random_state=42, stratify=labels
)

model = RandomForestClassifier(random_state=42, n_jobs=-1)
model.fit(X_train, y_train)
print("Model training complete.")

# 4. Evaluate the Model
print("\nStep 4: Evaluating model performance...")
y_pred = model.predict(X_test)
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=['Reject (0)', 'Select (1)']))

# 5. Save the Model AND the PCA transformer
print("\nStep 5: Saving trained model and PCA transformer...")
joblib.dump(model, 'trained_model.pkl') # <-- 3. UPDATED FILENAME
joblib.dump(pca, 'pca_transformer.pkl') # <-- 4. SAVE THE PCA TRANSFORMER
print("Model and PCA transformer saved successfully.")
print("--- Process Finished ---")