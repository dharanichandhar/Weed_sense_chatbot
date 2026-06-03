🌿 Weed Identification Assistant
An AI-powered RAG (Retrieval-Augmented Generation) chatbot that helps farmers identify and manage noxious weeds. Supports both English and Tamil languages.

 Features

 Weed Identification — Species name, characteristics, and differentiation from similar plants
 Control Methods — Mechanical, chemical, and biological control with timing windows
 Adaptive Retrieval — Automatically re-queries if initial facts are insufficient
 Bilingual Support — Responds in Tamil or English based on the question language
 Conversation Memory — Maintains chat history across the session

 Tech Stack
Component           Technology  
LLM                 OpenAI gpt-4o
Embeddings          OpenAI text-embedding-3-small
Vector Store        ChromaDB 
Orchestration       LangGraph
PDF Loading         LangChainPyPDFLoader 
Frontend            React Vite
Backend             Python FastApi




How It Works — RAG Pipeline (rag_pipeline.py)
The pipeline uses a LangGraph StateGraph with 4 nodes:

START → retrieve → evaluate → respond → END
                       ↓
                  reformulate → retrieve (loop)
Pipeline Nodes

Node         Description               
retrieve     Fetches top-5 relevant chunks from ChromaDB using the current query
evaluate     LLM evaluates if gathered facts are sufficient (answerable / needs_more / irrelevant)
reformulate  If facts are insufficient, generates a new targeted search query
respond      Generates the final answer using the prompt template

Evaluation States

answerable → Facts are sufficient, generate response
needs_more → Gap identified, reformulate query and re-retrieve
irrelevant → Question is not weed-related, return a polite redirect