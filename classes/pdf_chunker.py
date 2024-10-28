#coding: utf-8
import os
import json
from sentence_transformers import SentenceTransformer, models
from datetime import datetime
from classes.reader import Reader
from classes.elastic_indexer import ElasticIndexer

class PDFChunker:

    def __init__(self, path="pdfs/", config_file="pdfs/cache/indexed.json", indexer=None):
        """
        Init chunker for PDFs. 
        Init vectorization model and configure Elasticsearch indexer.
        """
        self.path = path
        self.config_file = config_file
        self.indexed_files = self.load_indexed_files()

        word_embedding_model = models.Transformer("models/e5-multilingual")
        pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension())
        self.model = SentenceTransformer(modules=[word_embedding_model, pooling_model])

        self.reader = Reader(path)

        self.indexer = indexer if indexer else ElasticIndexer()

    def load_indexed_files(self):
        """
        Load indexed file from JSON file.
        """
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {}

    def save_indexed_files(self):
        """
        Save list of already saved PDFs.
        """
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.indexed_files, f, ensure_ascii=False, indent=4)

    def chunk_text(self, text, chunk_size=512):
        """
        Chunk data.
        """
        paragraphs = text.split('\n')  
        chunks = []
        current_chunk = []
        current_length = 0

        for paragraph in paragraphs:
            words = paragraph.split()
            
            if current_length + len(paragraph) + 1 <= chunk_size:
                current_chunk.append(paragraph)
                current_length += len(paragraph) + 1
            else:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                current_chunk = [paragraph]  
                current_length = len(paragraph) + 1

            while len(current_chunk) > 0 and current_length > chunk_size:
                chunk_part = current_chunk[:chunk_size]  
                chunks.append(" ".join(chunk_part))
                current_chunk = current_chunk[chunk_size:]  

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks


    def process_pdf(self, file_name):
        """
        PDF treatement : extract text, chunk it, and vectorize it.
        """
        text = self.reader.extract_text(file_name)
        if not text:
            print(f"File {file_name} don't have any content.")
            return []

        chunks = self.chunk_text(text)

        title = os.path.splitext(file_name)[0] 
        file_path = os.path.join(self.path, file_name)
        timestamp = datetime.now().isoformat() 

        processed_chunks = []
        for i, chunk in enumerate(chunks):
            chunk_data = {
                "chunk": chunk,
                "metadata": {
                    "title": title,
                    "path": file_path,
                    "file_name": file_name,
                    "chunk_id": i + 1,  
                    "timestamp": timestamp
                }
            }
            processed_chunks.append(chunk_data)

        return processed_chunks

    def vectorize_chunks(self, chunks):
        """
        Vectorize chunks using sentence-transformers.
        """
        chunk_texts = [chunk['chunk'] for chunk in chunks]
        vectors = self.model.encode(chunk_texts)

        for i, chunk in enumerate(chunks):
            chunk['vector'] = vectors[i]

        return chunks

    def process_all_pdfs(self):
        """
        Treat all PDFs except already listed ones.
        """
        all_chunks = []
        for file_name in os.listdir(self.path):
            if file_name.endswith(".pdf"):
                if file_name in self.indexed_files:
                    print(f"File {file_name} already indexed.")
                    continue
                
                print(f"Treating {file_name}...")
                chunks = self.process_pdf(file_name)
                if chunks:
                    vectorized_chunks = self.vectorize_chunks(chunks)
                    all_chunks.extend(vectorized_chunks)

                    self.indexer.index_chunks(vectorized_chunks)

                    self.indexed_files[file_name] = {
                        "path": os.path.join(self.path, file_name),
                        "indexed_at": datetime.now().isoformat()
                    }
                    self.save_indexed_files()  

        return all_chunks
