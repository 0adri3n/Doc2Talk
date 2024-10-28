#coding: utf-8
from elasticsearch import Elasticsearch, helpers
import json

class ElasticIndexer:
    
    def __init__(self, index_name="pdf_chunks"):
        """
        Initialisation de l'indexeur Elasticsearch.
        """
        self.ip = "127.0.0.1"
        self.port = "9200"
        self.url = "http://" + self.ip + ":" + self.port
        self.username = "elastic"
        with open("config.json", "r") as fichier:
            config = json.load(fichier)
            self.password = config.get("password")

        self.es = Elasticsearch(self.url, basic_auth=(self.username, self.password))
        self.index_name = index_name
        self.create_index_if_not_exists()

    def create_index_if_not_exists(self):
        """
        Crée un index Elasticsearch s'il n'existe pas déjà.
        """
        if not self.es.indices.exists(index=self.index_name):
            mapping = {
                "mappings": {
                    "properties": {
                        "vector": {
                            "type": "dense_vector",
                            "dims": 1024
                        },
                        "metadata": {
                            "properties": {
                                "title": {"type": "text"},
                                "path": {"type": "text"},
                                "file_name": {"type": "keyword"},
                                "chunk_id": {"type": "integer"},
                                "timestamp": {"type": "date"}
                            }
                        },
                        "chunk": {"type": "text"}  # Ajout du champ chunk pour stocker le texte
                    }
                }
            }
            self.es.indices.create(index=self.index_name, body=mapping)
            print(f"Index '{self.index_name}' créé.")
        else:
            print(f"L'index '{self.index_name}' existe déjà.")


    def index_chunks(self, chunks):
        """
        Indexe les chunks vectorisés dans Elasticsearch.
        """
        actions = []
        for chunk in chunks:
            action = {
                "_index": self.index_name,
                "_source": {
                    "vector": chunk['vector'],
                    "chunk": chunk['chunk'],  # Ajout du texte du chunk ici
                    "metadata": chunk['metadata']
                }
            }
            actions.append(action)

        helpers.bulk(self.es, actions)
        print(f"{len(chunks)} chunks indexés dans Elasticsearch.")

    def delete_all_documents(self):
        """
        Supprime tous les documents de l'index.
        """
        self.es.delete_by_query(index=self.index_name, body={"query": {"match_all": {}}})
        print(f"Tous les documents de l'index '{self.index_name}' ont été supprimés.")
