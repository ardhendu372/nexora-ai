# Nexora AI

Nexora AI is a chatbot application that allows users to interact with an AI assistant and maintain separate conversations.

I built this project using React for the frontend and FastAPI for the backend. I integrated Google Gemini using LangChain to generate AI responses.

## Features

- Chat with an AI assistant.
- Start a new conversation.
- Maintain separate chat sessions.
- Save chat history in SQLite.
- Open previous conversations.
- Delete conversations.
- Show loading indicators while waiting for responses.
- Handle API errors.

## Technologies Used

- React.js and Vite
- Python and FastAPI
- LangChain
- Google Gemini API
- SQLite
- CSS

## Project Setup

### Backend

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_api_key
```

Start the backend:

```bash
uvicorn api:app --reload
```

### Frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the frontend at `http://localhost:5173`.

Backend API documentation: `http://127.0.0.1:8000/docs`

## What I Learned

While building Nexora AI, I learned how to connect a React frontend with a FastAPI backend, integrate an LLM using LangChain, manage chat sessions, and store conversation history using SQLite.

## Developer

Ardhendu Nayak

GitHub: https://github.com/ardhendu372