import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

print("--- Noise Analysis for Synthetic Resume Dataset ---")

# --- 1. Load the Dataset ---
print("Step 1: Loading local synthetic dataset...")
try:
    df = pd.read_csv("synthetic_resume_dataset.csv")
    df.dropna(inplace=True)
    # Map string labels to integers for analysis
    df['label'] = df['label'].map({"No Fit": 0, "Fit": 1})
    print(f"Dataset loaded: {len(df)} rows")
except FileNotFoundError:
    print("Error: 'synthetic_resume_dataset.csv' not found.")
    print("Please run the 'generate_dataset.py' script first.")
    exit()

# --- 2. Check for Duplicates with Conflicting Labels ---
print("\nStep 2: Checking for duplicates with conflicting labels...")
# Group by text pairs and count unique labels for each pair
label_counts = df.groupby(['resume_text', 'job_description_text'])['label'].nunique()
conflicting_duplicates = label_counts[label_counts > 1]
print(f"Found {len(conflicting_duplicates)} duplicate pairs with conflicting labels.")

# --- 3. Check Keyword Correlations (The Pattern) ---
print("\nStep 3: Checking keyword correlations...")

def check_correlation(job_keyword, resume_keyword, df):
    """Checks selection rate for a resume keyword within a specific job context."""
    # Find all JDs related to a specific role
    job_subset = df[df['job_description_text'].str.contains(job_keyword)]
    if len(job_subset) == 0:
        print(f"  - No jobs found with keyword '{job_keyword}'")
        return
        
    # Within that role, see if the resume keyword makes a difference
    contains_keyword = job_subset[job_subset['resume_text'].str.contains(resume_keyword)]
    does_not_contain_keyword = job_subset[~job_subset['resume_text'].str.contains(resume_keyword)]
    
    fit_rate_with_keyword = contains_keyword['label'].mean() if len(contains_keyword) > 0 else 0
    fit_rate_without_keyword = does_not_contain_keyword['label'].mean() if len(does_not_contain_keyword) > 0 else 0
    
    print(f"  - For JDs with '{job_keyword}':")
    print(f"    - Fit rate for resumes WITH '{resume_keyword}': {fit_rate_with_keyword:.2%}")
    print(f"    - Fit rate for resumes WITHOUT '{resume_keyword}': {fit_rate_without_keyword:.2%}")

# Check patterns for a few of the archetypes we created
check_correlation('django', 'python', df)
check_correlation('react', 'javascript', df)

# --- 4. PCA Visualization ---
print("\nStep 4: Generating embeddings for PCA visualization (using a fast model)...")
# Use a smaller, faster model for this diagnostic
sbert = SentenceTransformer("all-MiniLM-L6-v2")

# To speed things up, we'll analyze a random sample of 2000 data points
sample_df = df.sample(n=min(2000, len(df)), random_state=42)

# Create combined embeddings for the sample
embeddings = sbert.encode(
    (sample_df['resume_text'] + " [SEP] " + sample_df['job_description_text']).tolist(),
    show_progress_bar=True,
    convert_to_numpy=True
)

print("Reducing embedding dimensionality with PCA...")
pca = PCA(n_components=2)
embeddings_2d = pca.fit_transform(embeddings)

# Create a DataFrame for plotting
pca_df = pd.DataFrame(
    data=embeddings_2d,
    columns=('PC1', 'PC2')
)
pca_df['label'] = sample_df['label'].values

print("Generating plot...")
plt.figure(figsize=(10, 8))
sns.scatterplot(
    x="PC1", y="PC2",
    hue="label",
    palette=sns.color_palette("coolwarm", 2),
    data=pca_df,
    legend="full",
    alpha=0.6
)
plt.title("PCA of Synthetic Resume-JD Embeddings (0=No Fit, 1=Fit)")
plt.show()

print("\n--- Noise Analysis Complete ---")