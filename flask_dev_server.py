#!/usr/bin/env python3
"""
Simple Flask development server for Swedenborg Reader
Serves the API endpoint and static files
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
import sys

# Import functions from the API
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))
from index import search_texts, load_local_book

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains

@app.route('/api/index', methods=['POST'])
def api_post():
    try:
        payload = request.get_json()
        
        if not payload:
            return jsonify({"error": "Invalid JSON in request body"}), 400
        
        # Get the user's question/text from the frontend format
        user_text = payload.get("text", "")
        history = payload.get("history", [])
        book_context = payload.get("bookContext", None)
        
        if not user_text:
            return jsonify({"error": "Please provide 'text' field with your question"}), 400

        # Search for relevant passages
        matches = search_texts(user_text, book_context)
        
        # Generate a response based on the search results
        if matches:
            # Create a conversational response
            response_text = "I found some relevant passages for you:\n\n"
            
            for i, match in enumerate(matches[:3]):
                source = match.get('source', 'Unknown')
                title = match.get('title', '')
                text = match.get('text', '')
                
                response_text += f"**From {source}**"
                if title:
                    response_text += f" - {title}"
                response_text += f":\n{text}\n\n"
            
            response_text += "Would you like me to explain any of these passages or search for something else?"
        else:
            if book_context:
                book_title = book_context.get('title', 'the selected book')
                response_text = f"I couldn't find specific passages about '{user_text}' in {book_title}. Could you try rephrasing your question or ask about a different topic?"
            else:
                response_text = f"I couldn't find specific passages about '{user_text}' in Swedenborg's works. Could you try rephrasing your question or be more specific about what you'd like to learn?"

        response = {
            "responseText": response_text,
            "audioContent": None  # Could add TTS later
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"API Error: {e}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/index', methods=['GET'])
def api_get():
    response = {
        "status": "Swedenborg Reader API is running",
        "description": "This API accepts POST requests with JSON body containing 'text' field for questions about Swedenborg's works."
    }
    return jsonify(response)

@app.route('/api/index', methods=['OPTIONS'])
def api_options():
    return jsonify({}), 200

# Serve static files
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)

if __name__ == '__main__':
    print("Starting Flask development server...")
    print("This server handles both static files and API requests.")
    print("Visit http://localhost:5000 to test the application.")
    app.run(debug=True, host='0.0.0.0', port=5000)