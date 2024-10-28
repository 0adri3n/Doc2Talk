from sentence_transformers import SentenceTransformer, models
from elasticsearch import Elasticsearch
import json

class UserQuery:
    
    def __init__(self, index_name="pdf_chunks"):
        """
        Initialisation de la classe pour gérer les requêtes utilisateurs.
        """
        self.ip = "127.0.0.1"
        self.port = "9200"
        self.url = "http://" + self.ip + ":" + self.port
        self.username = "elastic"
        with open("config.json", "r") as fichier:
            config = json.load(fichier)
            self.password = config.get("password")

        # Initialiser Elasticsearch
        self.es = Elasticsearch(self.url, basic_auth=(self.username, self.password))
        self.index_name = index_name

        # Charger le même modèle que pour les PDFs
        word_embedding_model = models.Transformer("models/e5-multilingual")
        pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension())
        self.model = SentenceTransformer(modules=[word_embedding_model, pooling_model])

    def vectorize_question(self, question):
        """
        Vectorise la question de l'utilisateur.
        """
        question_vector = self.model.encode(question)
        return question_vector

    def standard_search(self, query_text):
        """
        Effectue une recherche standard (textuelle) sur Elasticsearch, 
        basée sur les métadonnées textuelles.
        """
        query = {
            "query": {
                "multi_match": {
                    "query": query_text,
                    "fields": ["metadata.title^2", "metadata.path", "metadata.file_name"]
                }
            }
        }
        response = self.es.search(index=self.index_name, body=query)
        return response

    def knn_search(self, query_vector, k=10):
        """
        Effectue une recherche KNN (basée sur la similarité de vecteurs).
        """
        query = {
            "knn": {
                "field": "vector",
                "query_vector": query_vector,
                "k": k,
                "num_candidates": 100
            }
        }
        response = self.es.search(index=self.index_name, body=query)
        return response

    def rrf_search(self, query_text, query_vector, k=10):
        """
        Combine plusieurs résultats avec RRF (Reciprocal Rank Fusion) entre une recherche textuelle et KNN.
        """
        text_search = self.standard_search(query_text)
        knn_search = self.knn_search(query_vector, k)

        # Extraction des IDs et scorings des résultats des deux requêtes
        text_results = {hit['_id']: hit['_score'] for hit in text_search['hits']['hits']}
        knn_results = {hit['_id']: hit['_score'] for hit in knn_search['hits']['hits']}

        # Fusion RRF
        rrf_results = {}
        for doc_id in set(text_results.keys()).union(knn_results.keys()):
            text_rank = 1 / (50 + text_results.get(doc_id, 0))  # Pénalité RRF pour recherche textuelle
            knn_rank = 1 / (50 + knn_results.get(doc_id, 0))    # Pénalité RRF pour KNN
            rrf_results[doc_id] = text_rank + knn_rank

        # Tri par score RRF
        sorted_rrf_results = sorted(rrf_results.items(), key=lambda item: item[1], reverse=True)
        return sorted_rrf_results

    def boosted_search(self, query_text, query_vector, k=10):
        """
        Recherche avec boosting, où certains champs sont boostés, et combinaison avec KNN.
        """
        query = {
            "query": {
                "bool": {
                    "should": [
                        {"multi_match": {
                            "query": query_text,
                            "fields": ["metadata.title^3", "metadata.path^2", "metadata.file_name^1"]
                        }},
                        {"knn": {
                            "field": "vector",
                            "query_vector": query_vector,
                            "k": k,
                            "num_candidates": 100
                        }}
                    ]
                }
            }
        }
        response = self.es.search(index=self.index_name, body=query)
        return response

    def query(self, question, method="standard"):
        """
        Méthode principale pour gérer la question utilisateur et choisir la méthode de recherche.
        """
        query_vector = self.vectorize_question(question)
        
        if method == "standard":
            return self.standard_search(question)
        elif method == "knn":
            return self.knn_search(query_vector)
        elif method == "rrf":
            return self.rrf_search(question, query_vector)
        elif method == "boost":
            return self.boosted_search(question, query_vector)
        else:
            raise ValueError(f"Méthode inconnue: {method}")

    def get_metadata_as_list(self, results):
        """
        Retourne les métadonnées et le texte des chunks pour les résultats de la recherche sous forme de liste.
        """
        metadata_list = []  # Liste pour stocker les métadonnées

        if isinstance(results, dict) and 'hits' in results:
            # Cas standard, KNN, ou Boost où results est un dictionnaire Elasticsearch
            for result in results['hits']['hits']:
                metadata = result['_source'].get('metadata', {})
                chunk_text = result['_source'].get('chunk', 'Texte du chunk non disponible')
                metadata_list.append({
                    "Title": metadata.get('title', 'N/A'),
                    "Path": metadata.get('path', 'N/A'),
                    "File Name": metadata.get('file_name', 'N/A'),
                    "Chunk ID": metadata.get('chunk_id', 'N/A'),
                    "Timestamp": metadata.get('timestamp', 'N/A'),
                    "Score": result['_score'],
                    "Chunk Text": chunk_text
                })
        elif isinstance(results, list):
            # Cas RRF où results est une liste de tuples (doc_id, score)
            for doc_id, score in results:
                # Recherche du document complet par ID pour obtenir les métadonnées et le texte du chunk
                doc = self.es.get(index=self.index_name, id=doc_id)
                metadata = doc['_source'].get('metadata', {})
                chunk_text = doc['_source'].get('chunk', 'Texte du chunk non disponible')
                metadata_list.append({
                    "Title": metadata.get('title', 'N/A'),
                    "Path": metadata.get('path', 'N/A'),
                    "File Name": metadata.get('file_name', 'N/A'),
                    "Chunk ID": metadata.get('chunk_id', 'N/A'),
                    "Timestamp": metadata.get('timestamp', 'N/A'),
                    "Score": score,
                    "Chunk Text": chunk_text
                })
        else:
            print("Format de résultat inattendu.")
        
        return metadata_list  # Retourne la liste des métadonnées

