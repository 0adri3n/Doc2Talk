#coding: utf-8
import PyPDF2
import re

class Reader:

    def __init__(self, path="pdfs/"):

        self.path = path

    def extract_text(self, file_name):
        """
        Extract text from PDF.
        Use PyPDF2 to extract, clean and structure data.
        """
        full_text = ""

        with open(self.path + file_name, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                # Extraire le texte d'une page
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n\n" 

        cleaned_text = self.clean_text(full_text)

        return cleaned_text

    def clean_text(self, text):

        # Removing multiple spaces and white spaces
        text = re.sub(r'\n\s*\n+', '\n\n', text)  

        # Removing HTML
        cleaner = re.compile('<.*?>') 
        text = re.sub(cleaner, '', text)
        text = text.replace('<em>', '')
        text = text.replace('</em>', '')

        text = self.remove_headers_footers(text)

        return text

    def remove_headers_footers(self, text):

        lines = text.split('\n')
        cleaned_lines = []
        previous_line = None

        for line in lines:
            if previous_line and line == previous_line:
                continue
            if len(line.strip()) < 5:
                continue

            if re.match(r'^\d+$', line.strip()):
                continue

            cleaned_lines.append(line)
            previous_line = line

        return "\n".join(cleaned_lines)

    def remove_non_ascii(self, text):

        return ''.join([i if ord(i) < 128 else ' ' for i in text])
