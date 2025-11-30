# Moroccan Hospitals Information Assistant

A multilingual chatbot (FR/AR/EN) that provides information about hospitals in Morocco using Gemini API and ChromaDB for vector search.

## Features

- 🌍 Multilingual support (French, Arabic, English)
- 🤖 Powered by Google Gemini API
- 🔍 Vector search using ChromaDB
- 💬 Interactive chat interface

## Project Structure

```
CHATHOPOA/
├── backend2/          # Main backend (FastAPI + ChromaDB)
│   ├── main.py       # FastAPI server
│   ├── ingest.py     # Data ingestion script
│   └── requirements.txt
├── backend/          # Legacy backend
└── project/          # Frontend (React + TypeScript)
```

## Setup

### Backend

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
cd backend2
pip install -r requirements.txt
```

3. Set environment variables:
```bash
# Create .env file
GEMINI_API_KEY=your_api_key_here
```

4. Ingest data:
```bash
python ingest.py
```

5. Run server:
```bash
python main.py
```

### Frontend

```bash
cd project
npm install
npm run dev
```

## License

MIT

