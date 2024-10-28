# Doc2Talk
Use LLM to interact with docs

Require : 

- Ollama on Docker (No edits necessary) | 
<a href="https://hub.docker.com/r/ollama/ollama" target="_blank">Installation link</a> |
Please pull Llama 3.2 by executing ```ollama pull llama3.2``` in the Ollama Docker container terminal.

- Elasticsearch (Remove SSL protection) | 
<a href="https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html" target="_blank">Installation link</a> | 
<a href="https://dev.to/wangpin34/how-to-disable-ssl-authencation-of-elasticsearch-46je" target="_blank">Remove SSL</a>


Installation : 


1 : 

Python Packages installation : ```pip install elasticsearch sentence_transformers PyPDF2 flask flask_limiter --user```

2 : 

Execute ```download_model.py``` to download CrossEncoder and SentenceTransformers models locally (Your data is YOUR data.)

3 :

First start ? Execute ```reset_db.py``` to index your very first PDFs to Elastic.

4 : 

Execute ```web_server.py``` and reach your local web server !


<img src="https://github.com/0adri3n/Doc2Talk/blob/master/screen_web.png"/>


<img src="https://github.com/0adri3n/Doc2Talk/blob/master/screen_docker.png"/>
