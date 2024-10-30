from classes.pdf_chunker import PDFChunker
from classes.elastic_indexer import ElasticIndexer

print("\nThis script will the new PDFs in pdfs/ folder to the Elastic Database.")
choice = input("Are you sure to proceed [Y/N] > ")

if choice.upper() == "Y" :

    indexer = ElasticIndexer(index_name="pdf_chunks_dogs")

    print("\n[Processing new PDFs]")

    chunker = PDFChunker(path="pdfs/dogs/", config_file="pdfs/dogs/indexed.json", indexer=indexer)
    processed_data = chunker.process_all_pdfs()

    print("\n[Indexing done]")

    print(f"\n[Chunk processed : {len(processed_data)}]")

else :

    print("Cancelling.")