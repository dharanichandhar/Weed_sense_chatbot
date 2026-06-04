
🌿 Weed Identification Assistant:
answerable → Facts are sufficient, generate response
needs_more → Gap identified, reformulate query and re-retrieve
irrelevant → Question is not weed-related, return a polite redirect
=======
# Weed Sense - AI Assistant for Farmers

An AI-powered chatbot that helps farmers identify and manage noxious weeds using RAG (Retrieval Augmented Generation).

## Features

- **Weed Identification** — Describe a weed and get the exact species with matching characteristics
- **Control Methods** — Mechanical, chemical, and biological control recommendations with timing
- **Growth Stage Guidance** — Specific seasons and growth stages for treatment
- **Chat History** — Maintains conversation context across queries
- **Suggestion Prompts** — Quick-start buttons for common questions

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, Vite, react-markdown |
| Backend | FastAPI, LangChain, LangGraph |
| LLM | OpenAI GPT-4o |
| Embeddings | OpenAI text-embedding-3-small |
| Vector DB | Chroma (persistent) |
| Knowledge Base | PDF (weed_dataset.pdf) |

## Project Structure

```
weed_sense_chatbot/
├── backend/
│   ├── main.py            # FastAPI server entry point
│   ├── rag_pipeline.py    # LangGraph RAG workflow
│   └── requirements.txt   # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.jsx        # Main chat UI component
│   │   ├── App.css        # Styles
│   │   ├── index.css      # Global styles
│   │   └── main.jsx       # React entry point
│   ├── package.json
│   └── vite.config.js
├── weed_dataset.pdf       # Weed knowledge base
└── .env                   # OpenAI API key (not tracked)
```

## Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` in the project root:
```
OPENAI_API_KEY=your_key_here
```

Run the server:
```bash
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

## Usage

1. Type a question about a weed (e.g., "What does Hoary Cress look like?") or click a suggestion button
2. The backend retrieves relevant facts from the weed database, evaluates if more info is needed, and returns a concise answer
3. Responses include species names, control methods, and timing where available

## Example Interactions

### Weed Identification
```
Q: What does Hoary Cress look like?
A: Species: Hoary Cress (Lepidium draba)
   • White flowers in dense flat-topped clusters
   • Grayish-green leaves covered in fine hairs
   • Grows 1-2 feet tall with spreading root system
   • Distinct from similar species by its perennial root system
```

### Control Methods
```
Q: How do I control Musk Thistle?
A: Species: Musk Thistle (Carduus nutans)
   Control Methods:
   • Mechanical — Mowing before flowering (early summer) or hand-pulling when soil is moist
   • Chemical — 2,4-D or dicamba applied at rosette stage (fall or early spring)
   • Biological — Weevil (Rhinocyllus conicus) larvae feed on developing seed heads
   Timing: Treat at rosette stage for best results; prevent seed set by mowing before bloom
```

### Q&A about Growth Stages
```
Q: What is the lifecycle of Musk Thistle?
A: Species: Musk Thistle (Carduus nutans)
   • Biennial lifecycle: germinates in year 1 (rosette), flowers in year 2
   • Rosette stage: fall through early spring
   • Bolting: late spring (April-May)
   • Flowering: June to August
   • Seed dispersal: late summer to fall
   Control: Best controlled at rosette stage in fall or early spring
```

### API Usage
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the lifecycle of Musk thistle?", "chat_history": []}'
```

## How It Works

The backend uses a LangGraph state machine with four nodes:

1. **Retrieve** — Searches Chroma vector store for relevant weed facts
2. **Evaluate** — Checks if gathered facts fully answer the question
3. **Reformulate** — If more facts are needed, generates a better search query and loops back to Retrieve (up to 2 retries)
4. **Respond** — Builds the final answer using GPT-4o with a weed-specific prompt template

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for LLM and embeddings |
>>>>>>> f0f48bb (update chatbot)
