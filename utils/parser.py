import fitz  # PyMuPDF
import docx

def extract_text_from_pdf(file):
    text = ""
    # file is a BytesIO stream; pass it directly to fitz.open()
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_text_from_docx(file):
    doc = docx.Document(file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

def extract_text(file):
    filename = file.name
    if filename.endswith('.pdf'):
        return extract_text_from_pdf(file)
    elif filename.endswith('.docx'):
        return extract_text_from_docx(file)
    else:
        return "Unsupported file type. Please upload PDF or DOCX."