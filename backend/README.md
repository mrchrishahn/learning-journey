# Mantis WebTeam MIT Courses Semantic Path API

This repository provides a pipeline to extract, embed, and serve MIT course data as a semantic‑path API. Given any two course titles, the API returns a sequence of courses that semantically bridge them using precomputed SentenceTransformer embeddings and a FAISS index.

## Repository Structure

```
backend/
├── Mantis WebTeam MIT courses.xlsx.zip   # ZIP of the multi-sheet Excel workbook (data source)
├── extract.py                            # Reads Excel → concatenated docs → FAISS index + pickles
├── embeddings.py                         # Loads pickles → computes & dumps embeddings (embs.npy, ids.pkl, metas.pkl)
├── documents.pkl                         # Pickle storing { ids: [...], docs: [...] }
├── metadata.pkl                          # Pickle storing list of metadata dicts per doc
├── embs.npy                              # N×D NumPy array of float32 embeddings
├── ids.pkl                               # Pickle list of record IDs
├── metas.pkl                             # Pickle list of metadata dicts
├── faiss_index.idx                       # Serialized FAISS FlatL2 index of embeddings
├── main.py                               # FastAPI service exposing `/semantic-path` endpoint
├── requirements.txt                      # Python dependencies
└── test.py (optional)                    # Example client/test code
```

## Prerequisites

* **Python 3.10** installed on macOS
* Install dependencies:

```bash
pip install -r requirements.txt
```

## Data Preparation

1. **Unzip** the course data:

   ```bash
   unzip "Mantis WebTeam MIT courses.xlsx.zip"
   ```

   This produces `Mantis WebTeam MIT courses.xlsx` in the working directory.

2. **Extract & Index** (one‑time):

   ```bash
   python3 extract.py
   ```

   * Reads all sheets, concatenates `course_num`, `course_title`, and `description` into text.
   * Embeds each row with `all-MiniLM-L6-v2` and adds to a FAISS FlatL2 index.
   * Produces:

     * `faiss_index.idx`
     * `documents.pkl` (ids & docs)
     * `metadata.pkl` (metadata list)

3. **Compute & Dump Embeddings** (optional speed‑up):

   ```bash
   python3 embeddings.py
   ```

   * Loads `documents.pkl` + `metadata.pkl`.
   * Bulk‑encodes all docs on CPU.
   * Dumps:

     * `embs.npy` (N×D embeddings)
     * `ids.pkl` (list of IDs)
     * `metas.pkl` (list of metadata dicts)

> **Note**: Once you have `embs.npy`, `ids.pkl`, and `metas.pkl`, you can skip `extract.py` & `faiss_index.idx` and rebuild the index entirely in `main.py` at startup.

## Running the API

The FastAPI service (`main.py`) exposes a single POST endpoint:

```
POST /semantic-path
Content-Type: application/json

{
  "start": "Independent Study in Architecture Design",
  "end":   "SHASS Exploration",
  "k": 5,
  "max_results": 10
}
```

* **start**: the title of the source course
* **end**: the title of the target course
* **k**: number of neighbors to consider at each greedy step (default 5)
* **max\_results**: maximum length of the returned path (default 10)

### Start the server

```bash
python3 main.py
```

The service listens on `http://0.0.0.0:8000`.  You can test interactively at:

* **Health**:  `GET http://localhost:8000/`
* **Swagger UI**: `http://localhost:8000/docs`

## Core Algorithm

1. **Embedding**: course text → 384‑dim vector via `all-MiniLM-L6-v2`.
2. **Similarity**: Euclidean (L2) distance measured in FAISS FlatL2 index.
3. **Greedy Path**:

   * Start from the `start` embedding.
   * At each step, query FAISS for the top‑k nearest neighbors (excluding visited courses).
   * Choose the neighbor whose embedding is closest to the **end** embedding, append it.
   * Repeat until the **end** is reached or `max_results` steps.
   * **Deduplicate**: ensure each course appears only once.
   * **Pad/Truncate**: if path is too short, insert additional unique neighbors of the **end** until reaching `max_results`; if too long, truncate to `max_results`.

This yields a concise semantic chain bridging any two course titles in MIT’s course catalog.

- Paul Kao
- Sunil Kumar
