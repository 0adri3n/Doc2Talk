from sentence_transformers import SentenceTransformer, models
from elasticsearch import Elasticsearch
import json

class UserQuery:
    
    def __init__(self, index_name="pdf_chunks"):

        self.ip = "127.0.0.1"
        self.port = "9200"
        self.url = "http://" + self.ip + ":" + self.port
        self.username = "elastic"
        with open("classes/config.json", "r") as fichier:
            config = json.load(fichier)
            self.password = config.get("password")

        self.es = Elasticsearch(self.url, basic_auth=(self.username, self.password))
        self.index_name = index_name

        word_embedding_model = models.Transformer("models/e5-multilingual")
        pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension())
        self.model = SentenceTransformer(modules=[word_embedding_model, pooling_model])

    def vectorize_question(self, question):

        question_vector = self.model.encode(question)
        return question_vector

    def standard_search(self, query_text):

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

        text_search = self.standard_search(query_text)
        knn_search = self.knn_search(query_vector, k)

        text_results = {hit['_id']: hit['_score'] for hit in text_search['hits']['hits']}
        knn_results = {hit['_id']: hit['_score'] for hit in knn_search['hits']['hits']}

        rrf_results = {}
        for doc_id in set(text_results.keys()).union(knn_results.keys()):
            text_rank = 1 / (50 + text_results.get(doc_id, 0)) 
            knn_rank = 1 / (50 + knn_results.get(doc_id, 0))  
            rrf_results[doc_id] = text_rank + knn_rank

        sorted_rrf_results = sorted(rrf_results.items(), key=lambda item: item[1], reverse=True)
        return sorted_rrf_results

    def boosted_search(self, query_text, query_vector, k=10):

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
            raise ValueError(f"Method not found : {method}")

    def get_metadata_as_list(self, results):

        metadata_list = []  

        if isinstance(results, dict) and 'hits' in results:
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
            for doc_id, score in results:
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
            print("Results format not recognized.")
        
        return metadata_list 

