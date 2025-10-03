from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from .agent_graph import run_agent

app = FastAPI(title="IntelliCourse API", version="1.0.0")

class QueryRequest(BaseModel):
    query: str = Field(..., description="User question about courses or general topics")

class ContextSnippet(BaseModel):
    source: str
    page: Optional[int] = None
    snippet: str

class QueryResponse(BaseModel):
    answer: str
    source_tool: str
    route: Optional[str] = None
    retrieved_context: Optional[List[ContextSnippet]] = None

@app.post("/chat", response_model=QueryResponse)
def chat(req: QueryRequest):
    result = run_agent(req.query)
    retrieved_context = None
    if result.get("source_tool") == "course_db" and "docs" in result:
        retrieved_context = [
            ContextSnippet(**d) for d in result.get("docs", [])
        ]
    return QueryResponse(
        answer=result.get("answer", ""),
        source_tool=result.get("source_tool", ""),
        route=result.get("route"),
        retrieved_context=retrieved_context
    )

@app.get("/healthz")
def healthz():
    return {"status": "ok"}
