from typing import Literal, TypedDict, List, Dict, Any, Optional
from dataclasses import dataclass

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import SystemMessage, HumanMessage

# LLMs
from .config import LLM_PROVIDER, TOP_K, TAVILY_API_KEY
from .prompts import ROUTER_SYSTEM, GENERATION_SYSTEM
from .rag import load_vector_store

# LangGraph
from langgraph.graph import StateGraph, END

# Tools
from langchain_community.tools.tavily_search import TavilySearchResults

# LLM provider setup
def get_llm():
    if LLM_PROVIDER == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(model="llama3-70b-8192", temperature=0)
    elif LLM_PROVIDER == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0)
    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}")

class AgentState(TypedDict, total=False):
    query: str
    route: Literal["course", "web"]
    source_tool: Literal["course_db", "web"]
    docs: List[Dict[str, Any]]
    web_results: List[Dict[str, Any]]
    answer: str

# Shared resources (loaded once)
_llm = None
_retriever = None
_web_tool = None

def _ensure_init():
    global _llm, _retriever, _web_tool
    if _llm is None:
        _llm = get_llm()
    if _retriever is None:
        vs = load_vector_store()
        _retriever = vs.as_retriever(search_type="mmr", search_kwargs={"k": TOP_K})
    if _web_tool is None:
        _web_tool = TavilySearchResults(max_results=5, tavily_api_key=TAVILY_API_KEY)

# ---- Nodes ----

def router_node(state: AgentState) -> AgentState:
    _ensure_init()
    llm = _llm
    prompt = ChatPromptTemplate.from_messages([
        ("system", ROUTER_SYSTEM),
        ("human", "{q}")
    ])
    chain = prompt | llm | StrOutputParser()
    route = chain.invoke({"q": state["query"]}).strip().lower()
    if route not in ("course", "web"):
        # Fallback: simple heuristic
        heur = "course" if any(k in state["query"].lower() for k in ["course", "prereq", "credit", "catalog", "syllabus", "department"]) else "web"
        route = heur
    state["route"] = route # type: ignore
    return state

def course_retrieval_node(state: AgentState) -> AgentState:
    _ensure_init()
    docs = _retriever.get_relevant_documents(state["query"])  # type: ignore
    # Convert to serializable dicts
    state["docs"] = [{
        "page_content": d.page_content,
        "metadata": d.metadata,
    } for d in docs]
    state["source_tool"] = "course_db"
    return state

def web_search_node(state: AgentState) -> AgentState:
    _ensure_init()
    results = _web_tool.invoke({"query": state["query"]})  # type: ignore
    state["web_results"] = results
    state["source_tool"] = "web"
    return state

def generation_node(state: AgentState) -> AgentState:
    _ensure_init()
    llm = _llm
    if state.get("source_tool") == "course_db":
        # Build context from docs
        context_lines = []
        for d in state.get("docs", []):
            meta = d.get("metadata", {})
            src = meta.get("source", "unknown")
            page = meta.get("page", "N/A")
            snippet = d.get("page_content", "").strip().replace("\n", " ")
            context_lines.append(f"[source: {src}, p.{page}] {snippet}")
        context = "\n".join(context_lines) if context_lines else "NO_CONTEXT"
    else:
        # Build context from web results
        context_lines = []
        for r in state.get("web_results", []):
            title = r.get("title", "result")
            url = r.get("url", "")
            content = r.get("content", "").strip().replace("\n", " ")
            context_lines.append(f"[web: {title} | {url}] {content}")
        context = "\n".join(context_lines) if context_lines else "NO_CONTEXT"

    prompt = ChatPromptTemplate.from_messages([
        ("system", GENERATION_SYSTEM),
        ("human", "Question: {q}\n\nContext:\n{ctx}\n\nAnswer:")
    ])
    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({"q": state["query"], "ctx": context}).strip()
    state["answer"] = answer

    return state

# ---- Graph wiring ----

def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("router", router_node)
    graph.add_node("course_retrieval", course_retrieval_node)
    graph.add_node("web_search", web_search_node)
    graph.add_node("generation", generation_node)

    graph.set_entry_point("router")

    def decide_route(state: AgentState) -> str:
        return "course_retrieval" if state.get("route") == "course" else "web_search"

    graph.add_conditional_edges("router", decide_route, {
        "course_retrieval": "course_retrieval",
        "web_search": "web_search"
    })

    graph.add_edge("course_retrieval", "generation")
    graph.add_edge("web_search", "generation")
    graph.add_edge("generation", END)

    return graph.compile()

# Single compiled app graph
APP_GRAPH = build_graph()

def run_agent(query: str) -> AgentState:
    state: AgentState = {"query": query}
    final_state = APP_GRAPH.invoke(state)
    # Keep only minimal context in response
    result: AgentState = {
        "query": query,
        "route": final_state.get("route"),  # type: ignore
        "source_tool": final_state.get("source_tool"),  # type: ignore
        "answer": final_state.get("answer", ""),
    }
    # Include small snippets for transparency
    if final_state.get("source_tool") == "course_db":
        snippets = []
        for d in final_state.get("docs", [])[:3]:
            meta = d.get("metadata", {})
            snippets.append({
                "source": meta.get("source", "unknown"),
                "page": meta.get("page", "N/A"),
                "snippet": d.get("page_content", "")[:300]
            })
        result["docs"] = snippets  # type: ignore
    else:
        result["web_results"] = final_state.get("web_results", [])[:3]  # type: ignore
    return result
