from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from braintrust import init_logger, traced
from braintrust.integrations.langchain import BraintrustCallbackHandler , set_global_handler


from rag_pipeline import graph


app = FastAPI()

init_logger(project = "Weed Sense")
set_global_handler(BraintrustCallbackHandler())


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


@traced(name = "Weed Chat")
def run_pipeline(question: str , chat_history: list):
    initial_state = {
         "original_question": question,
        "current_query": question,
        "gathered_facts": [],
        "evaluation": None,
        "missing_info": None,
        "response": "",
        "chat_history": chat_history,
        "retry_count": 0
    }
    return graph.invoke(initial_state)


@app.get("/")
def home():
    return {
        "message": "Farmer Weed Chatbot API is running"
    }


@app.post("/chat")
def chat(request: ChatRequest):
   
    final_state = run_pipeline(request.question, request.chat_history)
    return {
        "answer": final_state["response"],
        "chat_history": final_state["chat_history"]
    }