#coding: utf-8
import PyPDF2
import re

class Reader:

    def __init__(self, path="pdfs/"):
        """
        Initialisation du lecteur de PDF avec un chemin par défaut.
        """
        self.path = path

    def extract_text(self, file_name):
        """
        Extraction du texte à partir d'un fichier PDF.
        Utilise PyPDF2 pour extraire le texte brut, puis nettoie et structure le texte en paragraphes.
        """
        full_text = ""

        # Ouvrir le fichier PDF et lire le contenu
        with open(self.path + file_name, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                # Extraire le texte d'une page
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n\n"  # Ajouter un double saut de ligne entre les pages

        # Nettoyer le texte extrait
        cleaned_text = self.clean_text(full_text)

        return cleaned_text

    def clean_text(self, text):
        """
        Nettoie le texte extrait pour éliminer les artefacts et les espaces superflus.
        Cette méthode traite également les problèmes fréquents dans les PDF tels que les sauts de ligne et
        la correction des apostrophes mal interprétées.
        """
        # Normaliser le texte en Unicode NFC pour gérer correctement les accents et caractères spéciaux
        # text = unicodedata.normalize('NFC', text)

        # Suppression des espaces multiples et des lignes blanches excessives
        text = re.sub(r'\n\s*\n+', '\n\n', text)  # Laisser deux sauts de ligne entre les paragraphes

        # Suppression des artefacts non désirés (caractères non-ASCII)
        #text = re.sub(r'[^\x00-\x7F]+', '', text)

        # Supprimer les balises HTML
        cleaner = re.compile('<.*?>') 
        text = re.sub(cleaner, '', text)
        text = text.replace('<em>', '')
        text = text.replace('</em>', '')


        # Supprimer les en-têtes et pieds de page courants dans les documents PDF
        text = self.remove_headers_footers(text)

        return text

    def remove_headers_footers(self, text):
        """
        Supprime les en-têtes et pieds de page répétitifs dans les PDF.
        Cette méthode utilise des heuristiques pour identifier les répétitions fréquentes et les supprimer.
        """
        lines = text.split('\n')
        cleaned_lines = []
        previous_line = None

        for line in lines:
            # Supprimer les lignes très courtes qui sont souvent des artefacts d'en-têtes ou pieds de page
            if previous_line and line == previous_line:
                continue
            if len(line.strip()) < 5:
                continue

            # Suppression des numéros de page
            if re.match(r'^\d+$', line.strip()):
                continue

            cleaned_lines.append(line)
            previous_line = line

        return "\n".join(cleaned_lines)

    def remove_non_ascii(self, text):
        """
        Supprime les caractères non-ASCII du texte pour garantir une bonne indexation dans Elasticsearch.
        """
        # Remplacer les caractères non-ASCII par des espaces ou les supprimer
        return ''.join([i if ord(i) < 128 else ' ' for i in text])
