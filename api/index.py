from http.server import BaseHTTPRequestHandler
import json
import os
import base64

# Gracefully handle Google AI dependencies
try:
    import google.generativeai as genai
    GOOGLE_AI_AVAILABLE = True
except ImportError:
    GOOGLE_AI_AVAILABLE = False
    genai = None

try:
    from google.cloud import texttospeech
    GOOGLE_TTS_AVAILABLE = True
except ImportError:
    GOOGLE_TTS_AVAILABLE = False
    texttospeech = None

# Configure Google AI
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if GEMINI_API_KEY and GOOGLE_AI_AVAILABLE:
    genai.configure(api_key=GEMINI_API_KEY)

def get_gemini_response(text, history=None, book_context=None):
    """Get response from Google Gemini AI"""
    try:
        if not GEMINI_API_KEY or not GOOGLE_AI_AVAILABLE:
            return get_fallback_response(text, book_context)
        
        model = genai.GenerativeModel('gemini-pro')
        
        # Build context for the AI
        context_parts = []
        
        # Add system context about being a Swedenborg expert
        system_context = """You are Swedenbot, an expert assistant on the works of Emanuel Swedenborg. 
        You help users explore and understand his theological and philosophical writings. 
        Respond in a helpful, knowledgeable manner, drawing from Swedenborg's teachings when relevant.
        Keep responses conversational and engaging."""
        context_parts.append(system_context)
        
        # Add book context if available
        if book_context:
            book_info = f"""
            The user is currently exploring the book: "{book_context.get('title', 'Unknown')}"
            
            Here is some content from this book to help answer questions:
            {json.dumps(book_context, indent=2)[:2000]}...
            """
            context_parts.append(book_info)
        
        # Add conversation history
        if history:
            for msg in history[-5:]:  # Last 5 messages for context
                role = msg.get('role', '')
                parts = msg.get('parts', [])
                if parts and len(parts) > 0:
                    message_text = parts[0].get('text', '')
                    if role == 'user':
                        context_parts.append(f"User previously asked: {message_text}")
                    elif role == 'model':
                        context_parts.append(f"You previously responded: {message_text}")
        
        # Combine context and current question
        full_prompt = "\n\n".join(context_parts) + f"\n\nUser's current question: {text}"
        
        response = model.generate_content(full_prompt)
        return response.text
        
    except Exception as e:
        print(f"Error with Gemini API: {e}")
        return get_fallback_response(text, book_context)

def get_fallback_response(text, book_context=None):
    """Provide basic responses when AI service is not available"""
    text_lower = text.lower()
    
    # Basic responses about common Swedenborg topics
    if any(word in text_lower for word in ['heaven', 'paradise', 'afterlife']):
        return """According to Swedenborg, heaven is not a place but a state of being. In his work "Heaven and Hell," he describes heaven as existing wherever people live in love and wisdom. Heaven consists of countless communities of angels, each reflecting different aspects of divine love and truth. The angels there continue to grow in wisdom and love throughout eternity."""
    
    elif any(word in text_lower for word in ['hell', 'evil', 'punishment']) and 'hello' not in text_lower:
        return """In Swedenborg's theology, hell is not a place of eternal punishment imposed by God, but rather a state chosen by those who prefer selfishness and falsity over love and truth. Hell exists because some spirits prefer darkness to light. However, even in hell, divine mercy continues to flow, and the spirits there are allowed to live according to their chosen loves, though in a more limited way."""
    
    elif any(word in text_lower for word in ['love', 'charity', 'good']):
        return """For Swedenborg, love is the very essence of life and the primary attribute of the Divine. He teaches that there are three universal loves: love of God, love of the neighbor (charity), and love of self in proper order. True love always seeks the good of others and finds joy in their happiness. Love and wisdom together make up the divine nature."""
    
    elif any(word in text_lower for word in ['wisdom', 'truth', 'understanding']):
        return """Wisdom, according to Swedenborg, is divine truth flowing into human understanding. In his work "Divine Love and Wisdom," he explains that wisdom without love is cold and lifeless, while love without wisdom can be misguided. True wisdom comes from the marriage of divine love and truth, and it manifests as practical understanding that leads to a life of service."""
    
    elif any(word in text_lower for word in ['marriage', 'conjugial', 'relationship']):
        return """Swedenborg's "Conjugial Love" presents a beautiful vision of marriage as a spiritual union that can continue into eternity. He teaches that true marriage love unites not just two bodies, but two minds and spirits. When partners love what the other understands and understand what the other loves, they become "one flesh" in the deepest spiritual sense."""
    
    elif any(word in text_lower for word in ['bible', 'scripture', 'word']):
        return """Swedenborg viewed the Bible as the Divine Word, containing both literal and spiritual meanings. He developed a comprehensive system of biblical interpretation called "correspondences," showing how natural things in the Bible correspond to spiritual realities. His extensive biblical commentaries, particularly "Arcana Coelestia," reveal the inner spiritual sense of Genesis and Exodus."""
    
    elif any(word in text_lower for word in ['church', 'religion', 'christianity']):
        return """Swedenborg speaks of the "New Church" not as a denomination, but as a new dispensation of Christianity focused on the internal spiritual meaning of faith. He emphasized that the essence of religion is living according to divine truths, not just believing them. The church exists wherever people acknowledge the Lord and live according to His teachings."""
    
    elif book_context:
        title = book_context.get('title', 'this work')
        return f"""You've selected "{title}" - one of Swedenborg's important works. I'd be happy to help you explore its contents and teachings. What specific aspect of this work interests you? You can ask about particular concepts, chapters, or how the teachings relate to daily life."""
    
    else:
        return """Hello! I'm Swedenbot, here to help you explore the works of Emanuel Swedenborg. You can ask me about his teachings on heaven and hell, love and wisdom, marriage, biblical interpretation, or any other topics from his extensive writings. I can also help you navigate through his various works. What would you like to learn about?"""

def generate_audio(text):
    """Generate audio using Google Text-to-Speech"""
    try:
        if not GOOGLE_TTS_AVAILABLE:
            return None
            
        # Initialize the Text-to-Speech client
        client = texttospeech.TextToSpeechClient()
        
        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        # Build the voice request
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Standard-J",  # A pleasant male voice
            ssml_gender=texttospeech.SsmlVoiceGender.MALE
        )
        
        # Select the type of audio file you want returned
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        
        # Perform the text-to-speech request
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        # Return base64 encoded audio
        return base64.b64encode(response.audio_content).decode('utf-8')
        
    except Exception as e:
        print(f"Error generating audio: {e}")
        return None

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Set CORS headers
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        
        length = int(self.headers.get('content-length', 0))
        body = self.rfile.read(length)
        
        try:
            payload = json.loads(body)
        except Exception:
            response = {"error": "Invalid JSON"}
            self.wfile.write(json.dumps(response).encode())
            return

        # Extract data from frontend payload
        text = payload.get("text", "")
        history = payload.get("history", [])
        book_context = payload.get("bookContext")
        
        if not text.strip():
            response = {"error": "Please provide a text message"}
            self.wfile.write(json.dumps(response).encode())
            return

        # Get AI response
        ai_response = get_gemini_response(text, history, book_context)
        
        # Prepare response in format expected by frontend
        response_data = {
            "responseText": ai_response
        }
        
        # Add audio if available (and if text is not too long)
        if len(ai_response) < 500:  # Only generate audio for shorter responses
            audio_content = generate_audio(ai_response)
            if audio_content:
                response_data["audioContent"] = audio_content
        
        self.wfile.write(json.dumps(response_data).encode())

    def do_OPTIONS(self):
        # Handle preflight requests
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(b"Swedenbot API is running. Send POST requests with JSON body containing 'text', 'history', and 'bookContext' fields.")
