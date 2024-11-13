import requests
import json

class Prompter :

    def __init__(self, model="llama3.2") :

        self.model = model

    def generate_prompt(self, context_chunks, question):
        """
        Constructs the prompt for Ollama with the context and question.
        """
        context_chunks = context_chunks[:5]

        context_text = ""
        for chunk in context_chunks:
            metadata = (
                f"Metadata:\n"
                f"  - Title: {chunk['Title']}\n"
                f"  - Path: {chunk['Path']}\n"
                f"  - File Name: {chunk['File Name']}\n"
                f"  - Chunk ID: {chunk['Chunk ID']}\n"
                f"  - Timestamp: {chunk['Timestamp']}\n"
            )
            chunk_text = f"Chunk Text:\n{chunk['Chunk Text']}\n"
            context_text += f"{metadata}\n{chunk_text}\n\n" 

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


    def get_response_from_ollama(self, prompt):
        """
        Sends the prompt to the Ollama server and retrieves the response.
        """
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": self.model,
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
                    print("Processing is not yet complete.")
                else:
                    return api_response 
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON response: {e}")
        else:
            return("Error:", response.text)