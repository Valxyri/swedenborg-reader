# Swedenborg Reader

A web application for exploring the works of Emanuel Swedenborg through an interactive chat interface and digital library.

## Features

- **Interactive Chat**: Ask questions and receive relevant passages from Swedenborg's works
- **Digital Library**: Browse books by category (New Century Edition, Standard Edition, Latin Edition, Swedenborgiana)
- **Book-Specific Context**: Select a specific book to focus your questions within that work
- **Search Functionality**: Text-based search across multiple works simultaneously

## Local Development

### Problem & Solution

The application was originally designed to run on Vercel with serverless functions, but when running locally with `python3 -m http.server`, users encountered the error "Sorry, I'm having trouble connecting to the AI brain right now" because the simple HTTP server doesn't support POST requests to the API endpoint.

**Solution**: Use the Flask development server for local testing.

### Running Locally

1. **Install Dependencies**:
   ```bash
   pip install flask flask-cors
   ```

2. **Generate Books Index** (if needed):
   ```bash
   cd data
   python3 generate_books_json.py
   ```

3. **Start the Development Server**:
   ```bash
   python3 flask_dev_server.py
   ```

4. **Open Your Browser**:
   Visit `http://localhost:5000`

The Flask development server handles both:
- Static file serving (HTML, CSS, images, data files)
- API endpoint `/api/index` for chat functionality

### Files Added for Local Development

- `flask_dev_server.py` - Flask-based development server (recommended)
- `dev_server.py` - Alternative HTTP server implementation

## Project Structure

```
├── index.html              # Main web application
├── api/
│   └── index.py            # Vercel serverless function for API
├── data/
│   ├── *.json             # Book content files
│   ├── books.json         # Generated book index
│   └── generate_books_json.py
├── flask_dev_server.py    # Local development server
├── requirements.txt       # Python dependencies
└── vercel.json           # Vercel deployment configuration
```

## How It Works

1. **Frontend** (`index.html`): Single-page application with chat interface and library browser
2. **Backend** (`api/index.py`): Search functionality that finds relevant passages based on user queries
3. **Data** (`data/*.json`): JSON files containing the full text of Swedenborg's works
4. **Search Algorithm**: Text-based matching that ranks results by relevance

## Deployment

The application is designed to run on Vercel:
- Static files are served directly
- `api/index.py` runs as a serverless function
- No additional configuration needed for production deployment

## Screenshot

![Working Swedenbot Application](https://github.com/user-attachments/assets/cfd3d18d-f84b-4888-8440-5fd0fdeb91f4)

The application successfully responds to questions like "What is heaven like?" and "Tell me about angels" with relevant passages from Swedenborg's works, particularly from "Heaven and Hell" and other theological texts.