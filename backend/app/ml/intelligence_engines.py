import anthropic
import json
import re
from typing import List, Dict, Any
from app.core.config import get_settings

settings = get_settings()
_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


class ResearchGapDetector:
    def detect(self, papers_context: str) -> List[Dict[str, Any]]:
        prompt = f"""Analyze these research papers and identify research gaps.

{papers_context[:6000]}

Return a JSON array of gaps. Each gap object must have:
- topic: string (the gap topic)
- description: string (detailed description)
- novelty_score: number 0-100
- suggested_experiments: array of strings
- type: one of ["underexplored", "contradiction", "missing_experiment", "future_opportunity"]

Return ONLY valid JSON, no other text."""

        response = _client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        try:
            text = response.content[0].text.strip()
            text = re.sub(r'^```json\s*', '', text)
            text = re.sub(r'\s*```$', '', text)
            gaps = json.loads(text)
            return gaps if isinstance(gaps, list) else []
        except Exception:
            return [{"topic": "Data extraction failed", "description": "Could not parse gaps", "novelty_score": 0, "suggested_experiments": [], "type": "future_opportunity"}]


class PaperComparisonEngine:
    def compare(self, papers_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        papers_summary = ""
        for i, p in enumerate(papers_data[:10]):
            papers_summary += f"\nPaper {i+1}: {p.get('title', 'Untitled')}\nAbstract: {p.get('abstract', '')[:300]}\n"

        prompt = f"""Compare these research papers across key dimensions.

{papers_summary}

Return a JSON object with:
- comparison_table: array of objects, each with keys: paper_title, dataset, methods, models, accuracy, contributions, limitations
- summary: string with overall comparison analysis
- best_for: object mapping use_cases to paper titles

Return ONLY valid JSON."""

        response = _client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        try:
            text = response.content[0].text.strip()
            text = re.sub(r'^```json\s*', '', text)
            text = re.sub(r'\s*```$', '', text)
            return json.loads(text)
        except Exception:
            return {"comparison_table": [], "summary": "Comparison generated", "best_for": {}}


class KnowledgeGraphBuilder:
    def build(self, papers_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        nodes = []
        edges = []
        node_ids = set()

        for paper in papers_data[:20]:
            paper_id = str(paper.get("id", ""))[:8]
            paper_node_id = f"paper_{paper_id}"
            if paper_node_id not in node_ids:
                nodes.append({"id": paper_node_id, "label": paper.get("title", "Untitled")[:50], "type": "paper", "weight": 1.0})
                node_ids.add(paper_node_id)

            for author in paper.get("authors", [])[:3]:
                author_id = f"author_{re.sub(r'[^a-zA-Z]', '', str(author))[:20]}"
                if author_id not in node_ids:
                    nodes.append({"id": author_id, "label": str(author)[:50], "type": "author", "weight": 0.8})
                    node_ids.add(author_id)
                edges.append({"source": author_id, "target": paper_node_id, "relation": "authored", "weight": 1.0})

            topic = paper.get("topic", "Other")
            topic_id = f"topic_{topic.replace(' ', '_')}"
            if topic_id not in node_ids:
                nodes.append({"id": topic_id, "label": topic, "type": "topic", "weight": 0.9})
                node_ids.add(topic_id)
            edges.append({"source": paper_node_id, "target": topic_id, "relation": "belongs_to", "weight": 0.9})

            for kw in paper.get("keywords", [])[:5]:
                kw_id = f"kw_{re.sub(r'[^a-zA-Z]', '', kw)[:20]}"
                if kw_id not in node_ids:
                    nodes.append({"id": kw_id, "label": kw[:30], "type": "concept", "weight": 0.6})
                    node_ids.add(kw_id)
                edges.append({"source": paper_node_id, "target": kw_id, "relation": "uses_concept", "weight": 0.6})

        return {"nodes": nodes, "edges": edges, "node_count": len(nodes), "edge_count": len(edges)}


class ResearchIdeaGenerator:
    def generate(self, papers_context: str, gaps: List[Dict] = None) -> List[Dict[str, Any]]:
        gaps_text = ""
        if gaps:
            gaps_text = "Known gaps:\n" + "\n".join([g.get("description", "") for g in gaps[:5]])

        prompt = f"""Based on these research papers, generate creative research ideas.

{papers_context[:4000]}

{gaps_text}

Return a JSON array of 5-8 research ideas. Each idea must have:
- title: string
- description: string (2-3 sentences)
- rationale: string (why this is important)
- difficulty: "easy" | "medium" | "hard"
- novelty_score: number 0-100
- research_questions: array of strings (2-3 questions)
- experimental_approach: string

Return ONLY valid JSON."""

        response = _client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        try:
            text = response.content[0].text.strip()
            text = re.sub(r'^```json\s*', '', text)
            text = re.sub(r'\s*```$', '', text)
            ideas = json.loads(text)
            return ideas if isinstance(ideas, list) else []
        except Exception:
            return []


class FlashcardGenerator:
    def generate(self, paper_data: Dict[str, Any], card_types: List[str] = None) -> List[Dict[str, Any]]:
        if card_types is None:
            card_types = ["qa", "revision", "exam"]

        title = paper_data.get("title", "Paper")
        abstract = paper_data.get("abstract", "")
        sections = paper_data.get("parsed_sections", {})
        content = f"Title: {title}\nAbstract: {abstract}\n"
        for sec_name, sec_text in list(sections.items())[:3]:
            content += f"\n{sec_name}: {str(sec_text)[:500]}"

        prompt = f"""Create educational flashcards from this research paper.

{content[:4000]}

Return a JSON array of 10-15 flashcards. Each flashcard must have:
- front: string (question or concept)
- back: string (answer or explanation)
- card_type: "qa" | "revision" | "exam"
- difficulty: "easy" | "medium" | "hard"
- topic: string

Cover: key concepts, methodology, results, terminology, and exam-style questions.
Return ONLY valid JSON."""

        response = _client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        try:
            text = response.content[0].text.strip()
            text = re.sub(r'^```json\s*', '', text)
            text = re.sub(r'\s*```$', '', text)
            cards = json.loads(text)
            return cards if isinstance(cards, list) else []
        except Exception:
            return []
