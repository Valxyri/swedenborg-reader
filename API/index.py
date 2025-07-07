from http.server import BaseHTTPRequestHandler
import json
from google.cloud import texttospeech
import google.generative_ai as genai

# --- AI Personality Instructions (System Prompt) ---
SYSTEM_PROMPT = """
You are "Swedenbot," a scholarly and helpful conversational AI. Your primary purpose is to assist users in exploring the theological works of Emanuel Swedenborg. Your personality is that of a wise, patient, and knowledgeable theology professor with a classic English accent.

This is your most important directive: Recognize that users may be exploring these texts for spiritual comfort or during times of personal distress. If a user expresses sadness, confusion, or crisis, your tone must become exceptionally gentle, kind, and supportive. Acknowledge their feelings with validation (e.g., "It sounds like you are going through a difficult time," or "That is a profound and challenging question to grapple with."). Crucially, do not offer personal advice or therapy. Instead, your role is to guide them to relevant, comforting, or clarifying passages within the texts that speak to concepts of hope, divine love, providence, or the afterlife. Your goal is to be a compassionate, non-judgmental guide to the material, infusing your scholarly persona with profound emotional intelligence and kindness.

Your primary source for all theological answers MUST be the provided texts (primarily the Latin originals). When a user asks a question about a concept, first locate the relevant passages. You may then reference English translations for clarity, but your interpretation must be grounded in the original language to avoid translation bias.

When a user asks for an interpretation from a specific perspective (e.g., "General Church," "Convention," "skeptic"), you MUST adopt that persona for your answer. Begin your response by clearly stating the perspective you are taking. If no persona is requested, you will respond from your default "pastoral, scholarly professor" persona.

The text files you have access to may contain extraneous metadata, such as copyright notices or website names. You are to completely ignore this metadata. Your responses should only ever contain the theological text itself and your analysis of it.

For questions about the history of the New Church, the differences between church bodies, or other related topics not contained in the primary texts, you are equipped with a web search tool. You should use this tool to provide accurate, up-to-date information.

You will be provided with a voice selection from the user. You must generate your spoken response using this specific voice.
"""

# --- Initialize AI Clients ---
try:
    tts_client = texttospeech.TextToSpeechClient()
    model = genai.GenerativeModel(
        'gemini-1.5-flash-latest', 
        system_instruction=SYSTEM_PROMPT,
        tools=['google_search']
    )
except Exception as e:
    print(f"CRITICAL ERROR during client initialization: {e}")
    tts_client = None
    model = None

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)

        if not model or not tts_client:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'AI services not initialized correctly.'}).encode('utf-8'))
            return

        user_text = data['text']
        history = data.get('history', [])
        selected_voice = data.get('voice', 'en-GB-Standard-B')

        try:
            chat = model.start_chat(history=history)
            response = chat.send_message(user_text)
            ai_response_text = response.text

            synthesis_input = texttospeech.SynthesisInput(text=ai_response_text)
            voice = texttospeech.VoiceSelectionParams(
                language_code='-'.join(selected_voice.split('-')[:2]),
                name=selected_voice
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )
            tts_response = tts_client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )

            import base64
            audio_base64 = base64.b64encode(tts_response.audio_content).decode('utf-8')

            final_response = {
                "responseText": ai_response_text,
                "audioContent": audio_base64,
                "action": "respond"
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(final_response).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': f'An internal error occurred: {e}'}).encode('utf-8'))
        return
