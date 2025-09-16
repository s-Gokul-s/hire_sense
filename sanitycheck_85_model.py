import os
import sys

# Add the backend directory to the Python path to allow imports
# This assumes the script is run from the project's root directory
sys.path.append('./backend')

try:
    # We will use your PredictionService to load and run the model
    from app.services.prediction_service import PredictionService
except ImportError as e:
    print(f"Error: Could not import PredictionService. Details: {e}")
    print("Please ensure this script is run from the root 'hiresense' directory.")
    sys.exit(1)

# --- CONFIGURATION ---
# --- Point to the new, robust hybrid model ---
# This script assumes you have run 'train_hybrid_model.py' successfully
MODEL_TO_TEST = "./hiresense_hybrid_model"

print(f"--- Running Sanity Check on Final Hybrid Model: {MODEL_TO_TEST} ---")

# --- Test Case Definitions ---
# A robust, generalizable model should pass these real-world tests.

# Case 1: Obvious Good Fit (Real-world style)
jd_good_fit = "We are seeking a senior software engineer with strong Python and SQL skills. Experience with cloud platforms like AWS is required."
resume_good_fit = "Experienced Python developer with 8 years of experience. Proficient in SQL database management and certified in AWS solutions architecture."
expected_good_fit = "Fit" # The hybrid model should predict "Fit"

# Case 2: Obvious Bad Fit (Completely different domain)
jd_bad_fit = "We are looking for an experienced Digital Marketing Manager to lead our online strategy. Must have SEO and SEM experience."
resume_bad_fit = "Passionate Python and Java developer with experience building web applications and working with databases."
expected_bad_fit = "No Fit"


# --- Test Execution ---
tests = [
    ("Obvious Good Fit", jd_good_fit, resume_good_fit, expected_good_fit),
    ("Obvious Bad Fit", jd_bad_fit, resume_bad_fit, expected_bad_fit)
]

try:
    # Initialize the predictor with the specific model we want to test
    predictor = PredictionService(model_path=MODEL_TO_TEST)
except FileNotFoundError as e:
    print(f"\n❌ CRITICAL ERROR: Could not load the model.")
    print(f"   Details: {e}")
    print(f"   Please ensure you have run the 'train_hybrid_model.py' script and the model folder '{MODEL_TO_TEST}' exists.")
    sys.exit(1)


all_passed = True
for name, jd, resume, expected in tests:
    print(f"\nRunning Test: {name}...")
    result = predictor.predict(resume, jd)
    prediction = result.get("prediction")
    
    if prediction == expected:
        print(f"  ✅ PASS: Model correctly predicted '{prediction}'")
    else:
        print(f"  ❌ FAIL: Expected '{expected}', but model predicted '{prediction}'")
        all_passed = False

# --- Final Verdict ---
print("\n--- Sanity Check Complete ---")
if all_passed:
    print("✅🎉 All sanity checks passed! The model is behaving logically and is ready for final integration.")
else:
    print("❌ A problem was detected in the model's logic. This model should not be used.")