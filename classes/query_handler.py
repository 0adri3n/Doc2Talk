from sentence_transformers import CrossEncoder
from elasticsearch import Elasticsearch, exceptions

class QueryHandler:

    def __init__(self, index_name="pdf_chunks", reranker_model='models/ms-marco-MiniLM-L-12-v2'):
        self.ip = "127.0.0.1"
        self.port = "9200"
        self.url = f"http://{self.ip}:{self.port}"
        self.username = "elastic"
        self.password = "Mck35G-U8mqPqdawQFqB"

        # Initialiser Elasticsearch
        try:
            self.indexer = Elasticsearch(self.url, basic_auth=(self.username, self.password))
            # Vérifiez si l'index existe
            if not self.indexer.indices.exists(index=index_name):
                raise ValueError(f"L'index '{index_name}' n'existe pas.")
            self.index_name = index_name
        except exceptions.ConnectionError as e:
            print(f"Erreur de connexion à Elasticsearch: {e}")
            raise
        except Exception as e:
            print(f"Une erreur s'est produite lors de l'initialisation d'Elasticsearch: {e}")
            raise

        # Initialiser le CrossEncoder pour le reranking
        self.cross_encoder = CrossEncoder(reranker_model)

    def rerank_results(self, question, results_as_list):
        """
        Rerank les résultats de recherche en utilisant le CrossEncoder.
        """
        # Créer les paires pour le CrossEncoder à partir de results_as_list
        pairs = [(question, result['Chunk Text']) for result in results_as_list]

        # Prédire les scores avec le CrossEncoder
        scores = self.cross_encoder.predict(pairs)

        # Associer les scores aux résultats et trier
        reranked_results = sorted(zip(results_as_list, scores), key=lambda x: x[1], reverse=True)

        return [result for result, _ in reranked_results]
