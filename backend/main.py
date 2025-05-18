#!/usr/bin/env python3.10
import logging
from fastapi import FastAPI, Body
from pydantic import BaseModel, Field
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- FastAPI App Setup ---
app = FastAPI(title="Semantic Path API")

# Root endpoint for health check and quick info
@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Semantic Path API. Navigate to /docs for Swagger UI."}

# --- Preload static resources ---
ids        = pickle.load(open("ids.pkl","rb"))            # list of IDs
docs       = pickle.load(open("documents.pkl","rb"))["docs"]  # list of texts
metads     = pickle.load(open("metas.pkl","rb"))          # list of metadata dicts
embeddings = np.load("embs.npy")                             # (N, D) float32 array

dict_id_to_vec = dict(zip(ids, embeddings))

# --- Split raw doc text to get description ---
def split_raw(raw: str) -> str:
    parts = raw.split(" \n ")
    return parts[-1] if len(parts) >= 3 else ""

# Placeholders for model and index
model = None
index = None

# --- Startup event: load model & build FAISS index ---
@app.on_event("startup")
def startup_event():
    global model, index
    logger.info("Starting up: loading model and building FAISS index")
    model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
    dim = embeddings.shape[1]
    idx = faiss.IndexFlatL2(dim)
    idx.add(embeddings)
    index = idx
    logger.info("Model loaded and FAISS index built with %d embeddings", embeddings.shape[0])

# --- Exact-match helper ---
def exact_match(q: str):
    ql = q.strip().lower()
    for _id, m in zip(ids, metads):
        if m.get("course_title", "").strip().lower() == ql:
            return _id
    return None

# --- Greedy path finder ---
def greedy_path(start_id: str, end_id: str, end_emb: np.ndarray, k: int, max_steps: int):
    # 1) Initial greedy walk towards end_id
    path = [start_id]
    visited_ids = {start_id}
    visited_titles = {metads[ids.index(start_id)].get("course_title", "")}
    current = start_id

    for _ in range(max_steps - 1):
        # find k+1 nearest (including self)
        cur_vec = dict_id_to_vec[current].reshape(1, -1)
        dists, nbrs = index.search(cur_vec, k + 1)

        # filter out already visited IDs or titles
        candidates = [
            i for i in nbrs[0]
            if ids[i] not in visited_ids
            and metads[i].get("course_title", "") not in visited_titles
        ]
        if not candidates:
            break

        # choose the candidate closest to end_emb
        next_idx = min(candidates, key=lambda i: np.linalg.norm(embeddings[i] - end_emb))
        next_id = ids[next_idx]
        next_title = metads[next_idx].get("course_title", "")

        path.append(next_id)
        visited_ids.add(next_id)
        visited_titles.add(next_title)
        current = next_id

        if current == end_id:
            break

    # 2) Deduplicate entire path, preserving first occurrences
    seen = set()
    unique_path = []
    for pid in path:
        if pid not in seen:
            unique_path.append(pid)
            seen.add(pid)
    path = unique_path

    # 3) Ensure end_id is at the end
    if path[-1] != end_id:
        path.append(end_id)
        seen.add(end_id)

    # 4) Pad with additional neighbors of end_id if too few
    if len(path) < max_steps:
        dists, nbrs = index.search(end_emb.reshape(1, -1), max_steps * 2)
        for idx in nbrs[0]:
            cid = ids[idx]
            title = metads[idx].get("course_title", "")
            if cid not in seen and title not in visited_titles:
                # insert before the last element (end_id)
                path.insert(-1, cid)
                seen.add(cid)
            if len(path) >= max_steps:
                break

    # 5) Truncate if too many
    if len(path) > max_steps:
        mids = path[1:-1][: max_steps - 2]
        path = [path[0]] + mids + [end_id]

    return path



# --- Pydantic models ---
class PathRequest(BaseModel):
    start: str = Field(
        ..., 
        description="The title of the course to start from", 
        example="Independent Study in Architecture Design"
    )
    end: str = Field(
        ..., 
        description="The title of the course to end at", 
        example="SHASS Exploration"
    )
    k: int = Field(
        5,
        description="Number of nearest‐neighbor steps to consider at each hop",
        example=5
    )
    max_results: int = Field(
        10,
        description="Maximum length of the returned semantic path",
        example=10
    )

    class Config:
        schema_extra = {
            "example": {
                "start": "Independent Study in Architecture Design",
                "end": "SHASS Exploration",
                "k": 5,
                "max_results": 10
            }
        }


class StepContent(BaseModel):
    step: int
    course_num: str
    course_title: str
    description: str

class PathResponse(BaseModel):
    path: list[StepContent]

# --- API endpoint (POST) ---
@app.post(
    "/semantic-path",
    response_model=PathResponse,
    summary="Compute semantic path between two courses",
    description=(
        "Given a `start` and `end` course title, this endpoint returns "
        "a sequence of intermediate courses that semantically bridge them. "
        "Uses pre‐computed FAISS embeddings under the hood."
    )
)
def semantic_path(
    payload: PathRequest = Body(..., description="Parameters for semantic path search")
):
    start, end, k, max_results = payload.start, payload.end, payload.k, payload.max_results
    logger.info(f"Request payload: {payload.dict()}")
    s_id = exact_match(start) or ids[index.search(
        model.encode(start).astype('float32').reshape(1,-1),1
    )[1][0][0]]
    e_id = exact_match(end) or ids[index.search(
        model.encode(end).astype('float32').reshape(1,-1),1
    )[1][0][0]]
    logger.info("Resolved: %s -> %s", s_id, e_id)
    end_emb = model.encode(end).astype('float32')

    path_ids = greedy_path(s_id, e_id, end_emb, k, max_results)
    logger.info("Path length: %d", len(path_ids))

    items = []
    for idx, pid in enumerate(path_ids, start=1):
        meta = metads[ids.index(pid)]
        desc = split_raw(docs[ids.index(pid)])
        items.append(StepContent(
            step=idx,
            course_num=meta.get("course_num",""),
            course_title=meta.get("course_title",""),
            description=desc
        ))
    logger.info("Returning %d items", len(items))
    return PathResponse(path=items)

# --- Entry point ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
