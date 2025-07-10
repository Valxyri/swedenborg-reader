from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.parse

def get_data_base_url():
    """Get the base URL for data files"""
    # In production, this will be the Vercel deployment URL
    # For local development, we could use a localhost URL
    return os.environ.get('VERCEL_URL', 'https://swedenborg-reader.vercel.app') + '/data/'

def get_local_book_files():
    """Get list of all JSON book files"""
    # Since we can't scan the directory remotely, we'll maintain a static list
    # of available book files. This could also be loaded from a manifest file.
    book_files = [
        "9q_latin.json", "ac_latin.json", "ae_latin.json", "ang_latin.json", 
        "ar_latin.json", "ath_latin.json", "be_latin.json", "books.json",
        "bsn_vol1_191113.json", "bsn_vol2_191113.json", "calv_latin.json",
        "canons_latin.json", "cg_latin.json", "cl_latin.json", "conc_latin.json",
        "cor_latin.json", "dac_latin.json", "dlw_latin.json", "dp_latin.json",
        "earths_latin.json", "em_latin.json", "hd_latin.json", "hh_latin.json",
        "inv_latin.json", "ise_latin.json", "lj_latin.json", "ncecorrespondences_portable.json",
        "nce_heavenandhell_portable.json", "nce_lastjudgment.json", "nce_secretsofheaven1_portable.json",
        "nce_secretsofheaven2_portable.json", "nce_secretsofheaven3_portable.json",
        "nce_surveysoulbodyinteraction_portable.json", "nce_thelord_portable.json",
        "nce_truechristianity1_portable.json", "nce_truechristianity2_portable.json",
        "pp_latin.json", "sc_latin.json", "se_latin.json", "sf_compendium_warren.json",
        "sf_epicoftheafterlife_lagercrantz.json", "sf_scientistexploresspirit.json",
        "sf_skinner_roses.json", "swedenborg_foundation_apocalypse_explained_01.json",
        "swedenborg_foundation_apocalypse_explained_02.json", "swedenborg_foundation_apocalypse_explained_03.json",
        "swedenborg_foundation_apocalypse_explained_04.json", "swedenborg_foundation_apocalypse_explained_05.json",
        "swedenborg_foundation_apocalypse_explained_06.json", "swedenborg_foundation_apocalypse_revealed_01.json",
        "swedenborg_foundation_apocalypse_revealed_02.json", "swedenborg_foundation_arcana_coelestia_01.json",
        "swedenborg_foundation_arcana_coelestia_02.json", "swedenborg_foundation_arcana_coelestia_03.json",
        "swedenborg_foundation_arcana_coelestia_04.json", "swedenborg_foundation_arcana_coelestia_05.json",
        "swedenborg_foundation_arcana_coelestia_06.json", "swedenborg_foundation_arcana_coelestia_07.json",
        "swedenborg_foundation_arcana_coelestia_08.json", "swedenborg_foundation_arcana_coelestia_09.json",
        "swedenborg_foundation_arcana_coelestia_10.json", "swedenborg_foundation_arcana_coelestia_11.json",
        "swedenborg_foundation_arcana_coelestia_12.json", "swedenborg_foundation_conjugial_love.json",
        "swedenborg_foundation_divine_love_and_wisdom.json", "swedenborg_foundation_divine_providence.json",
        "swedenborg_foundation_true_christian_religion_01.json", "swedenborg_foundation_true_christian_religion_02.json",
        "swedenborg_foundation_true_christian_religion_03.json", "tcr_latin.json", "wh_latin.json"
    ]
    return book_files

def load_remote_book(filename):
    """Load a book file from the remote data URL"""
    base_url = get_data_base_url()
    file_url = base_url + urllib.parse.quote(filename)
    
    try:
        with urllib.request.urlopen(file_url) as response:
            data = response.read()
            return json.loads(data.decode('utf-8'))
    except Exception as e:
        print(f"Error loading {filename} from {file_url}: {e}")
        return None

def search_in_book_content(content, search_terms):
    """Search for terms in book content structure"""
    results = []
    
    if not content:
        return results
    
    # Handle different book content structures
    sections = content.get('sections', [])
    if not sections and isinstance(content, list):
        sections = content
    
    for section in sections:
        if isinstance(section, dict):
            # Check title
            title = section.get('title', '')
            text_content = section.get('text', '')
            
            # Combine title and text for searching
            combined_text = f"{title} {text_content}".lower()
            
            # Check if any search term is found
            if any(term in combined_text for term in search_terms):
                results.append({
                    "title": title,
                    "text": text_content[:500] + "..." if len(text_content) > 500 else text_content,
                    "relevance": sum(1 for term in search_terms if term in combined_text)
                })
        elif isinstance(section, str):
            # Simple string content
            if any(term in section.lower() for term in search_terms):
                results.append({
                    "title": "Text Section",
                    "text": section[:500] + "..." if len(section) > 500 else section,
                    "relevance": sum(1 for term in search_terms if term in section.lower())
                })
    
    # Sort by relevance
    results.sort(key=lambda x: x['relevance'], reverse=True)
    return results[:3]  # Return top 3 most relevant

def search_texts(question, book_context=None):
    """Search through available texts based on question"""
    search_terms = [term.lower().strip() for term in question.lower().split() if len(term.strip()) > 2]
    
    if not search_terms:
        return []
    
    all_results = []
    
    # If we have a specific book context, search only in that book
    if book_context:
        results = search_in_book_content(book_context, search_terms)
        for result in results:
            result['source'] = book_context.get('title', 'Selected Book')
        all_results.extend(results)
    else:
        # Search through a selection of key books
        key_books = [
            "nce_heavenandhell_portable.json",
            "swedenborg_foundation_divine_love_and_wisdom.json",
            "swedenborg_foundation_true_christian_religion_01.json",
            "nce_thelord_portable.json"
        ]
        
        for filename in key_books:
            book_data = load_remote_book(filename)
            if book_data:
                results = search_in_book_content(book_data, search_terms)
                for result in results:
                    result['source'] = book_data.get('title', filename.replace('.json', ''))
                all_results.extend(results)
    
    # Sort all results by relevance and return top results
    all_results.sort(key=lambda x: x['relevance'], reverse=True)
    return all_results[:5]

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('content-length', 0))
        body = self.rfile.read(length)
        try:
            payload = json.loads(body)
        except Exception:
            self.send_response(400)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = {"error": "Invalid JSON in request body"}
            self.wfile.write(json.dumps(response).encode())
            return

        # Get the user's question/text from the frontend format
        user_text = payload.get("text", "")
        history = payload.get("history", [])
        book_context = payload.get("bookContext", None)
        
        if not user_text:
            self.send_response(400)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = {"error": "Please provide 'text' field with your question"}
            self.wfile.write(json.dumps(response).encode())
            return

        try:
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

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()
            
            response = {
                "responseText": response_text,
                "audioContent": None  # Could add TTS later
            }
            
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = {"error": f"Server error: {str(e)}"}
            self.wfile.write(json.dumps(response).encode())

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        response = {
            "status": "Swedenborg Reader API is running",
            "description": "This API accepts POST requests with JSON body containing 'text' field for questions about Swedenborg's works.",
            "data_source": "remote_files"
        }
        self.wfile.write(json.dumps(response, indent=2).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
