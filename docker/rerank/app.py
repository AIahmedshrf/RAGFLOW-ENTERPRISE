from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os, torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_ID = os.getenv("RERANK_MODEL", "BAAI/bge-reranker-v2-m3")

app = FastAPI(title="Local Reranker", version="1.0")

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_ID)
model.eval()

class RerankRequest(BaseModel):
    query: str
    documents: List[str]
    top_n: Optional[int] = 5
    model: Optional[str] = None

@app.get("/v1/health")
def health():
    return {"status": "ok", "model": MODEL_ID}

@app.post("/v1/rerank")
def rerank(req: RerankRequest):
    if not req.documents:
        raise HTTPException(400, "documents is empty")
    
    # Compute scores for all documents
    with torch.no_grad():
        inputs = tokenizer([req.query]*len(req.documents),
                           req.documents,
                           padding=True, truncation=True, max_length=512, return_tensors="pt")
        scores = model(**inputs).logits.squeeze(-1).tolist()
    
    # Create results with original indices
    results = [
        {"index": i, "relevance_score": float(score), "document": doc}
        for i, (doc, score) in enumerate(zip(req.documents, scores))
    ]
    
    # Sort by relevance_score descending
    results_sorted = sorted(results, key=lambda x: x["relevance_score"], reverse=True)
    
    # Return top_n results (RAGFlow expects "results" key, not "data")
    k = min(req.top_n or len(req.documents), len(results_sorted))
    return {
        "object": "list",
        "model": req.model or MODEL_ID,
        "results": results_sorted[:k]
    }
