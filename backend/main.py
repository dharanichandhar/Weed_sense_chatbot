from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag_pipeline import graph


app = FastAPI(title="Farmer Weed Chatbot API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str
    chat_history: list = []


@app.get("/")
def home():
    return {
        "message": "Farmer Weed Chatbot API is running"
    }


@app.post("/chat")
def chat(request: ChatRequest):
    initial_state = {
        "original_question": request.question,
        "current_query": request.question,
        "gathered_facts": [],
        "evaluation": None,
        "missing_info": None,
        "response": "",
        "chat_history": request.chat_history,
        "retry_count": 0
    }

    final_state = graph.invoke(initial_state)

    return {
        "answer": final_state["response"],
        "chat_history": final_state["chat_history"]
    }