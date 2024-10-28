from classes.pdf_chunker import PDFChunker
from classes.elastic_indexer import ElasticIndexer

# Exemple d'utilisation
indexer = ElasticIndexer(index_name="pdf_chunks")
indexer.delete_all_documents()
chunker = PDFChunker(path="pdfs/", config_file="pdfs/cache/indexed.json", indexer=indexer)
processed_data = chunker.process_all_pdfs()

# Afficher le nombre de chunks traités et vectorisés
print(f"Nombre de chunks traités : {len(processed_data)}")
print(processed_data[3])
print("\n\n")
print(processed_data[8])