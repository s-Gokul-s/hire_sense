import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os
from typing import List

# --- DEFINITIVE CONFIGURATION ---
MODEL_FOLDER_NAME = "hiresense_hybrid_model"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

try:
    SERVICE_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.abspath(os.path.join(SERVICE_FILE_DIR, "..", "..", ".."))
    MODEL_PATH = os.path.join(PROJECT_ROOT, MODEL_FOLDER_NAME)
except NameError:
    MODEL_PATH = f"../{MODEL_FOLDER_NAME}"

class PredictionService:
    def __init__(self, model_path: str = MODEL_PATH):
        self.model_path = model_path
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model directory '{MODEL_FOLDER_NAME}' not found at '{self.model_path}'.")
            
        print(f"Loading model from {self.model_path} onto {DEVICE}...")
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path).to(DEVICE)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        self.model.eval()
        print("Model loaded successfully.")

    def predict(self, resume_text: str, jd_text: str) -> dict:
        """Handles a single prediction."""
        # This function remains for single-use cases or testing.
        inputs = self.tokenizer(resume_text, jd_text, return_tensors="pt", padding="max_length", truncation=True, max_length=512).to(DEVICE)
        with torch.no_grad():
            logits = self.model(**inputs).logits
        probabilities = torch.softmax(logits, dim=1).cpu().numpy()[0]
        predicted_class_id = probabilities.argmax().item()
        label_map = {0: "No Fit", 1: "Fit"}
        return {
            "prediction": label_map[predicted_class_id],
            "fit_probability": f"{float(probabilities[1]):.2%}"
        }

    # --- NEW BATCH PREDICTION METHOD ---
    def predict_batch(self, resumes: List[str], jd_text: str) -> List[dict]:
        """
        Handles multiple resumes against a single JD in a highly efficient batch.
        """
        if not resumes:
            return []

        # Create pairs of (resume, jd) for the tokenizer
        jd_list = [jd_text] * len(resumes)
        
        # Tokenize the entire batch at once
        inputs = self.tokenizer(resumes, jd_list, return_tensors="pt", padding=True, truncation=True, max_length=512).to(DEVICE)
        
        # Run inference on the entire batch in a single pass
        with torch.no_grad():
            logits = self.model(**inputs).logits
        
        # Get probabilities for the whole batch
        probabilities_batch = torch.softmax(logits, dim=1).cpu().numpy()
        
        # Process the results for each item in the batch
        results = []
        label_map = {0: "No Fit", 1: "Fit"}
        for probabilities in probabilities_batch:
            predicted_class_id = probabilities.argmax().item()
            results.append({
                "prediction": label_map[predicted_class_id],
                "fit_probability": float(probabilities[1]) # Return as float for sorting
            })
            
        return results

print("Initializing Prediction Service...")
prediction_service = PredictionService()
print("Prediction Service is ready.")

