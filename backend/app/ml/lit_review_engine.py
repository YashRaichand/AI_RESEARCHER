import anthropic
from typing import List, Dict, Any
from app.core.config import get_settings

settings = get_settings()


class LiteratureReviewEngine:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    def generate(self, topic: str, papers_context: str) -> Dict[str, Any]:
        prompt = f"""You are an expert academic researcher. Write a comprehensive literature review on the topic: "{topic}"

Based on these research papers:
{papers_context[:8000]}

Write a structured literature review with these exact sections:

## 1. Introduction
Brief overview of the research area and its importance.

## 2. Thematic Analysis
Identify and discuss 3-5 major themes found across the papers.

## 3. Trends
Key trends and developments in this research area.

## 4. Key Papers Summary
Brief summary of the most important papers.

## 5. Research Gaps
What is missing, underexplored, or contradictory in the literature.

## 6. Conclusion
Synthesis and future directions.

Use academic writing style. Be specific and cite papers where relevant."""

        response = self.client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}],
        )
        content = response.content[0].text

        themes = self._extract_themes(content)
        trends = self._extract_trends(content)
        gaps = self._extract_gaps(content)

        return {
            "content": content,
            "themes": themes,
            "trends": trends,
            "gaps": gaps,
            "word_count": len(content.split()),
        }

    def _extract_themes(self, content: str) -> List[str]:
        import re
        theme_section = re.search(r'Thematic Analysis(.*?)(?:##|$)', content, re.DOTALL | re.IGNORECASE)
        if theme_section:
            lines = [l.strip() for l in theme_section.group(1).split('\n') if l.strip() and len(l.strip()) > 20]
            return lines[:6]
        return []

    def _extract_trends(self, content: str) -> List[str]:
        import re
        trends_section = re.search(r'Trends(.*?)(?:##|$)', content, re.DOTALL | re.IGNORECASE)
        if trends_section:
            lines = [l.strip() for l in trends_section.group(1).split('\n') if l.strip() and len(l.strip()) > 20]
            return lines[:6]
        return []

    def _extract_gaps(self, content: str) -> List[str]:
        import re
        gaps_section = re.search(r'Research Gaps(.*?)(?:##|$)', content, re.DOTALL | re.IGNORECASE)
        if gaps_section:
            lines = [l.strip() for l in gaps_section.group(1).split('\n') if l.strip() and len(l.strip()) > 20]
            return lines[:6]
        return []
