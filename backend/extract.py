import pandas as pd
import numpy as np
import pickle
import os
from openpyxl import load_workbook
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import faiss

# -------------- Configuration --------------
PATH = os.getcwd()
EXCEL_PATH = os.path.join(PATH,'Mantis WebTeam MIT courses.xlsx')
TEXT_COLUMNS = ["course_num", "course_title", "description"]  # Columns to combine into the document text
FAISS_INDEX_PATH = "./faiss_index.idx"   # Filepath to store FAISS index
DOCS_PICKLE_PATH = "./documents.pkl"     # Filepath to store docs and IDs
METADATA_PICKLE_PATH = "./metadata.pkl"  # Filepath to store metadata list

# --------------- Setup ---------------------
# Initialize embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")
# Get embedding dimension
dim = model.get_sentence_embedding_dimension()
# Initialize FAISS index (Flat L2)
index = faiss.IndexFlatL2(dim)

# Containers for document storage
ids = []
docs = []
metadatas = []

total_count = 0
# 1. Read all sheets from the Excel workbook into a dict
all_sheets = pd.read_excel(EXCEL_PATH, sheet_name=None, engine="openpyxl")

for sheet_name, df in all_sheets.items():
    # Normalize column names
    df.columns = df.columns.str.strip().str.lower()
    # Check for missing columns
    missing = set(TEXT_COLUMNS) - set(df.columns)
    if missing:
        print(f"⚠️ Skipping sheet '{sheet_name}'; missing columns: {', '.join(missing)}")
        continue
    # Filter to non-empty rows
    df = df.dropna(subset=[TEXT_COLUMNS[0]], how="all")

    # 2. Ingest each row in the sheet
    for idx, row in df.iterrows():
        # Combine text columns
        doc_text = " \n ".join(str(row[col]) for col in TEXT_COLUMNS if pd.notna(row[col]))
        # Compute embedding
        embedding = model.encode(doc_text)
        # Add to FAISS index
        emb_vector = np.array([embedding], dtype='float32')
        index.add(emb_vector)

        # Record IDs, docs, metadata
        base_id = row.get("course_num", idx)
        record_id = f"{sheet_name}_{base_id}"
        ids.append(record_id)
        docs.append(doc_text)
        meta = {col: row[col] for col in TEXT_COLUMNS if col != "description" and pd.notna(row[col])}
        meta.update({"sheet": sheet_name, "source": EXCEL_PATH})
        metadatas.append(meta)

        total_count += 1

# 3. Save FAISS index and associated data
faiss.write_index(index, FAISS_INDEX_PATH)
with open(DOCS_PICKLE_PATH, "wb") as f:
    pickle.dump({"ids": ids, "docs": docs}, f)
with open(METADATA_PICKLE_PATH, "wb") as f:
    pickle.dump(metadatas, f)

print(f"✅ Ingested {total_count} records into FAISS index at '{FAISS_INDEX_PATH}'")
