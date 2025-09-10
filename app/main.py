from fastapi import FastAPI
from pydantic import BaseModel
from .graph import build_graph

app = FastAPI()
graph = build_graph()

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    evidence: dict | None = None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    state = {"question": req.question}
    final = graph.invoke(state)
    return {
        "answer": final.get("answer", ""),
        "evidence": final.get("evidence", None),
    }
