import PyPDF2
import re

def extract_resume_content(pdf_path):
    """Extract content from the resume PDF"""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    
    # Clean up the text by removing extra whitespaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

if __name__ == "__main__":
    pdf_path = r"c:\Users\rajpr\OneDrive\Desktop\All projects\Agent\res (1).pdf"
    content = extract_resume_content(pdf_path)
    print("Full extracted content from PDF:")
    print(content)  # Print full content to see everything