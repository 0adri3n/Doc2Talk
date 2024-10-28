import pandas as pd
import matplotlib.pyplot as plt
import json
import re
from collections import Counter

def clean_text(text):
    # Convertir le texte en minuscules et retirer la ponctuation
    text = text.lower()  # Convertir en minuscules
    text = re.sub(r'[^\w\s]', '', text)  # Retirer la ponctuation
    return text

def analyze_and_plot_data():
    # Lire le fichier JSON
    try:
        data = pd.read_json('logs/requests_log.json', lines=True)
    except ValueError as e:
        print("Erreur lors de la lecture du fichier JSON :", e)
        return

    # Analyser les mots-clés dans les questions
    # Nettoyer et séparer les mots
    all_keywords = []
    for question in data['question']:
        cleaned_question = clean_text(question)
        words = cleaned_question.split()
        all_keywords.extend(words)  # Ajouter les mots à la liste

    # Compter les mots
    keyword_counts = Counter(all_keywords)

    # Convertir en DataFrame pour faciliter le traîtement
    keyword_counts_df = pd.DataFrame(keyword_counts.items(), columns=['keyword', 'count'])
    keyword_counts_df = keyword_counts_df.sort_values(by='count', ascending=False)


    # Compter les requêtes par IP
    ip_counts = data['client_ip'].value_counts()

    # Graphique des mots-clés
    plt.figure(figsize=(12, 6))
    keyword_counts_df.head(10).set_index('keyword')['count'].plot(kind='bar', color='skyblue')
    plt.title('Top 10 des mots-clés dans les questions')
    plt.xlabel('Mots-clés')
    plt.ylabel('Nombre de requêtes')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('static/data/img/keyword_report.png')  # Sauvegarde du graphique

    # Graphique des requêtes par IP
    plt.figure(figsize=(12, 6))
    ip_counts.head(10).plot(kind='bar', color='salmon')
    plt.title('Top 10 des adresses IP')
    plt.xlabel('IP')
    plt.ylabel('Nombre de requêtes')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('static/data/img/ip_report.png')  # Sauvegarde du graphique

if __name__ == "__main__":
    analyze_and_plot_data()
