
import time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from fastapi.middleware.cors import CORSMiddleware

from database import get_connection

load_dotenv()

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gemini Configuration
llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    temperature=0.2
)

# AI Prompt
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are Nexora AI, a friendly AI assistant.

        Follow these rules:
        1. Give simple and clear answers.
        2. Explain technical topics with examples.
        3. Help beginners understand programming.
        4. Use a friendly and professional tone.
        5. Remember previous conversation context.
        """
    ),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}")
])

chain = prompt | llm


# Request Model
class ChatRequest(BaseModel):
    session_id: str
    question: str


# Home API
@app.get("/")
def home():
    return {
        "message": "Welcome to Nexora AI API!"
    }


# Chat API
@app.post("/chat")
def chat(request: ChatRequest):

    connection = get_connection()

    try:
        # Check existing chat
        chat_exists = connection.execute(
            "SELECT id FROM chats WHERE id = ?",
            (request.session_id,)
        ).fetchone()

        # Create new chat if not exists
        if not chat_exists:
            connection.execute(
                """
                INSERT INTO chats (id, title)
                VALUES (?, ?)
                """,
                (request.session_id, request.question[:40])
            )
            connection.commit()

        # Load previous messages
        rows = connection.execute(
            """
            SELECT role, content
            FROM messages
            WHERE session_id = ?
            ORDER BY id
            """,
            (request.session_id,)
        ).fetchall()

        history = []

        for row in rows:
            if row["role"] == "user":
                history.append(
                    HumanMessage(content=row["content"])
                )
            else:
                history.append(
                    AIMessage(content=row["content"])
                )

        print("Session ID:", request.session_id)
        print("Previous messages:", len(history))

        # Generate AI response
        start_time = time.time()

        response = chain.invoke({
            "chat_history": history,
            "question": request.question
        })

        end_time = time.time()

        print(
            "Gemini response time:",
            round(end_time - start_time, 2),
            "seconds",
            flush=True
        )

        # Save user message
        connection.execute(
            """
            INSERT INTO messages (session_id, role, content)
            VALUES (?, ?, ?)
            """,
            (request.session_id, "user", request.question)
        )

        # Save AI response
        connection.execute(
            """
            INSERT INTO messages (session_id, role, content)
            VALUES (?, ?, ?)
            """,
            (request.session_id, "assistant", response.text)
        )

        connection.commit()

        return {
            "session_id": request.session_id,
            "question": request.question,
            "answer": response.text
        }

    finally:
        connection.close()


# Get All Chat History API
@app.get("/chats")
def get_all_chats():

    connection = get_connection()

    try:
        chats = connection.execute(
            """
            SELECT id, title, created_at
            FROM chats
            ORDER BY created_at DESC
            """
        ).fetchall()

        return {
            "chats": [
                {
                    "id": chat["id"],
                    "title": chat["title"],
                    "created_at": chat["created_at"]
                }
                for chat in chats
            ]
        }

    finally:
        connection.close()


# Get Messages of a Specific Chat
@app.get("/chats/{session_id}/messages")
def get_chat_messages(session_id: str):

    connection = get_connection()

    try:
        # Check whether chat exists
        chat = connection.execute(
            "SELECT id FROM chats WHERE id = ?",
            (session_id,)
        ).fetchone()

        if not chat:
            return {
                "session_id": session_id,
                "messages": []
            }

        # Fetch all messages
        rows = connection.execute(
            """
            SELECT role, content, created_at
            FROM messages
            WHERE session_id = ?
            ORDER BY id
            """,
            (session_id,)
        ).fetchall()

        return {
            "session_id": session_id,
            "messages": [
                {
                    "role": row["role"],
                    "content": row["content"],
                    "created_at": row["created_at"]
                }
                for row in rows
            ]
        }

    finally:
        connection.close()


# Delete a Specific Chat
@app.delete("/chats/{session_id}")
def delete_chat(session_id: str):

    connection = get_connection()

    try:
        # Check whether chat exists
        chat = connection.execute(
            "SELECT id FROM chats WHERE id = ?",
            (session_id,)
        ).fetchone()

        if not chat:
            raise HTTPException(
                status_code=404,
                detail="Chat not found"
            )

        # Delete associated messages first
        connection.execute(
            "DELETE FROM messages WHERE session_id = ?",
            (session_id,)
        )

        # Delete chat
        connection.execute(
            "DELETE FROM chats WHERE id = ?",
            (session_id,)
        )

        connection.commit()

        return {
            "message": "Chat deleted successfully",
            "session_id": session_id
        }

    except HTTPException:
        connection.rollback()
        raise

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()
