<h1 align="center" id="title">Doc2Talk</h1>

<p align="center"><img src="https://cdn.icon-icons.com/icons2/4042/PNG/512/bot_smile_robot_robo_chatbot_assistant_advisor_icon_256844.png" alt="project-image" width="200"></p>

<p id="description">Use LLM in Python to interact with your documentations.</p>

---


<h2>Project Screenshots:</h2>

![image](https://github.com/user-attachments/assets/d94efb12-6219-4a1b-9b4f-f511daefbe30)

![image](https://github.com/user-attachments/assets/5ccacb5b-3a82-40fa-8284-796afa7ebc3d)

<h2>⚙ Project Architecture</h2>

![image](https://github.com/user-attachments/assets/f5efdedb-3937-4936-8329-d41fc6053e04)


<h2>🧐 Features</h2>

Here're some of the project's best features:

*   Upload your PDFs, chunk them and vectorize it
*   Store them in your Elastic Docker container
*   Host your models locally (privacy max 😎)
*   Host your Ollama server
*   Interact with your own chatbot to learn easily from your documentations
*   Request Doc2Talk's Fast API with your own scripts

Here're some of the project's <i>worst</i> features:

*   Use a LOT of ressources

<h2>🛠️ Installation Steps</h2>

1 . Install Docker Desktop (for Windows/Mac/Linux) <a href="https://www.docker.com/products/docker-desktop/">here</a>

2 . Install Python <a href="https://www.python.org/downloads/">here</a>.

3 . Get the necessary Python packages :

```pip install -r requirements.txt --user```

4 . Set up Ollama and Elasticsearch containers :

- Ollama (No edits necessary) | 
<a href="https://hub.docker.com/r/ollama/ollama" target="_blank">Installation link</a>

**Please pull Gemma 2 by executing ```ollama pull gemma2``` in the Ollama Docker container terminal.**

- Elasticsearch (Remove SSL protection necessary) | 
<a href="https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html" target="_blank">Installation link</a> | 
<a href="https://dev.to/wangpin34/how-to-disable-ssl-authencation-of-elasticsearch-46je" target="_blank">Remove SSL</a>

**Please copy the password outputed by Elasticsearch on it's first start and put it in the ```classes/config.json``` file.**

4 . Execute ```download_model.py``` to download CrossEncoder and SentenceTransformers models locally (Your data is YOUR data.)

5 . First start ? Execute ```reset_db.py``` to index your very first PDFs to Elastic. Don't forget to put them in the ```pdfs``` folder and to change the path, the index name and the config path in the script !

6 . Execute ```web_server.py``` and reach your local web server !

7 . That's it ! Doc2Talk is ready 🕺</p>

**Notes** . If you want to add PDFs to an index, execute ```index_new_pdf.py``` and don't forget to edit the script to upload to the right index (and to specify the folder path) !

<h2>⚡FastAPI Doc</h2>

This API uses **FastAPI** to provide services for processing and indexing PDF documents, as well as managing transformer models. The API includes endpoints for querying documents, downloading models, indexing new PDFs, and resetting an Elasticsearch index. Protected with a token system, the API is secured and track user's requests. User's token are encrypted with Triple DES and stored in a Database.

### Prerequisites

- **Encryption Key** (Create a 24 bytes key) : ```python toolbox/generate_key.py```
- **Token Database** (Create a token database on first start) : ```python toolbox/token_manager.py```


To start the API server, run:
```bash
uvicorn fast_api:app --host 0.0.0.0 --reload --port 8083
```

---

### Endpoints

### 1. `/ask` (POST)
Submits a question to the LLM model based on documents indexed in Elasticsearch.

- **URL**: `/ask`
- **Method**: POST
- **Parameters**:
  - `index_name` (str, required): Name of the Elasticsearch index.
  - `question` (str, required): The question to ask.
- **Example Request**:
  ```bash
  curl -X POST "http://127.0.0.1:8083/ask" -F "index_name=pdf_dogs" -F "question=Who is the prettiest dog ?"  -H "Authorization: Bearer <YOUR_TOKEN>"
  ```
- **Response**: 
  ```json
  {
    "message": "Query processed successfully.",
    "question": "Who is the prettiest dog ?",
    "answer": "<Model-generated answer>"
  }
  ```

### 2. `/download-models` (POST)
Downloads and saves the required transformer models if they are not already available.

- **URL**: `/download-models`
- **Method**: POST
- **Description**: Downloads the CrossEncoder and SentenceTransformer models in the background.
- **Example Request**:
  ```bash
  curl -X POST "http://127.0.0.1:8083/download-models -H "Authorization: Bearer <YOUR_TOKEN>""
  ```
- **Response**:
  ```json
  {
    "message": "Model download initiated (or skipped if already present)."
  }
  ```

### 3. `/index-new-pdf` (POST)
Indexes a PDF file into the specified Elasticsearch index.

- **URL**: `/index-new-pdf`
- **Method**: POST
- **Parameters**:
  - `index_name` (str, required): Name of the index where the PDF file will be added.
  - `pdf_file` (file, required): PDF file to be indexed.
- **Example Request**:
  ```bash
  curl -X POST "http://127.0.0.1:8083/index-new-pdf" -F "index_name=pdf_dogs" -F "pdf_file=@path/to/file.pdf -H "Authorization: Bearer <YOUR_TOKEN>""
  ```
- **Response**:
  ```json
  {
    "message": "Indexing completed.",
    "chunks_processed": <Number of processed chunks>,
    "file_saved": "pdfs/<index_name>/<file_name>.pdf"
  }
  ```

### 4. `/reset-index` (POST)
Resets an Elasticsearch index by deleting all its documents.

- **URL**: `/reset-index`
- **Method**: POST
- **Parameters**:
  - `index_name` (str, required): Name of the index to reset.
- **Example Request**:
  ```bash
  curl -X POST "http://127.0.0.1:8083/reset-index" -F "index_name=pdf_dogs -H "Authorization: Bearer <YOUR_TOKEN>""
  ```
- **Response**:
  ```json
  {
    "message": "Index reset.",
    "index_name": "pdf_dogs"
  }
  ```

  ### 4. `/test-endpoint` (GET)
Just a test endpoint.
- **URL**: `/test-endpoint`
- **Method**: GET
- **Example Request**:
  ```bash
  curl -X GET "http://127.0.0.1:8083/test-endpoint" -H "Authorization: Bearer <YOUR_TOKEN>""
  ```
- **Response**:
  ```json
  {
      "message": "Secure endpoint accessed successfully."
  }
  ```

### Logging

Each request is logged with:
- Client IP address
- Hostname (if available)
- Response code
- Response content

### Protection

As an admin, storing the encryption key and the database on a portable device (USB) is advised. Edit the ```data/data_location.json``` and set the locations on your USB.

<h2>📃 To-Do List</h2>

- [X] Replace scripts with an API
- [X] Secure API with tokens
- [ ] Create a Docker instance for every services (Flask Server, APIs)
- [X] API routes to ask the LLM
- [ ] Powershell/Bash script to deploy automatically Docker instances
- [ ] Docker Image of Doc2Talk for easy deployment
- [ ] Better GUI
- [X] Optimize performances (Llama3.2 --> Gamma2 + better context structure)
- [X] Create different context, avoid removing all PDFs everytime
- [ ] So, multiple chats
- [X] Progression bar when PDF indexing
- [X] Translate to English (GUI, script)
- [ ] Benchmark differents models

<h2>💻 Built with</h2>

Technologies used in the project:

*   Python
*   Flask
*   Docker
*   HuggingFace models
*   Ollama
*   ElasticSearch
*   FastAPI
*   Triple DES

<h2>🛡️ License:</h2>

This project is licensed under the MIT

<h2>💖Like my work?</h2>
