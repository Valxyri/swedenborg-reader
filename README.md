# Swedenborg Reader - Swedenbot Chatbot

An interactive chatbot for exploring the works of Emanuel Swedenborg. Features an intelligent AI assistant that can discuss Swedenborg's theological and philosophical writings.

## Features

- 🤖 **AI-Powered Chatbot**: Uses Google Gemini AI for intelligent responses about Swedenborg's works
- 📚 **Library Browser**: Browse and explore different editions of Swedenborg's writings  
- 🎯 **Context-Aware**: Maintains conversation history and book context for better responses
- 🔊 **Text-to-Speech**: Audio responses when Google Cloud TTS is configured
- 🎨 **Beautiful UI**: Elegant interface with period-appropriate fonts and styling
- 🛡️ **Fallback System**: Comprehensive responses even without AI services configured

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/Valxyri/swedenborg-reader.git
   cd swedenborg-reader
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run locally** (for development)
   ```bash
   python -m http.server 8080
   ```
   Open http://localhost:8080 in your browser.

## Configuration

### Google AI Integration (Optional)

For enhanced AI responses, set up a Google Gemini API key:

1. Get an API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Set the environment variable:
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```

### Google Cloud Text-to-Speech (Optional)

For audio responses:
1. Set up a Google Cloud project
2. Enable the Text-to-Speech API
3. Configure authentication (service account key or default credentials)

## Deployment

This app is designed to work with Vercel's serverless functions:

1. **Deploy to Vercel**
   ```bash
   vercel deploy
   ```

2. **Set Environment Variables** in your Vercel dashboard:
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - `GOOGLE_APPLICATION_CREDENTIALS`: Path to your Google Cloud service account key (for TTS)

## API Usage

The chatbot API accepts POST requests to `/api/index`:

```javascript
fetch('/api/index', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: "What is heaven like?",
    history: [], // Previous conversation messages
    bookContext: null // Current book data if browsing
  })
})
```

Response format:
```json
{
  "responseText": "According to Swedenborg, heaven is...",
  "audioContent": "base64-encoded-mp3-data" // Optional
}
```

## Fallback Mode

Without AI services configured, Swedenbot provides intelligent pre-written responses about:
- Heaven and Hell
- Love and Wisdom  
- Marriage (Conjugial Love)
- Biblical interpretation
- The New Church
- And other core Swedenborg topics

## Development

### File Structure
```
├── index.html          # Main frontend application
├── api/
│   └── index.py       # Serverless API function
├── books.json         # Library catalog
├── data/              # Book content files
├── requirements.txt   # Python dependencies
└── vercel.json       # Vercel configuration
```

### Testing

Run the comprehensive test suite:
```bash
python test_api.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.