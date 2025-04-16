AI Resume Matcher

This project is an AI-powered Resume Matcher that compares resumes with job descriptions using semantic similarity and keyword matching. Built with Streamlit, SpaCy, and SentenceTransformers.

Features

- Match single or multiple resumes against a job description.
- Semantic analysis using sentence embeddings.
- Keyword comparison with match score breakdown.
- Visualizations: pie & bar charts.
- Downloadable PDF report per resume.

Tech Stack

- Python
- Streamlit
- SpaCy
- Sentence Transformers
- Plotly
- PDF & DOCX parsing (`PyMuPDF`, `python-docx`)

File Structure

├── app.py 
├── requirements.txt 
├── README.md 
└── utils 
   ├── matcher.py 
   └── parser.py

How to Run

1. Install dependencies:

pip install -r requirements.txt


2. Launch the app:

streamlit run app.py


3. Upload a job description and one or more resumes.

Input Types

- Job Description: Text, PDF, or DOCX
- Resumes: PDF or DOCX (Single or Multiple)

Output

- Match Score
- Semantic vs Keyword Contribution
- Matched Keywords
- PDF Report per Resume

---

Created as part of a Data Science Internship project. 
