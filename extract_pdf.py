import PyPDF2
import re

def extract_resume_content(pdf_path):
    
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

