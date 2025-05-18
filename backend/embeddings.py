# dump_embeddings.py
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

# 1. Load your existing documents + metadata
data    = pickle.load(open("documents.pkl", "rb"))
ids, docs = data["ids"], data["docs"]
metads  = pickle.load(open("metadata.pkl", "rb"))

# 2. Compute embeddings once
model = SentenceTransformer("all-MiniLM-L6-v2")
embs  = np.vstack([model.encode(doc).astype("float32") for doc in docs])

# 3. Dump to disk
np.save("embs.npy", embs)
pickle.dump(ids,   open("ids.pkl",   "wb"))
pickle.dump(metads,open("metas.pkl", "wb"))

print(f"✔️  Saved {len(ids)} ids to ids.pkl, metadata to metas.pkl, embeddings to embs.npy")
