import re
import spacy
from sentence_transformers import SentenceTransformer, util
from nltk.corpus import stopwords
import nltk

# Ensure stopwords are downloaded
try:
    from nltk.corpus import stopwords
    stop_words = set(stopwords.words('english'))
except LookupError:
    nltk.download('stopwords')
    from nltk.corpus import stopwords
    stop_words = set(stopwords.words('english'))

def preprocess(text):
    text = text.lower()
    text = re.sub(r'\bapis\b', 'api', text)  # normalize plurals
    text = re.sub(r'\bml\b', 'machine learning', text)  # short forms
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

model = SentenceTransformer("all-mpnet-base-v2")
nlp = spacy.load("en_core_web_sm")

GENERIC_IGNORE = {
    "bachelor", "degree", "years", "experience", "strong", "understanding",
    "real", "world", "solutions", "functional", "cross", "based", "field",
    "year", "solution", "team", "collaborate", "build", "develop"
}

# Boost score by matching key skills
def keyword_boost(text1, text2, boost_keywords):
    score = 0
    common_keywords = []
    for kw in boost_keywords:
        if kw in text1 and kw in text2:
            score += 1
            common_keywords.append(kw)
    return score / len(boost_keywords), common_keywords

stop_words = set(stopwords.words('english'))

def extract_keywords(text):
    # Simple keyword extractor: remove stopwords, punctuation, numbers
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())  # words with 3+ letters
    keywords = set([word for word in words if word not in stop_words])
    return keywords

def match_resume_to_jd(resume_text, job_description):
    important_keywords = [
        "python", "flask", "fastapi", "tensorflow",
        "spacy", "textacy", "fastembed", "nlp"
    ]

    resume_text_clean = preprocess(resume_text)
    jd_text_clean = preprocess(job_description)

    # Semantic similarity
    resume_embedding = model.encode(resume_text_clean, convert_to_tensor=True)
    jd_embedding = model.encode(jd_text_clean, convert_to_tensor=True)
    semantic_score = util.cos_sim(resume_embedding, jd_embedding).item()

    # Keyword Boost (based on your fixed list)
    keyword_score, common_keywords = keyword_boost(resume_text_clean, jd_text_clean, important_keywords)

    # Extract keyword sets for diff table
    jd_keywords = extract_keywords(job_description)
    resume_keywords = extract_keywords(resume_text)

    # Final Score
    final_score = round((semantic_score * 0.8 + keyword_score * 0.2) * 100, 2)

    return final_score, common_keywords, semantic_score, keyword_score, jd_keywords, resume_keywords
