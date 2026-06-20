import anthropic
from typing import AsyncGenerator, List, Dict, Any, Optional
from app.ml.rag_engine import RAGEngine
from app.core.config import get_settings

settings = get_settings()


class ChatEngine:
    def __init__(self, rag_engine: RAGEngine):
        self.rag_engine = rag_engine
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    async def chat(
        self,
        question: str,
        paper_ids: Optional[List[str]] = None,
        chat_history: Optional[List[Dict]] = None,
    ) -> AsyncGenerator[str, None]:
        chunks = self.rag_engine.retrieve_with_citations(question, paper_ids=paper_ids, top_k=8)
        context = self.rag_engine.format_context(chunks)
        system_prompt = self.rag_engine.build_system_prompt()

        messages = []
        if chat_history:
            for msg in chat_history[-6:]:
                messages.append({"role": msg["role"], "content": msg["content"]})

        user_content = f"""Context from research papers:
{context}

Question: {question}

Answer based on the provided context. Cite sources using [Source: Paper XXXXXXXX] format."""

        messages.append({"role": "user", "content": user_content})

        with self.client.messages.stream(
            model="claude-3-5-haiku-20241022",
            max_tokens=2048,
            system=system_prompt,
            messages=messages,
        ) as stream:
            for text in stream.text_stream:
                yield text

        citations = [
            {
                "paper_id": c["paper_id"],
                "chunk_text": c["chunk_text"][:200],
                "section": c.get("section_name", ""),
                "score": c.get("hybrid_score", 0),
            }
            for c in chunks
        ]
        yield f"\n\n__CITATIONS__{str(citations)}__END_CITATIONS__"

    def extract_citations_from_response(self, response: str) -> tuple[str, List[Dict]]:
        if "__CITATIONS__" in response:
            parts = response.split("__CITATIONS__")
            text = parts[0].strip()
            try:
                import ast
                citations = ast.literal_eval(parts[1].replace("__END_CITATIONS__", "").strip())
            except Exception:
                citations = []
            return text, citations
        return response, []
