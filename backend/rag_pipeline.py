from typing import TypedDict, List, Literal
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import PromptTemplate
from langgraph.graph import START, END, StateGraph


BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

PDF_PATH = BASE_DIR / "weed_dataset.pdf"

loader = PyPDFLoader(str(PDF_PATH))
pages = loader.load()
print(f"Total pages: {len(pages)}")


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
)

chunks = text_splitter.split_documents(pages)
print(f"Total chunks: {len(chunks)}")


embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

vector_store = Chroma(
    collection_name="weed_management",
    embedding_function=embeddings,
)

existing = vector_store.get()

if len(existing["ids"]) == 0:
    vector_store.add_documents(documents=chunks)
else:
    print("Already exists, skipping!")

retriever = vector_store.as_retriever(search_kwargs={"k": 3})


llm = ChatOpenAI(model="gpt-4o")


weed_prompt_template = """
You are an expert agricultural assistant helping 
farmers identify and manage noxious weeds.

Previous Conversation:
{chat_history}

Instructions:
- Answer ONLY using the verified facts provided
- If answer not in facts say 
  "I don't have information about that"
- Keep response SHORT and CONCISE
- Maximum 5 bullet points
- For weed identification:
  * Mention exact species name
  * List matching characteristics
  * Differentiate from similar species
- For control methods:
  * List ALL methods: mechanical, chemical, biological
  * Include specific timing windows
  * Mention growth stages
- For timing questions:
  * Be specific about seasons and growth stages
- Be clear and simple for farmers to understand
- Structure response like this:
  * Species/Issue: (if identification)
  * Control Methods: (bullet points)
  * Timing: (if available)

Verified Facts:
{facts}

Farmer Question: {question}

Answer:"""

weed_prompt = PromptTemplate.from_template(weed_prompt_template)
weed_chain = weed_prompt | llm


class WeedState(TypedDict):
    original_question: str
    current_query: str
    gathered_facts: List[str]
    evaluation: str | None
    missing_info: str | None
    response: str
    chat_history: List
    retry_count: int


class Evaluation(BaseModel):
    status: Literal["answerable", "needs_more", "irrelevant"] = Field(
        description=(
            "'answerable' if facts fully answer the question, "
            "'needs_more' if specific gap remains, "
            "'irrelevant' if question is not about weeds"
        )
    )
    reasoning: str = Field(
        description="Brief explanation of what we know and what's missing"
    )
    missing_piece: str = Field(
        default="",
        description="If needs_more: describe the specific information gap"
    )


class Reformulation(BaseModel):
    new_query: str = Field(
        description="A specific search query to find the missing information."
    )
    rationale: str = Field(
        description="Why this query should fill the gap."
    )


def retrieve_facts(state: WeedState):
    """Search the knowledge base for facts relevant to the query"""

    query = state["current_query"]
    new_facts = state.get("gathered_facts", []).copy()

    docs = retriever.invoke(query)

    for doc in docs:
        if doc.page_content not in new_facts:
            new_facts.append(doc.page_content)

    return {
        "gathered_facts": new_facts
    }


def evaluate(state: WeedState):
    question = state["original_question"]
    gathered = state.get("gathered_facts", [])

    facts_str = "\n".join(f"- {fact}" for fact in gathered) if gathered else "(none)"

    eval_llm = llm.with_structured_output(Evaluation)

    result = eval_llm.invoke([
        SystemMessage(content=(
            "You are an expert evaluator for agricultural weed management. "
            "Given a farmer's question and gathered facts, "
            "determine if the facts are sufficient to answer.\n\n"
            "- 'answerable': facts contain all info needed to fully answer\n"
            "- 'needs_more': some relevant facts exist but specific gap remains. "
            "Describe exactly what's missing in missing_piece.\n"
            "- 'irrelevant': question is not about weeds, weed identification, "
            "or weed management.\n"
        )),
        HumanMessage(content=(
            f"Question: {question}\n\n"
            f"Gathered facts:\n{facts_str}"
        )),
    ])

    print(f"[Evaluation]: {result.status} | {result.reasoning}")

    return {
        "evaluation": result.status,
        "missing_info": result.missing_piece
    }


def reformulate(state: WeedState):
    question = state["original_question"]
    gathered = state.get("gathered_facts", [])
    missing = state.get("missing_info", "")

    facts_str = "\n".join(f"- {fact}" for fact in gathered)

    reform_llm = llm.with_structured_output(Reformulation)

    result = reform_llm.invoke([
        SystemMessage(content=(
            "You are a query reformulation specialist. "
            "Given the original question, "
            "the facts gathered so far, and the identified information gap, "
            "create a NEW search query that targets the missing piece.\n\n"
            "Rules:\n"
            "- The query must be DIFFERENT from what would have "
            "produced the existing facts.\n"
            "- Be specific — use names, entities, or details "
            "from gathered facts.\n"
            "- Keep the query short under 10 words."
        )),
        HumanMessage(content=(
            f"Original question: {question}\n\n"
            f"Gathered facts:\n{facts_str}\n\n"
            f"Information gap: {missing}"
        )),
    ])

    print(f"Follow up query: {result.new_query} ({result.rationale})")

    return {
        "current_query": result.new_query,
        "retry_count": state.get("retry_count", 0) + 1
    }


def respond(state: WeedState):
    question = state["original_question"]
    gathered = state.get("gathered_facts", [])
    chat_history = state.get("chat_history", [])
    evaluation = state.get("evaluation", "")

    if evaluation == "irrelevant":
        response_text = (
            "I'm specialized in weed identification and management only. "
            "Please ask me about weeds, control methods, or plant characteristics."
        )

        updated_history = chat_history + [
            {"role": "user", "content": question},
            {"role": "assistant", "content": response_text}
        ]

        return {
            "response": response_text,
            "chat_history": updated_history
        }

    facts_str = "\n".join(f"- {fact}" for fact in gathered)

    history_str = "\n".join(
        f"{msg['role']}: {msg['content']}"
        for msg in chat_history
    ) if chat_history else "No previous conversation"

    response = weed_chain.invoke({
        "question": question,
        "facts": facts_str,
        "chat_history": history_str
    })

    updated_history = chat_history + [
        {"role": "user", "content": question},
        {"role": "assistant", "content": response.content}
    ]

    return {
        "response": response.content,
        "chat_history": updated_history
    }


def evaluate_router(state: WeedState) -> Literal["answerable", "needs_more", "irrelevant"]:
    if state["evaluation"] == "answerable":
        return "answerable"

    if state["evaluation"] == "irrelevant":
        return "irrelevant"

    if state.get("retry_count", 0) >= 2:
        return "answerable"

    return "needs_more"


workflow = StateGraph(WeedState)

workflow.add_node("retrieve", retrieve_facts)
workflow.add_node("evaluate", evaluate)
workflow.add_node("reformulate", reformulate)
workflow.add_node("respond", respond)

workflow.add_edge(START, "retrieve")
workflow.add_edge("retrieve", "evaluate")

workflow.add_conditional_edges(
    "evaluate",
    evaluate_router,
    {
        "answerable": "respond",
        "needs_more": "reformulate",
        "irrelevant": "respond"
    }
)

workflow.add_edge("reformulate", "retrieve")
workflow.add_edge("respond", END)

graph = workflow.compile()