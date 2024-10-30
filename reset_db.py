from classes.pdf_chunker import PDFChunker
from classes.elastic_indexer import ElasticIndexer

print("\nThis script will remove ALL indexed data to replace it by the pdfs in pdfs/ folder.")
choice = input("Are you sure to proceed [Y/N] > ")

if choice.upper() == "Y" :

    confirm = input("Please remove config.json file in the folder then press enter.")

    print("\n[Cache file reset]")

    indexer = ElasticIndexer(index_name="pdf_chunks_dogs")

    print("\n[Removing chunks from Elastic]")
    indexer.delete_all_documents()

    print("\n[Processing new PDFs]")

    chunker = PDFChunker(path="pdfs/dogs/", config_file="pdfs/dogs/indexed.json", indexer=indexer)
    processed_data = chunker.process_all_pdfs()

    print("\n[Indexing done]")

    print(f"\n[Chunk processed : {len(processed_data)}]")

else :

    print("Cancelling.")