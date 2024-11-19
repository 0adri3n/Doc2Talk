<h1 align="center" id="title">Doc2Talk</h1>

<p align="center"><img src="https://cdn.icon-icons.com/icons2/4042/PNG/512/bot_smile_robot_robo_chatbot_assistant_advisor_icon_256844.png" alt="project-image" width="200"></p>

<p id="description">Use LLM in Python to interact with your documentations.</p>

---


<h2>Project Screenshots:</h2>

![image](https://github.com/user-attachments/assets/d94efb12-6219-4a1b-9b4f-f511daefbe30)

![image](https://github.com/user-attachments/assets/5ccacb5b-3a82-40fa-8284-796afa7ebc3d)

<h2>⚙ Project Architecture</h2>

![image](https://github.com/user-attachments/assets/dce23594-4d2f-4177-a42f-4581d3b9a83f)


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
  - `model` (str, required): Name of model to use for the prompt.
- **Example Request**:
  ```bash
  curl -X POST "http://127.0.0.1:8083/ask" -F "index_name=pdf_dogs" -F "question=Who is the prettiest dog ?" -F "model=gemma2:latest"  -H "Authorization: Bearer <YOUR_TOKEN>"
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
  curl -X POST "http://127.0.0.1:8083/download-models" -H "Authorization: Bearer <YOUR_TOKEN>"
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
  curl -X POST "http://127.0.0.1:8083/index-new-pdf" -F "index_name=pdf_dogs" -F "pdf_file=@path/to/file.pdf" -H "Authorization: Bearer <YOUR_TOKEN>"
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
  curl -X POST "http://127.0.0.1:8083/reset-index" -F "index_name=pdf_dogs" -H "Authorization: Bearer <YOUR_TOKEN>"
  ```
- **Response**:
  ```json
  {
    "message": "Index reset.",
    "index_name": "pdf_dogs"
  }
  ```

  ### 5. `/check-models` (POST)
Check loaded models on Ollama instance.

- **URL**: `/check-models`
- **Method**: GET
- **Example Request**:
  ```bash
  curl -X GET "http://127.0.0.1:8083/check-models" -H "Authorization: Bearer <YOUR_TOKEN>"
  ```
- **Response**:
  ```json
  {
      "models": [
          "mistral:latest",
          "phi3:3.8b",
          "qwen2.5-coder:3b",
          "gemma2:latest",
          "llama3.2:latest"
      ]
  }
  ```

  ### 6. `/test-endpoint` (GET)
Just a test endpoint.
- **URL**: `/test-endpoint`
- **Method**: GET
- **Example Request**:
  ```bash
  curl -X GET "http://127.0.0.1:8083/test-endpoint" -H "Authorization: Bearer <YOUR_TOKEN>"
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

---

<h2>Ollama Models Benchmark Summary</h2>

#### **Time Performance**
| Model                  | Total Time (s) | Average Time per Query (s) | Number of Queries |
|------------------------|----------------|----------------------------|--------------------|
| **mistral:latest**     | 257.81         | 85.94                      | 3                  |
| **phi3:3.8b**          | 196.86         | 65.62                      | 3                  |
| **qwen2.5-coder:3b**   | 110.98         | 36.99                      | 3                  |
| **gemma2:latest**      | 323.61         | 107.87                     | 3                  |
| **llama3.2:latest**    | 101.65         | 33.88                      | 3                  |

- **Fastest Model:** `llama3.2:latest` with an average query time of **33.88s**.
- **Slowest Model:** `gemma2:latest` with an average query time of **107.87s**.

#### **Resource Consumption**
- **CPU Usage:**
  - Spikes observed up to 1600% utilization across 16 CPUs.
  - Sustained usage varied between 600% and 1200% during intensive query phases.
- **Memory Usage:**
  - Peaked at **27.02GB** out of 30.48GB.
  - Steady increments in memory consumption noted during benchmark progression.

#### **Linguistic Robustness**
- All five models can write almost perfectly in English. However, I've already seen some grammatical faults in other languages like French while using Llama3.2.
- Testing all languages trained on each models can perfect this benchmark, although using English for every prompt avoid spelling mistakes.

#### **Relevance of Responses**
- In my opinion `gemma2` provide detailed answers, constructed only with informations given from the documentation and not other informations.
- `mistral` and `llama3.2` are still well-trained models but they can provide fake informations by inventing them if they don't find answers.
- `phi3` and `qwen2.5` show good answers, but `phi3` seems to be more efficient than `qwen2.5` which provides short answers with a lack of details


### **System Specifications**

| Component          | Specification                                                 |
|---------------------|---------------------------------------------------------------|
| **RAM**            | 64GB                                                          |
| **CPU**            | 11th Gen Intel(R) Core(TM) i7-11800H @ 2.30GHz (8 cores, 16 threads) |
| **Docker Allocations** | ~32GB RAM and 16 logical CPUs                               |
| **GPU**            | Not utilized (Ollama runs on CPU)                              |

### **Observations**
1. **Time Efficiency:** `llama3.2:latest` delivered the fastest responses, making it the most time-efficient model for the queries.
2. **Resource Usage:**
   - High CPU utilization was noted, suggesting intensive computation demands across all models.
   - Memory usage was near capacity, indicating the need for systems with significant memory resources for similar tasks.
3. **Performance vs. Time:** `gemma2:latest` was the slowest but consumed comparable CPU and memory resources to faster models like `qwen2.5-coder:3b`.

#### **Conclusion**
- For scenarios prioritizing speed, `llama3.2:latest` is the best option.
- For scenario prioritizing informations look-up in a document, `gemma2` seems to be the best option.

### Benchmark Responses

#### **Question 1:** *What are the risk factors for addiction mentioned in the document?*

| model            | response                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | time_taken         |
|------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------|
| mistral:latest   | 1. Environmental factors:<br>   - Home and Family: Parental substance abuse, criminal behavior, or a chaotic home environment.<br>   - Peer and School: Drug-using peers, academic failure, poor social skills, and negative school environment.<br>   - Community: Community poverty, lack of neighborhood pride, and community attitudes that are permissive towards drug use.<br><br>2. Biological factors:<br>   - Genetics: A person's genetic makeup can increase their vulnerability to addiction.<br>   - Gender and ethnicity: These factors may play a role in the development of addiction.<br>   - Mental disorders: People with mental health conditions are at greater risk of drug abuse and addiction.<br>   - Stage of development: Adolescents and children are more susceptible due to their developmental stage.<br>   - Other medical conditions: Certain medical conditions can also increase a person's risk of addiction.                                                                                                                                                                                                          | 95.5136296749115   |
| phi3:3.8b        | The review identifies multiple environmental and biological risk factors associated with drug abuse and addiction. Environmental risks include aspects such as a chaotic home environment, exposure to substance use by parents or siblings, involvement in criminal behavior within the family, peer pressure from friends who use drugs, poor academic performance, lack of extracurricular activities, negative school experiences like harassment and bullying, unstable living conditions such as poverty, neighborhood violence, perceived community acceptance of drug-taking practices. Biological factors include genetics (estimated between 40 to 60 percent influence on a person’s vulnerability), gender disparities in substance abuse rates with males being more susceptible than females, and the prevalence of mental health disorders such as depression or attention deficit hyperactivity disorder that can increase risk. Furthermore, personal characteristics like aggression, impulsivity, lack of self-control during childhood, poor social skills, academic competency issues also play a role in increasing addiction risks. | 61.49191761016846  |
| qwen2.5-coder:3b | The risk factors for addiction mentioned in the document include:<br><br>1. Genetic factors (40-60% of vulnerability)<br>2. Environmental factors like family, peer, school influence<br>3. Social skills and self-control<br>4. Lack of parental supervision<br>5. Poor academic performance<br>6. Gender<br>7. Mental disorders<br>8. Chaotic home environment or abuse<br>9. Parent's use and attitudes<br>10. Peer influences<br>11. Community attitudes<br>12. Poor school achievement                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | 37.319685220718384 |
| gemma2:latest    | The document lists several risk factors for addiction, categorized as environmental and biological:<br><br>**Environmental Risk Factors:**<br><br>* **Home and Family:** Parental or older family member drug or alcohol abuse, criminal behavior.<br>* **Peer and School:** Drug-using peers, academic failure, poor social skills.<br>* **Early use of drugs**<br>* **Availability of drugs**<br>* **Cost of drugs**<br>* **Route of administration**<br>* **Effect of the drug itself**<br>* **Community attitudes**<br>* **Poor school achievement**<br><br>* **Chaotic home environment and abuse**<br>* **Parents' drug use and attitudes**<br>* **Peer influences** <br><br><br>**Biological Risk Factors:**<br><br>* **Genetics**<br>* **Gender**<br>* **Mental disorders** <br><br><br><br>Let me know if you have any other questions about the document.                                                                                                                                                                                                                                                                                        | 116.66316318511963 |
| llama3.2:latest  | The risk factors for addiction mentioned in the document include:<br><br>1. Genetic factors<br>2. Environmental factors, such as:<br>   - Home and family (parents' or older family members' abuse of alcohol or drugs, or criminal behavior)<br>   - Peer and school (drug-using peers can influence young people to try drugs for the first time)<br>   - Academic failure or poor social skills<br>3. Biological factors, such as:<br>   - Genetics<br>   - Gender<br>   - Mental disorders<br>4. Social and community factors, including:<br>   - Chaotic home and abuse<br>   - Parent's use and attitudes towards drugs<br>   - Peer influences<br>   - Community attitudes towards drugs<br>   - Poor school achievement                                                                                                                                                                                                                                                                                                                                                                                                                            | 38.27025127410889  |



#### **Question 2:** *How do drugs alter the brain's reward system?*

| model            | response                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | time_taken         |
|------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------|
| mistral:latest   |  Drugs alter the brain's reward system by flooding it with dopamine, a neurotransmitter associated with feelings of pleasure. This overstimulation of the reward circuit produces euphoric effects that strongly reinforce the behavior of drug use, teaching the user to repeat it. Over time, long-term drug abuse can cause impairment in cognitive function and adaptations in habit or non-conscious memory systems. The brain learns to associate activities with pleasure or reward, making drugs more addictive than natural rewards due to their ability to release a greater amount of dopamine when taken.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | 79.14704704284668  |
| phi3:3.8b        | Drugs of abuse alter the brain's reward system by flooding it with dopamine. Normally, dopamine is released in response to natural rewards like food and sex, which reinforces behaviors essential for survival. However, drugs can cause a much greater release or mimic this process more effectively, leading to an exaggerated increase in dopamine levels within the brain's reward circuitry. This disruption greatly amplifies messages related to pleasure and craving pathways, which over time teaches individuals to repeat drug-taking behaviors as a form of self-medication or escape from negative emotions associated with cravings.<br><br>Additionally, some drugs can cause long-term changes in the brain's chemistry by affecting other neurotransmitters like glutamate that are involved in learning and memory processes within this circuitry. These alterations not only reinforce drug use but also impair cognitive functions such as decision making and problem solving, which further perpetuates addictive behaviors without conscious thought or control from the user. | 62.54024696350098  |
| qwen2.5-coder:3b | Drugs of abuse alter the brain's reward system by flooding it with dopamine, which is a neurotransmitter that regulates movement, emotion, motivation, and feelings of pleasure. When cocaine is taken, dopamine increases are exaggerated, and communication is altered. This increased dopamine causes euphoric effects, which strongly reinforce drug use and teach the user to repeat it.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 34.330410957336426 |
| gemma2:latest    | Drugs of abuse primarily work by flooding the brain’s reward system with dopamine. Dopamine is a neurotransmitter associated with pleasure and motivation. Drugs cause an exaggerated increase in dopamine, disrupting the normal communication channels within this circuit. This overstimulation creates a feeling of euphoria and reinforces the behavior of drug use, making the user more likely to repeat it.  <br><br><br>Here's a breakdown from the provided text:<br><br>* **Dopamine:** Drugs target the brain's reward system by increasing dopamine levels much higher than natural rewards like food or music would.<br>* **Overstimulation:** This surge of dopamine creates an intense feeling of pleasure, known as euphoria, that strongly reinforces drug use. <br>* **Learning:** The brain learns to associate the drug with pleasure, making it more likely the user will seek out and repeat the behavior. <br><br><br><br>Let me know if you have any other questions!                                                                                                           | 107.45936226844788 |
| llama3.2:latest  | Drugs of abuse directly or indirectly target the brain’s reward system by flooding the circuit with dopamine. This increases dopamine levels and exaggerates natural responses, leading to amplified messages that disrupt communication channels. When a drug is taken, it activates the brain's pleasure center, releasing high amounts of dopamine (2-10 times more than normal) which reinforces the behavior of drug use and teaches the user to repeat it.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | 30.478031873703003 |



#### **Question 3:** *What are the health consequences of long-term drug addiction?*

| model            | response                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | time_taken        |
|------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------|
| mistral:latest   |  The health consequences of long-term drug addiction may include lung or cardiovascular disease, stroke, cancer, mental disorders, HIV/AIDS, hepatitis B and C, lung disease, and negative effects from prenatal drug exposure on infants and children. These consequences can lead to intellectual development delays, behavioral problems in children, academic struggles, increased risk of unplanned pregnancies, violence, and infectious diseases among adolescents. Furthermore, long-term drug abuse can impair cognitive function due to changes in the brain's reward circuit and learning ability.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | 83.15089654922485 |
| phi3:3.8b        | The review indicates that individuals suffering from long-term drug addiction often encounter multiple medical issues. These may include diseases affecting the lungs, heart, blood vessels (cardiovascular disease), brain functions such as strokes or seizures due to cerebrovascular disorders and epilepsy respectively, various types of cancer caused by substances like nicotine found in smoked drugs, HIV/AIDS transmission through needle sharing among intravenous drug users (Hepatitis B and C can also be transmitted this way), lung diseases including emphysema or chronic bronchitis that are exacerbated by tobacco smoke abuse. Additionally, mental disorders like depression may worsen due to the physiological changes induced in brain structures such as the ventral tegmental area (VTA) and its connections with the nucleus accumbens during substance misuse; these areas are part of what is called reward circuitry. Furthermore, drug abusers often have impaired cognitive functions due to altered concentrations of neurotransmitters like glutamate that play a crucial role in learning and memory processes within the brain. Drug-seeking behavior becomes difficult for some individuals because they struggle with habitual or nonconscious memories associated with drug use, which can be triggered by environmental cues - this is known as conditioning. Lastly, prenatal exposure to drugs has harmful consequences on infants and children's developmental outcomes leading potentially to premature birth, low birth weight, slower intellectual growth, behavior issues in adulthsoftheir life, educational struggles during childhood, increased risk for unplanned pregnancies among teenagers addicted to drugs, susceptibility to violence and infectious diseases. | 72.8249089717865  |
| qwen2.5-coder:3b | long-term drug addiction can cause serious health problems for others. Three of the more devastating and troubling consequences of addiction are: zNegative effects of prenatal drug exposure on infants and children A mother's abuse of heroin or prescription opioids during pregnancy can cause a withdrawal syndrome (called neonatal abstinence syndrome, or NAS) in her infant. It is also likely that some drug- exposed children will need educational support in the classroom to help them overcome what may be subtle deficits in developmental functioning.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | 39.32793068885803 |
| gemma2:latest    | Long-term drug addiction can have severe medical consequences, affecting various organs and systems. <br><br>Here's a summary based on the provided text:<br><br>* **Cardiovascular Disease:**  Addiction increases the risk of heart disease and stroke.<br>* **Respiratory Issues:** Lung diseases and cancer are common outcomes of prolonged drug abuse, especially with tobacco use.<br>* **Cancer:** Smoking, a common addiction, is directly linked to various cancers like mouth, throat, larynx, and blood cancers. <br>* **Mental Disorders:** Addiction can worsen existing mental health conditions or trigger new ones.<br><br>The text also highlights the impact of prenatal drug exposure on infants, causing neonatal abstinence syndrome and developmental issues.  <br><br><br>Let me know if you have any other questions.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | 99.49221539497375 |
| llama3.2:latest  | According to the provided text, the health consequences of long-term drug addiction include:<br><br>1. Cardiovascular disease<br>2. Stroke<br>3. Cancer<br>4. HIV/AIDS<br>5. Hepatitis B and C<br>6. Lung disease<br>7. Mental disorders (including negative effects on prenatal exposure)<br><br>Additionally, long-term drug abuse can also cause impairments in cognitive function due to alterations in the brain's reward circuit and ability to learn.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | 32.89807438850403 |



---

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
- [X] Benchmark differents models

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
