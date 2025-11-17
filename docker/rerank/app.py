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
    with torch.no_grad():
        inputs = tokenizer([req.query]*len(req.documents),
                           req.documents,
                           padding=True, truncation=True, max_length=512, return_tensors="pt")
        scores = model(**inputs).logits.squeeze(-1).tolist()
    ranked = sorted(zip(req.documents, scores), key=lambda x: x[1], reverse=True)
    k = min(req.top_n or 5, len(ranked))
    data = [{"index": i, "relevance_score": float(s), "document": d}
            for i,(d,s) in enumerate(ranked[:k])]
    return {"object":"list","model": req.model or MODEL_ID,"data": data}
