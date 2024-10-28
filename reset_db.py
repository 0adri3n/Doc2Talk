from classes.pdf_chunker import PDFChunker
from classes.elastic_indexer import ElasticIndexer

print("\nThis script will remove ALL indexed data to replace it by the pdfs in pdfs/ folder.")
choice = input("Are you sure to proceed [Y/N] > ")

if choice == "Y" :

    with open("pdfs/cache/indexed.json", "w") as cache :
        cache.write()
        cache.close()

    print("\n[Cache file reset]")

    indexer = ElasticIndexer(index_name="pdf_chunks")

    print("\n[Removing chunks from Elastic]")
    indexer.delete_all_documents()

    print("\n[Processing new PDFs]")

    chunker = PDFChunker(path="pdfs/", config_file="pdfs/cache/indexed.json", indexer=indexer)
    processed_data = chunker.process_all_pdfs()

    print("\n[Indexing done]")

    print(f"\n[Chunk processed : {len(processed_data)}]")

else :

    print("Cancelling.")