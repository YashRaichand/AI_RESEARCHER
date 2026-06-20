import os
import json
import numpy as np
import faiss
from typing import List, Dict, Any, Optional
from pathlib import Path

class EmbeddingEngine:
    def __init__(self, index_path: str = "./faiss_indexes"):
        self.index_path = Path(index_path)
        self.index_path.mkdir(parents=True, exist_ok=True)
        self.dimension = 768
        self.index: Optional[faiss.Index] = None
        self.metadata: List[Dict] = []
        self._model = None
        self._load_or_create_index()

    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer("all-mpnet-base-v2")
        return self._model

    def _load_or_create_index(self):
        idx_file = self.index_path / "main.index"
        meta_file = self.index_path / "metadata.json"
        if idx_file.exists():
            self.index = faiss.read_index(str(idx_file))
            with open(meta_file) as f:
                self.metadata = json.load(f)
        else:
            self.index = faiss.IndexFlatIP(self.dimension)
            self.metadata = []

    def _save_index(self):
        faiss.write_index(self.index, str(self.index_path / "main.index"))
        with open(self.index_path / "metadata.json", "w") as f:
            json.dump(self.metadata, f)

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        embeddings = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return embeddings.astype(np.float32)

    def embed_paper(self, paper_data: Dict[str, Any], paper_id: str) -> List[Dict]:
        chunks = []
        if paper_data.get("full_text"):
            words = paper_data["full_text"].split()
            paragraphs = [" ".join(words[i:i+200]) for i in range(0, min(len(words), 10000), 150)]
            for idx, para in enumerate(paragraphs[:100]):
                if len(para.strip()) > 50:
                    chunks.append({"text": para, "type": "paragraph", "index": idx, "section": "full_text"})

        for section_name, section_text in paper_data.get("sections", {}).items():
            if section_text and len(section_text) > 100:
                chunks.append({"text": section_text[:2000], "type": "section", "index": 0, "section": section_name})

        if not chunks:
            return []

        texts = [c["text"] for c in chunks]
        embeddings = self.embed_texts(texts)

        stored = []
        for chunk, emb in zip(chunks, embeddings):
            faiss_id = self.index.ntotal
            self.index.add(emb.reshape(1, -1))
            meta = {
                "faiss_id": faiss_id,
                "paper_id": paper_id,
                "chunk_type": chunk["type"],
                "chunk_text": chunk["text"],
                "chunk_index": chunk["index"],
                "section_name": chunk["section"],
                "embedding_model": "all-mpnet-base-v2",
            }
            self.metadata.append(meta)
            stored.append(meta)

        self._save_index()
        return stored

    def search(self, query: str, paper_ids: Optional[List[str]] = None, top_k: int = 10) -> List[Dict]:
        if self.index.ntotal == 0:
            return []
        query_emb = self.embed_texts([query])
        k = min(top_k * 5, self.index.ntotal)
        scores, indices = self.index.search(query_emb, k)
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.metadata):
                continue
            meta = self.metadata[idx]
            if paper_ids and meta["paper_id"] not in paper_ids:
                continue
            results.append({**meta, "score": float(score)})
            if len(results) >= top_k:
                break
        return results
    