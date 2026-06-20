from typing import List, Dict, Any, Optional
from rank_bm25 import BM25Okapi
import re
from app.ml.embedding_engine import EmbeddingEngine


class RAGEngine:
    def __init__(self, embedding_engine: EmbeddingEngine):
        self.embedding_engine = embedding_engine

    def hybrid_search(self, query: str, paper_ids: Optional[List[str]] = None, top_k: int = 10) -> List[Dict]:
        semantic_results = self.embedding_engine.search(query, paper_ids=paper_ids, top_k=top_k * 2)
        if not semantic_results:
            return []

        all_texts = [r["chunk_text"] for r in semantic_results]
        tokenized = [t.lower().split() for t in all_texts]
        if not tokenized:
            return semantic_results[:top_k]

        bm25 = BM25Okapi(tokenized)
        query_tokens = query.lower().split()
        bm25_scores = bm25.get_scores(query_tokens)

        for i, result in enumerate(semantic_results):
            semantic_score = result.get("score", 0)
            bm25_score = float(bm25_scores[i]) if i < len(bm25_scores) else 0
            bm25_norm = bm25_score / (max(bm25_scores) + 1e-9)
            result["hybrid_score"] = 0.6 * semantic_score + 0.4 * bm25_norm

        semantic_results.sort(key=lambda x: x["hybrid_score"], reverse=True)
        return semantic_results[:top_k]

    def retrieve_with_citations(self, query: str, paper_ids: Optional[List[str]] = None, top_k: int = 8) -> List[Dict]:
        results = self.hybrid_search(query, paper_ids=paper_ids, top_k=top_k)
        for r in results:
            r["citation_key"] = f"[Source: Paper {r['paper_id'][:8]}]"
        return results

    def format_context(self, chunks: List[Dict]) -> str:
        context_parts = []
        for i, chunk in enumerate(chunks):
            paper_ref = f"[{i+1}] Paper ID: {chunk['paper_id'][:8]}"
            if chunk.get("section_name"):
                paper_ref += f" | Section: {chunk['section_name']}"
            context_parts.append(f"{paper_ref}\n{chunk['chunk_text']}\n")
        return "\n---\n".join(context_parts)

    def build_system_prompt(self) -> str:
        return (
            "You are Scientia AI, an expert academic research assistant. "
            "You answer questions based strictly on the provided research paper context. "
            "Always cite your sources using the [Source: Paper XXXXXXXX] format. "
            "Be precise, academic, and helpful. If information is not in the context, say so clearly. "
            "Structure your answers with clear headings when appropriate."
        )
