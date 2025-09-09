import pandas as pd
import random

print("--- Starting Synthetic Dataset Generation ---")

# Define the building blocks for our dataset
ROLES = {
    "Python Developer": {
        "skills": ["python", "django", "flask", "sql", "apis", "git"],
        "resume_templates": [
            "Experienced Python Developer with a strong background in {skills} seeking a challenging role.",
            "Software engineer specializing in backend development with Python. Proficient in {skills}.",
            "Detail-oriented developer with expertise in creating web applications using {skills}."
        ],
        "jd_templates": [
            "We are hiring a Python Developer to join our team. Must have experience with {skills}.",
            "Seeking a skilled Software Engineer for a backend role. Requirements include {skills}.",
            "Job opening for a Python programmer. The ideal candidate will know {skills}."
        ]
    },
    "Frontend Developer": {
        "skills": ["javascript", "react", "vue", "css", "html", "typescript"],
        "resume_templates": [
            "Creative Frontend Developer skilled in building responsive user interfaces with {skills}.",
            "UI specialist with a passion for modern web technologies, including {skills}.",
            "Frontend engineer focused on performance and user experience. Expertise in {skills}."
        ],
        "jd_templates": [
            "Looking for a Frontend Developer proficient in {skills} to build our next-gen UI.",
            "Join our UI team! We are looking for a developer with experience in {skills}.",
            "Urgent hiring for a React Developer. Must have a strong command of {skills}."
        ]
    },
    "Data Scientist": {
        "skills": ["python", "pandas", "scikit-learn", "tensorflow", "sql", "statistics"],
        "resume_templates": [
            "Data Scientist with a proven track record of building predictive models using {skills}.",
            "Analytical professional with expertise in machine learning and data analysis. Skilled in {skills}.",
            "Machine learning engineer with a focus on delivering data-driven insights using {skills}."
        ],
        "jd_templates": [
            "Hiring a Data Scientist to analyze large datasets. Required skills include {skills}.",
            "We are looking for a Machine Learning expert to join our data team. Must know {skills}.",
            "Data Scientist role available. The candidate must be proficient in {skills}."
        ]
    },
    "Cloud Engineer": {
        "skills": ["aws", "docker", "kubernetes", "terraform", "ci/cd", "linux"],
        "resume_templates": [
            "Certified Cloud Engineer with extensive experience in deploying and managing infrastructure using {skills}.",
            "DevOps professional specializing in cloud automation and containerization with {skills}.",
            "Cloud infrastructure expert with skills in {skills}."
        ],
        "jd_templates": [
            "Seeking a Cloud Engineer to manage our AWS infrastructure. Experience with {skills} is mandatory.",
            "DevOps Engineer needed. Must have hands-on experience with {skills}.",
            "Join our cloud team! We require knowledge of {skills}."
        ]
    }
}

SOFT_SKILLS = ["communication", "teamwork", "problem-solving", "leadership", "agile methodologies"]

def generate_text(template, skills):
    """Generates a text by filling a template with a sample of skills."""
    num_skills = random.randint(3, len(skills))
    num_soft_skills = random.randint(1, 3)
    
    selected_skills = random.sample(skills, num_skills)
    selected_soft_skills = random.sample(SOFT_SKILLS, num_soft_skills)
    
    all_skills = selected_skills + selected_soft_skills
    random.shuffle(all_skills)
    
    return template.format(skills=", ".join(all_skills))

# --- Main Generation Loop ---
dataset_rows = []
role_names = list(ROLES.keys())

for i in range(5000):
    # Decide if this will be a "Fit" or "No Fit"
    is_fit = random.choice([0, 1])
    
    # Pick the target role for the job description
    target_role_name = random.choice(role_names)
    target_role = ROLES[target_role_name]
    
    # Generate the job description based on the target role
    jd_template = random.choice(target_role["jd_templates"])
    job_description_text = generate_text(jd_template, target_role["skills"])

    if is_fit:
        # For a "Fit", the resume has the same skills as the JD
        resume_role = target_role
        label = "Fit"
    else:
        # For a "No Fit", the resume has skills from a different role
        mismatch_role_name = random.choice([r for r in role_names if r != target_role_name])
        resume_role = ROLES[mismatch_role_name]
        label = "No Fit"
        
    # Generate the resume text
    resume_template = random.choice(resume_role["resume_templates"])
    resume_text = generate_text(resume_template, resume_role["skills"])

    dataset_rows.append({
        "resume_text": resume_text,
        "job_description_text": job_description_text,
        "label": label
    })

# Convert to DataFrame and save
df = pd.DataFrame(dataset_rows)
# Shuffle the dataset to mix everything up
df = df.sample(frac=1).reset_index(drop=True)

output_filename = "synthetic_resume_dataset.csv"
df.to_csv(output_filename, index=False)

print(f"\nSuccessfully generated {len(df)} rows.")
print(f"Dataset saved to '{output_filename}'.")
print("\nLabel distribution in the new dataset:")
print(df['label'].value_counts())
print("\n--- Process Finished ---")