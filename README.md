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

**Please pull Llama 3.2 by executing ```ollama pull llama3.2``` in the Ollama Docker container terminal.**

- Elasticsearch (Remove SSL protection necessary) | 
<a href="https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html" target="_blank">Installation link</a> | 
<a href="https://dev.to/wangpin34/how-to-disable-ssl-authencation-of-elasticsearch-46je" target="_blank">Remove SSL</a>

**Please copy the password outputed by Elasticsearch on it's first start and put it in the ```classes/config.json``` file.**

4 . Execute ```download_model.py``` to download CrossEncoder and SentenceTransformers models locally (Your data is YOUR data.)

5 . First start ? Execute ```reset_db.py``` to index your very first PDFs to Elastic. Don't forget to put them in the ```pdfs``` folder and to change the path, the index name and the config path in the script !

6 . Execute ```web_server.py``` and reach your local web server !

7 . That's it ! Doc2Talk is ready 🕺</p>

**Notes** . If you want to add PDFs to an index, execute ```index_new_pdf.py``` and don't forget to edit the script to upload to the right index (and to specify the folder path) !


<h2>📃 To-Do List</h2>

- [ ] Translate to English (GUI, script)
- [ ] Powershell/Bash script to deploy automatically Docker instances
- [ ] API routes
- [ ] Docker Image of Doc2Talk for easy deployment
- [ ] Better GUI
- [ ] Optimize performances
- [X] Create different context, avoid removing all PDFs everytime
- [ ] So, multiple chats
- [X] Progression bar when PDF indexing

<h2>💻 Built with</h2>

Technologies used in the project:

*   Python
*   Flask
*   Docker
*   HuggingFace models
*   Ollama
*   ElasticSearch

<h2>🛡️ License:</h2>

This project is licensed under the MIT

<h2>💖Like my work?</h2>
