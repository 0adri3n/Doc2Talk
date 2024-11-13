from fastapi import FastAPI, BackgroundTasks, Request, File, UploadFile, Form
import socket
import json
import re
from collections import Counter
from pathlib import Path

from classes.logger import Logger
from classes.prompter import Prompter
from classes.user_query import UserQuery
from classes.query_handler import QueryHandler
from classes.pdf_chunker import PDFChunker
from classes.elastic_indexer import ElasticIndexer
from sentence_transformers import SentenceTransformer, CrossEncoder

app = FastAPI()
# uvicorn fast_api:app --reload --port 8083

logger = Logger(filename="logs_fastapi", write_file=True)
prompter = Prompter(model="gemma2")

@app.post("/ask")
async def query_llm(request: Request, index_name: str = Form(...), question: str = Form(...)) :
    """
    Ask LLM and get an answer.
    """
    client_ip = request.client.host
    try:
        client_hostname = socket.gethostbyaddr(client_ip)[0]
    except socket.herror:
        client_hostname = "Hostname unavailable"

    user_query = UserQuery(index_name=index_name)
    query_handler = QueryHandler(index_name=index_name)

    response = user_query.query(question, method="rrf")
    results = user_query.get_metadata_as_list(response)
    reranked_results = query_handler.rerank_results(question=question, results_as_list=results)

    prompt = prompter.generate_prompt(reranked_results, question)
    answer = prompter.get_response_from_ollama(prompt)

    logger.send_log(
        f"FAST API request : /ask, question: {question} | index: {index_name}",
        client_ip,
        client_hostname,
        r_code=200,
        answer=answer
    )

    return {
        "message": "Query processed successfully.",
        "question": question,
        "answer": answer
    }

@app.post("/download-models")
async def download_models(request: Request, background_tasks: BackgroundTasks):
    """Download and save transformer models in the background if not already downloaded."""

    def download():
        models = {
            "ms-marco-MiniLM-L-12-v2": "cross-encoder/ms-marco-MiniLM-L-12-v2",
            "e5-multilingual": "intfloat/multilingual-e5-large"
        }

        for model_name, model_path in models.items():
            model_dir = Path(f"models/{model_name}")
            if model_dir.exists():
                print(f"Model {model_name} already exists. Skipping download.")
                continue
            
            print(f"Starting download: {model_name}")
            model = (CrossEncoder(model_path) if "cross-encoder" in model_path 
                     else SentenceTransformer(model_path))
            model.save(model_dir)
            print(f"Download finished: {model_name}")

    background_tasks.add_task(download)

    client_ip = request.client.host

    try:
        client_hostname = socket.gethostbyaddr(client_ip)[0]
    except socket.herror:
        client_hostname = "Hostname unavailable"

    logger.send_log("FAST API request : /download-models", client_ip, client_hostname, r_code=200, answer="Model download initiated (or skipped if already present).")

    return {"message": "Model download initiated (or skipped if already present)."}


# curl -X POST "http://127.0.0.1:8083/index-new-pdf" -F "index_name=pdf_dogs" -F "pdf_file=@dogs_doc.pdf"
@app.post("/index-new-pdf")
async def index_new_pdf(request: Request, index_name: str = Form(...), pdf_file: UploadFile = File(...)):
    """Index a new PDF file to the specified Elasticsearch index and save the file."""
    
    pdf_dir = Path(f"pdfs/{index_name}/")
    pdf_dir.mkdir(parents=True, exist_ok=True) 

    pdf_path = f"pdfs/{index_name}/{pdf_file.filename}"
    with open(pdf_path, "wb") as f:
        content = await pdf_file.read()
        f.write(content)

    indexer = ElasticIndexer(index_name=index_name)
    chunker = PDFChunker(path=f"pdfs/{index_name}/", config_file=f"pdfs/{index_name}/indexed.json", indexer=indexer)
    
    processed_data = chunker.process_all_pdfs()

    client_ip = request.client.host

    try:
        client_hostname = socket.gethostbyaddr(client_ip)[0]
    except socket.herror:
        client_hostname = "Hostname unavailable"

    logger.send_log("FAST API request : /index-new-pdf", client_ip, client_hostname, r_code=200, answer="Indexing completed.")

    return {
        "message": "Indexing completed.",
        "chunks_processed": len(processed_data),
        "file_saved": str(pdf_path)
    }

@app.post("/reset-index")
async def reset_index(request: Request, index_name: str = Form(...)):
    """Reset specified Elasticsearch index and re-index PDFs from the specified path."""
    
    indexer = ElasticIndexer(index_name=index_name)
    indexer.delete_all_documents()

    client_ip = request.client.host

    try:
        client_hostname = socket.gethostbyaddr(client_ip)[0]
    except socket.herror:
        client_hostname = "Hostname unavailable"

    logger.send_log("FAST API request : /reset-index", client_ip, client_hostname, r_code=200, answer="Indexing reset.")

    return {
        "message": "Index reset.",
        "index_name": index_name
    }
