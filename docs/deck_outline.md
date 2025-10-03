# IntelliCourse — 10‑Slide Deck (with notes)

## Slide 1 — Title
- IntelliCourse: AI‑Powered University Course Advisor
- Tagline: “Ask about courses like you would a mentor.”
**Say:** In the next 7–10 minutes, I’ll show the problem, our solution, how it works, results, and what’s next.

## Slide 2 — Problem
- Students sift PDFs to answer simple planning questions
- Hard to find prerequisites, cross‑disciplinary options, or topic coverage
**Say:** Today, students spend time navigating dense catalogs; that slows planning and leads to suboptimal choices.

## Slide 3 — Solution
- REST API + Agent that answers catalog questions
- RAG over course PDFs; routes to web for general questions
**Say:** IntelliCourse retrieves from the catalog when appropriate or searches the web when broader context is needed.

## Slide 4 — Demo
- Query examples:
  - “What are the prerequisites for Advanced Machine Learning?”
  - “Which courses cover Python and data visualization?”
  - “Give me a course that combines biology with CS.”
**Say:** I’ll run three quick queries through the API and show the JSON answer with snippets.

## Slide 5 — Architecture
- FastAPI → LangGraph agent (router) → (retriever | web) → LLM
- Chroma + all‑MiniLM‑L6‑v2
**Say:** The router classifies intent; RAG retrieves top‑K chunks; the LLM synthesizes an answer with citations.

## Slide 6 — Implementation
- LangChain loaders, splitters, embeddings
- LangGraph state machine, conditional edges
**Say:** We structured the code into modules for API, agent, RAG; each piece is testable and replaceable.

## Slide 7 — Results
- Retrieval accuracy on a small labeled set
- Latency breakdown (retrieval vs generation)
**Say:** We validated outputs against a checklist of questions and measured end‑to‑end times.

## Slide 8 — Limitations
- Catalog freshness; syllabus coverage
- Router errors; hallucination risk
**Say:** We mitigate with clear citations, conservative prompting, and an explicit “no answer” path.

## Slide 9 — Roadmap
- Add syllabus ingestion; add rerankers
- Add feedback loop; cache popular queries
**Say:** Next, we’ll widen sources and improve quality and speed.

## Slide 10 — Ask
- Pilot with 2–3 departments
- Feedback on accuracy and coverage
**Say:** We’re looking for pilot partners and reviewer feedback.
