from fastapi import FastAPI, BackgroundTasks, Request, File, UploadFile, Form, HTTPException
import socket
import sqlite3
import json
from pyDes import triple_des
from pathlib import Path
from functools import wraps

from classes.logger import Logger
from classes.prompter import Prompter
from classes.user_query import UserQuery
from classes.query_handler import QueryHandler
from classes.pdf_chunker import PDFChunker
from classes.elastic_indexer import ElasticIndexer
from sentence_transformers import SentenceTransformer, CrossEncoder

app = FastAPI()
# uvicorn fast_api:app --host 0.0.0.0 --reload --port 8083

logger = Logger(filename="logs_fastapi", write_file=True)
prompter = Prompter(model="gemma2")

CONFIG_PATH = "data/data_location.json"

def load_config():
    with open(CONFIG_PATH, "r") as config_file:
        return json.load(config_file)

def load_encryption_key():
    config = load_config()
    key_path = Path(config["encryption_key_path"])
    if not key_path.exists():
        raise FileNotFoundError(f"Encryption key not found at {key_path}. Please generate it.")
    with open(key_path, "rb") as key_file:
        return key_file.read()

def validate_token(token: str):
    config = load_config()
    db_path = config["db_path"]
    encryption_key = load_encryption_key()
    encrypted_token = triple_des(encryption_key).encrypt(token, padmode=2)
    print(encrypted_token)
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT token FROM tokens WHERE token = ?", (encrypted_token,))
        if not cursor.fetchone():
            raise HTTPException(status_code=403, detail="Invalid or unauthorized token.")


def extract_token(authorization: str) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="Invalid Authorization header format. Expected 'Bearer <token>'.")
    return authorization[len("Bearer "):]

import socket
from fastapi import HTTPException, Request
from functools import wraps

def token_required(endpoint_func):
    @wraps(endpoint_func)
    async def wrapper(request: Request, *args, **kwargs):
        client_ip = request.client.host

        try:
            client_hostname = socket.gethostbyaddr(client_ip)[0]
        except socket.herror:
            client_hostname = "Hostname unavailable"

        authorization = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(status_code=401, detail="Missing Authorization header.")
        
        token = extract_token(authorization)

        logger.send_log(
            f"FAST API Request : Token validation attempt for {token}",
            client_ip,
            client_hostname,
            r_code=200,
            answer="Token validation in progress"
        )
        validate_token(token)

        return await endpoint_func(request=request, *args, **kwargs)

    return wrapper


@app.get("/test-endpoint")
@token_required
async def secure_endpoint(request: Request):
    return {"message": "Secure endpoint accessed successfully."}

@app.post("/ask")
@token_required
async def query_llm(request: Request, index_name: str = Form(...), question: str = Form(...)):
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
@token_required
async def download_models(request: Request, background_tasks: BackgroundTasks):
    def download():
        models = {
            "ms-marco-MiniLM-L-12-v2": "cross-encoder/ms-marco-MiniLM-L-12-v2",
            "e5-multilingual": "intfloat/multilingual-e5-large"
        }
        for model_name, model_path in models.items():
            model_dir = Path(f"models/{model_name}")
            if model_dir.exists():
                continue
            model = (CrossEncoder(model_path) if "cross-encoder" in model_path 
                     else SentenceTransformer(model_path))
            model.save(model_dir)
    background_tasks.add_task(download)
    client_ip = request.client.host
    try:
        client_hostname = socket.gethostbyaddr(client_ip)[0]
    except socket.herror:
        client_hostname = "Hostname unavailable"
    logger.send_log("FAST API request : /download-models", client_ip, client_hostname, r_code=200, answer="Model download initiated (or skipped if already present).")
    return {"message": "Model download initiated (or skipped if already present)."}

@app.post("/index-new-pdf")
@token_required
async def index_new_pdf(request: Request, index_name: str = Form(...), pdf_file: UploadFile = File(...)):
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
@token_required
async def reset_index(request: Request, index_name: str = Form(...)):
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
