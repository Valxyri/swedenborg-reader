from http.server import BaseHTTPRequestHandler
import json
import requests
import urllib.parse
import os

DATA_FILES = [
    # List your JSON filenames here, or automate fetching a list from your repo
    "heaven-and-hell.json",
    "divine-love-and-wisdom.json",
    # ... add more
]

def fetch_text(filename):
    url = f"https://raw.githubusercontent.com/Valxyri/swedenborg-reader-data/main/data/{filename}"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()

def search_texts(question):
    # Very simple search: looks for the question word(s) in the text
    results = []
    qwords = question.lower().split()
    for fn in DATA_FILES:
        try:
            data = fetch_text(fn)
            # Assume each file is a list of paragraphs or sections
            for para in data:
                text = para if isinstance(para, str) else json.dumps(para)
                if any(word in text.lower() for word in qwords):
                    results.append({"file": fn, "text": text})
        except Exception as e:
            continue
    return results

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('content-length', 0))
        body = self.rfile.read(length)
        try:
            payload = json.loads(body)
        except Exception:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid JSON")
            return

        question = payload.get("question", "")
        if not question:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Please send a {'question': 'your question'} in the request body.")
            return

        matches = search_texts(question)
        if matches:
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            # Return the first 1-3 matches for brevity
            response = {"answers": matches[:3]}
            self.wfile.write(json.dumps(response, indent=2).encode())
        else:
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = {"answers": ["Sorry, no relevant passages found."]}
            self.wfile.write(json.dumps(response, indent=2).encode())

    def do_GET(self):
        # Optional: add a GET endpoint for status or usage instructions
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"This API accepts POST requests with a JSON body like {'question': 'What is heaven?'}. It will reply with relevant passages from Swedenborg's works.")
