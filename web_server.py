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
from classes.elastic_indexer import ElasticIndexer
from classes.prompter import Prompter

app = Flask(__name__)

app.config['SECRET_KEY'] = 'docdoc'

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

csrf = CSRFProtect(app)

logger = Logger(filename="logs_webserver", write_file=True)

prompter = Prompter(model="gemma2")

@app.route('/')
def home():
    form = QuestionForm()
    clearform = ClearForm()
    indexer = ElasticIndexer() 
    indices = indexer.get_all_indices() 
    return render_template('index.html', form=form, clearform=clearform, indices=indices)


@app.route('/ask', methods=['POST'])
@limiter.limit("5 per minute")
def ask_question():
    client_ip = request.remote_addr

    indexer = ElasticIndexer(index_name="") 
    indices = indexer.get_all_indices()

    try:
        client_hostname = socket.gethostbyaddr(client_ip)[0]
    except socket.herror:
        client_hostname = "Hostname unavailable"

    form = QuestionForm()

    # Initialize session history if it doesn't exist
    if 'history' not in session:
        session['history'] = []

    if form.validate_on_submit():
        question = form.question.data
        selected_index = request.form.get('selected_index', 'pdf_chunks')  # Default index

        # Use the selected index for user_query and query_handler
        user_query = UserQuery(index_name=selected_index)
        query_handler = QueryHandler(index_name=selected_index)

        # Query and process the response
        response = user_query.query(question, method="rrf")
        results = user_query.get_metadata_as_list(response)
        print(results)
        reranked_results = query_handler.rerank_results(question=question, results_as_list=results)

        prompt = prompter.generate_prompt(reranked_results, question)

        answer = prompter.get_response_from_ollama(prompt)

        # Add the question and answer to session history
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

        logger.send_log("New request: " + question, client_ip, client_hostname, r_code=200, answer=answer)
        
        # Update the session
        session.modified = True  # Indicate that the session has been modified

        return render_template('index.html', response=answer, form=form, clearform=ClearForm(), indices=indices, history=session['history'])

    else:
        logger.send_log("Request failed validation", client_ip, client_hostname, r_code=400)
        return render_template('index.html', form=form, clearform=ClearForm(), indices=indices, history=session['history'])


@app.route('/clear_history', methods=['POST'])
@limiter.limit("5 per minute")
def clear_history():
    clearform = ClearForm()
    indexer = ElasticIndexer() 
    indices = indexer.get_all_indices()
    if clearform.validate_on_submit():
        session.pop('history', None)
    return render_template('index.html', form=QuestionForm(), clearform=ClearForm(), indices=indices, history=None)


@app.route('/reports')
def reports():
    return render_template('reports.html')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
