import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os
from typing import List

# Import updated skill matching
from app.services.insights_service import get_skill_matches, extract_skills, clean_text

# --- DEFINITIVE CONFIGURATION ---
MODEL_FOLDER_NAME = "hiresense_hybrid_model"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

try:
    SERVICE_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.abspath(os.path.join(SERVICE_FILE_DIR, "..", "..", ".."))
    MODEL_PATH = os.path.join(PROJECT_ROOT, MODEL_FOLDER_NAME)
except NameError:
    MODEL_PATH = f"../{MODEL_FOLDER_NAME}"

# --- Weights for hybrid score ---
W_ML = 0.7
W_SKILLS = 0.3

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

    def compute_hybrid_score(self, resume_text: str, jd_text: str, ml_prob: float) -> float:
        """Compute hybrid Fit Score using ML probability + skill match %."""
        skill_data = get_skill_matches(jd_text, resume_text)
        jd_skills = skill_data["jd_skills"]
        matched_skills = skill_data["matched_skills"]
        if jd_skills:
            skill_match_pct = len(matched_skills) / len(jd_skills)
        else:
            skill_match_pct = 1.0  # avoid division by zero
        hybrid_score = W_ML * ml_prob + W_SKILLS * skill_match_pct
        return hybrid_score

    def predict(self, resume_text: str, jd_text: str) -> dict:
        """Handles a single prediction with hybrid Fit Score."""
        inputs = self.tokenizer(
            resume_text, jd_text, 
            return_tensors="pt", padding="max_length", truncation=True, max_length=512
        ).to(DEVICE)
        
        with torch.no_grad():
            logits = self.model(**inputs).logits
        
        probabilities = torch.softmax(logits, dim=1).cpu().numpy()[0]
        ml_prob = float(probabilities[1])
        predicted_class_id = probabilities.argmax().item()
        label_map = {0: "No Fit", 1: "Fit"}

        # Compute hybrid score
        hybrid_score = self.compute_hybrid_score(resume_text, jd_text, ml_prob)

        return {
            "prediction": label_map[predicted_class_id],
            "fit_probability": f"{ml_prob:.2%}",
            "hybrid_fit_score": f"{hybrid_score:.2%}"
        }

    def predict_batch(self, resumes: List[str], jd_text: str) -> List[dict]:
        """Batch prediction with hybrid Fit Score."""
        if not resumes:
            return []

        jd_list = [jd_text] * len(resumes)
        inputs = self.tokenizer(
            resumes, jd_list, 
            return_tensors="pt", padding=True, truncation=True, max_length=512
        ).to(DEVICE)
        
        with torch.no_grad():
            logits = self.model(**inputs).logits
        
        probabilities_batch = torch.softmax(logits, dim=1).cpu().numpy()
        results = []
        label_map = {0: "No Fit", 1: "Fit"}

        for idx, probabilities in enumerate(probabilities_batch):
            ml_prob = float(probabilities[1])
            predicted_class_id = probabilities.argmax().item()
            resume_text = resumes[idx]
            hybrid_score = self.compute_hybrid_score(resume_text, jd_text, ml_prob)

            results.append({
                "prediction": label_map[predicted_class_id],
                "fit_probability": ml_prob,
                "hybrid_fit_score": hybrid_score
            })
            
        return results

print("Initializing Prediction Service...")
prediction_service = PredictionService()
print("Prediction Service is ready.")
