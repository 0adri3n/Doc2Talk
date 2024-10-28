#coding: utf-8
import os
import json
from sentence_transformers import SentenceTransformer, models
from datetime import datetime
from classes.reader import Reader  # Importation de ta classe Reader pour extraire le texte
from classes.elastic_indexer import ElasticIndexer  # Importer la nouvelle classe ElasticIndexer

class PDFChunker:

    def __init__(self, path="pdfs/", config_file="pdfs/cache/indexed.json", indexer=None):
        """
        Initialisation du chunker pour les PDF. Utilise le chemin des PDF, 
        initialise le modèle de vectorisation et configure l'indexeur Elasticsearch.
        """
        self.path = path
        self.config_file = config_file
        self.indexed_files = self.load_indexed_files()

        # Initialiser le modèle de sentence-transformers
        word_embedding_model = models.Transformer("models/e5-multilingual")
        pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension())
        self.model = SentenceTransformer(modules=[word_embedding_model, pooling_model])

        # Initialiser le lecteur PDF
        self.reader = Reader(path)

        # Initialiser l'indexeur Elasticsearch
        self.indexer = indexer if indexer else ElasticIndexer()

    def load_indexed_files(self):
        """
        Charge la liste des fichiers PDF déjà indexés depuis le fichier de configuration JSON.
        Si le fichier n'existe pas, il retourne un dictionnaire vide.
        """
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {}

    def save_indexed_files(self):
        """
        Sauvegarde la liste des fichiers PDF déjà indexés dans le fichier de configuration JSON.
        """
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.indexed_files, f, ensure_ascii=False, indent=4)

    def chunk_text(self, text, chunk_size=512):
        """
        Découpe le texte en chunks en tenant compte des fins de paragraphes.
        """
        paragraphs = text.split('\n')  # Diviser le texte par paragraphes
        chunks = []
        current_chunk = []
        current_length = 0

        for paragraph in paragraphs:
            words = paragraph.split()
            
            # Vérifier si ajouter ce paragraphe dépasserait la limite du chunk
            if current_length + len(paragraph) + 1 <= chunk_size:
                # Si le chunk reste dans la limite, ajouter le paragraphe complet
                current_chunk.append(paragraph)
                current_length += len(paragraph) + 1
            else:
                # Si le chunk dépasse, sauvegarder le chunk actuel et démarrer un nouveau
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                current_chunk = [paragraph]  # Nouveau chunk avec le paragraphe actuel
                current_length = len(paragraph) + 1

            # Si le paragraphe est trop grand, on le découpe en morceaux
            while len(current_chunk) > 0 and current_length > chunk_size:
                chunk_part = current_chunk[:chunk_size]  # Prendre un morceau
                chunks.append(" ".join(chunk_part))
                current_chunk = current_chunk[chunk_size:]  # Réduire le chunk

        # Ajouter le dernier chunk si du texte reste
        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks


    def process_pdf(self, file_name):
        """
        Traite un fichier PDF : extrait le texte, le découpe en chunks, et vectorise chaque chunk.
        """
        # Extraire le texte à partir du fichier PDF
        text = self.reader.extract_text(file_name)
        if not text:
            print(f"Le fichier {file_name} ne contient pas de texte.")
            return []

        # Découper le texte en chunks
        chunks = self.chunk_text(text)

        # Métadonnées du document
        title = os.path.splitext(file_name)[0]  # Utiliser le nom de fichier comme titre
        file_path = os.path.join(self.path, file_name)
        timestamp = datetime.now().isoformat()  # Obtenir le timestamp actuel

        processed_chunks = []
        for i, chunk in enumerate(chunks):
            chunk_data = {
                "chunk": chunk,
                "metadata": {
                    "title": title,
                    "path": file_path,
                    "file_name": file_name,
                    "chunk_id": i + 1,  # Numéro du chunk
                    "timestamp": timestamp
                }
            }
            processed_chunks.append(chunk_data)

        return processed_chunks

    def vectorize_chunks(self, chunks):
        """
        Vectorise une liste de chunks en utilisant le modèle de sentence-transformers.
        """
        chunk_texts = [chunk['chunk'] for chunk in chunks]
        vectors = self.model.encode(chunk_texts)

        # Associer les vecteurs aux chunks originaux
        for i, chunk in enumerate(chunks):
            chunk['vector'] = vectors[i]

        return chunks

    def process_all_pdfs(self):
        """
        Traite tous les PDF dans le répertoire spécifié, sauf ceux déjà indexés.
        """
        all_chunks = []
        for file_name in os.listdir(self.path):
            if file_name.endswith(".pdf"):
                # Vérifier si le fichier a déjà été indexé
                if file_name in self.indexed_files:
                    print(f"Le fichier {file_name} a déjà été indexé. Passer.")
                    continue
                
                print(f"Traitement du fichier {file_name}...")
                chunks = self.process_pdf(file_name)
                if chunks:
                    # Vectoriser les chunks extraits
                    vectorized_chunks = self.vectorize_chunks(chunks)
                    all_chunks.extend(vectorized_chunks)

                    # Indexer dans Elasticsearch via ElasticIndexer
                    self.indexer.index_chunks(vectorized_chunks)

                    # Ajouter le fichier à la liste des fichiers indexés et sauvegarder
                    self.indexed_files[file_name] = {
                        "path": os.path.join(self.path, file_name),
                        "indexed_at": datetime.now().isoformat()
                    }
                    self.save_indexed_files()  # Sauvegarder l'état du fichier JSON

        return all_chunks
