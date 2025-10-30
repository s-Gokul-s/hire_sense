# 🤖 Hiresense – AI Resume Shortlister

**Hiresense** is an AI-driven Resume Shortlisting System that fine-tunes a **pretrained RoBERTa model** on a custom dataset of resumes and job descriptions to predict candidate–job fit scores.  
It helps recruiters and HR professionals automate the resume screening process with **deep contextual language understanding**, improving accuracy, speed, and fairness.

---
## 🚀 Features
- Upload resumes in PDF, DOCX, or text format and enter job descriptions as text or PDF
- Automatic text extraction and preprocessing
- Fine-tuned RoBERTa model predicts candidate–job fit scores
- Displays ranked candidate results with clear visual scoring
- View individual resumes with matched and missed skill insights
- Download resumes, ranked results (CSV), or all resumes (ZIP)
- Built with a full-stack architecture (FastAPI + React + Tailwind CSS)
- Modular design for easy model or UI updates
  
---

## 🧠 Tech Stack

**Frontend:** React, Tailwind CSS  
**Backend:** FastAPI, Python  
**ML / NLP:** RoBERTa, scikit-learn, pandas, sentence-transformers, nltk, spaCy  
**Other Tools:** uvicorn, python-multipart, PyMuPDF, NumPy

---

## 📁 Project Structure

```
hiresense/
├── .vscode/                 # VS Code configuration files
├── backend/                 # Python application
│   ├── .vscode/
│   ├── app/
│   ├── .gitignore
│   └── run.py               # Entry point for the backend server
├── frontend/                # Vite/React application
│   ├── public/
│   ├── src/
│   ├── .gitignore
│   ├── README.md
│   ├── eslint.config.js
│   ├── index.html
│   ├── package-lock.json
│   ├── package.json
│   └── vite.config.js
├── check/                 
├── .gitignore               # Root Git ignore rules
├── README.md                # Project documentation (this file)
├── hybrid_model.py          # Script for the integrated model
└── requirements.txt         # Python dependencies for the project
```

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/s-Gokul-s/hire_sense.git
cd hire_sense
```

### 2️⃣ Backend Setup (FastAPI)
```bash
cd backend
pip install -r requirements.txt
python run.py
```
The backend server will start (default: `http://127.0.0.1:8000`)

### 3️⃣ Frontend Setup (React)
```bash
cd ../frontend
npm install
npm start
```
The frontend will start on `http://localhost:5173`

---

## 🚀 Usage

1. Open the app at **http://localhost:5173**
2. Enter or upload a **Job Description (PDF or text)**.
3. Upload one or more **Resume files (PDF, DOCX, or TXT)**.
4. Click **“Get Result”**.
5. The system will:
   - Extract and preprocess text.
   - Predict candidate–job fit scores using **RoBERTa**.
   - Display ranked results with fit percentages.
   - Allow viewing each resume with **matched and missed skills** highlighted.
6. You can **download results** as CSV or all resumes as a ZIP file.

---

## 🧠 Model Details

The trained **RoBERTa model** used for similarity and fit scoring is **not included** in this repository due to size limits.

However, a **model training script** is provided:
```bash
python hybrid_model.py
```

---

## 🧪 Future Enhancements

- Deploy as a browser plugin for recruiters  
- Add cloud storage support for resumes  
- Introduce explainable AI metrics (e.g., SHAP values)  
- Integrate with LinkedIn API for candidate import  

---

📚 Acknowledgments

This project makes use of the open-source Skill Extraction model
👉 [amjad-awad/skill-extractor](https://huggingface.co/amjad-awad/skill-extractor)

developed by Amjad Awad and hosted on Hugging Face.

It is used to identify and extarct relevant skills from resumes and job descriptions.This mode is utilized solely for academic and research purposes,with full credit to the orginal author.

---

## 🌐 Live Demo

🔗 Coming Soon! (Deployment in progress…)

---

## 👤 Author

**S Gokul**    
💼 [LinkedIn](https://www.linkedin.com/in/s-gokul-s)  
📧 gokul228396@gmail.com  

---





