from sentence_transformers import CrossEncoder
from elasticsearch import Elasticsearch, exceptions
import json

class QueryHandler:

    def __init__(self, index_name="pdf_chunks", reranker_model='models/ms-marco-MiniLM-L-12-v2'):
        self.ip = "127.0.0.1"
        self.port = "9200"
        self.url = f"http://{self.ip}:{self.port}"
        self.username = "elastic"
        with open("classesconfig.json", "r") as fichier:
            config = json.load(fichier)
            self.password = config.get("password")

        try:
            self.indexer = Elasticsearch(self.url, basic_auth=(self.username, self.password))
            if not self.indexer.indices.exists(index=index_name):
                raise ValueError(f"Index '{index_name}' don't exist.")
            self.index_name = index_name
        except exceptions.ConnectionError as e:
            print(f"Elasticsearch connection error: {e}")
            raise
        except Exception as e:
            print(f"Error when init Elasticsearch: {e}")
            raise

        self.cross_encoder = CrossEncoder(reranker_model)

    def rerank_results(self, question, results_as_list):
        """
        Rerank results using CrossEncoder.
        """
        pairs = [(question, result['Chunk Text']) for result in results_as_list]

        scores = self.cross_encoder.predict(pairs)

        reranked_results = sorted(zip(results_as_list, scores), key=lambda x: x[1], reverse=True)

        return [result for result, _ in reranked_results]
