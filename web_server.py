from flask import Flask, render_template, request, session
import socket
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from forms.qforms import QuestionForm
from forms.clearform import ClearForm
from classes.logger import Logger
import datetime
import json

from classes.user_query import UserQuery
from classes.query_handler import QueryHandler

app = Flask(__name__)

app.config['SECRET_KEY'] = 'docdoc'

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

csrf = CSRFProtect(app)

logger = Logger()
user_query = UserQuery(index_name="pdf_chunks")
query_handler = QueryHandler(index_name="pdf_chunks")


def generate_prompt(context_chunks, question):
    """
    Construit le prompt pour Ollama avec le contexte et la question.
    """
    context_text = "\n\n".join([chunk['Chunk Text'] for chunk in context_chunks])  # Limiter à 5 chunks par ex.
    prompt = (
        "You are a knowledgeable assistant.\n"
        "Please answer the following question using the provided context.\n\n"
        "Context:\n"
        f"{context_text}\n\n"
        "Question:\n"
        f"{question}\n\n"
        "Answer:"
    )
    return prompt

import requests

def get_response_from_ollama(prompt):
    """
    Envoie le prompt au serveur Ollama et récupère la réponse.
    """
    url = "http://localhost:11434/api/generate"  # URL mise à jour pour Ollama
    payload = {
        "model": "llama3.2",  # Modèle spécifié
        "prompt": prompt,
        "stream": False
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        try:
            data = json.loads(response.text)
            api_response = data.get("response", "")
            
            if not data.get("done", False): 
                print("Le traitement n'est pas encore terminé.")
            else:
                return api_response 
        except json.JSONDecodeError as e:
            print(f"Erreur lors du décodage de la réponse JSON: {e}")
    else:
        return("Erreur:", response.text)


@app.route('/')
def home():
    form = QuestionForm()
    clearform = ClearForm()
    return render_template('index.html', form=form, clearform=clearform)

@app.route('/ask', methods=['POST'])
@limiter.limit("5 per minute")
def ask_question():
    client_ip = request.remote_addr

    try:
        client_hostname = socket.gethostbyaddr(client_ip)[0]
    except socket.herror:
        client_hostname = "Nom d'hôte non disponible"

    form = QuestionForm()

    # Initialiser l'historique dans la session si elle n'existe pas encore
    if 'history' not in session:
        session['history'] = []

    if form.validate_on_submit():
        question = form.question.data

        # Choisir une méthode (par exemple, standard, knn, rrf, boost)
        response = user_query.query(question, method="rrf")
        results = user_query.get_metadata_as_list(response)
        reranked_results = query_handler.rerank_results(question=question, results_as_list=results)

        prompt = generate_prompt(reranked_results, question)

        answer = get_response_from_ollama(prompt)

        # Ajouter la question et la réponse à l'historique de la session
        session['history'].append({'question': question, 'answer': answer})

        log_data = {
            'timestamp': datetime.datetime.now().isoformat(),
            'question': question,
            'client_ip': client_ip,
            'client_hostname': client_hostname,
            'response_code': 200
        }
        with open('logs/requests_log.json', 'a') as log_file:
            log_file.write(json.dumps(log_data) + '\n')

        logger.send_log("New request: " + question, client_ip, client_hostname, r_code=200)
        
        # Mettre à jour la session
        session.modified = True  # Indiquer que la session a été modifiée

        return render_template('index.html', response=answer, form=form, clearform=ClearForm(),history=session['history'])

    else:
        logger.send_log("Request failed validation", client_ip, client_hostname, r_code=400)
        return render_template('index.html', form=form, clearform=ClearForm(), history=session['history'])

@app.route('/clear_history', methods=['POST'])
@limiter.limit("5 per minute")
def clear_history():
    clearform = ClearForm()
    if clearform.validate_on_submit():
        session.pop('history', None)
    return render_template('index.html', form=QuestionForm(), clearform=ClearForm(), history=None)


@app.route('/reports')
def reports():
    return render_template('reports.html')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
