#coding: utf-8
from elasticsearch import Elasticsearch, helpers
import json

class ElasticIndexer:
    
    def __init__(self, index_name="pdf_chunks"):
        """
        Init Elasticsearch indexer.
        """
        self.ip = "127.0.0.1"
        self.port = "9200"
        self.url = "http://" + self.ip + ":" + self.port
        self.username = "elastic"
        with open("classes/config.json", "r") as fichier:
            config = json.load(fichier)
            self.password = config.get("password")

        self.es = Elasticsearch(self.url, basic_auth=(self.username, self.password))
        if index_name != "":
            self.index_name = index_name
            self.create_index_if_not_exists()

    def create_index_if_not_exists(self):
        """
        Create Elastic indexer if not exists.
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
                        "chunk": {"type": "text"}
                    }
                }
            }
            self.es.indices.create(index=self.index_name, body=mapping)
            print(f"Index '{self.index_name}' created.")
        else:
            print(f"index '{self.index_name}' already exist.")


    def index_chunks(self, chunks):
        """
        Index chunks in Elasticsearch.
        """
        actions = []
        for chunk in chunks:
            action = {
                "_index": self.index_name,
                "_source": {
                    "vector": chunk['vector'],
                    "chunk": chunk['chunk'],
                    "metadata": chunk['metadata']
                }
            }
            actions.append(action)

        helpers.bulk(self.es, actions)
        print(f"{len(chunks)} chunks indexed in Elasticsearch.")

    def delete_all_documents(self):
        """
        Delete all docs from index.
        """
        self.es.delete_by_query(index=self.index_name, body={"query": {"match_all": {}}})
        print(f"All docs from index '{self.index_name}' removed.")

    def get_all_indices(self):
        """
        Get all indices in Elasticsearch.
        """
        indices = self.es.indices.get_alias(index="*")
        visible_indices = []

        for index, details in indices.items():
            if not index.startswith('.') and not details['aliases']:
                visible_indices.append(index)

        return visible_indices
