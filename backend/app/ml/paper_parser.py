import re
from typing import Dict, List, Any


SECTION_PATTERNS = {
    "introduction": r'\b(introduction|background|overview|motivation)\b',
    "literature_review": r'\b(related work|literature review|prior work|previous work|background and related)\b',
    "methodology": r'\b(methodology|methods?|approach|proposed method|our approach|model|architecture)\b',
    "experiments": r'\b(experiments?|experimental setup|evaluation|implementation details)\b',
    "results": r'\b(results?|findings|performance|analysis|discussion|ablation)\b',
    "conclusion": r'\b(conclusion|summary|future work|limitations|concluding remarks)\b',
    "references": r'\b(references|bibliography)\b',
}


class ScientificPaperParser:
    def parse(self, raw_text: str) -> Dict[str, Any]:
        lines = raw_text.split("\n")
        sections = self._identify_sections(lines)
        return {
            "sections": sections,
            "section_order": list(sections.keys()),
            "word_counts": {k: len(v.split()) for k, v in sections.items()},
        }

    def _identify_sections(self, lines: List[str]) -> Dict[str, str]:
        sections: Dict[str, List[str]] = {k: [] for k in SECTION_PATTERNS}
        sections["other"] = []
        current_section = "other"

        for line in lines:
            line_lower = line.lower().strip()
            matched = False
            for section, pattern in SECTION_PATTERNS.items():
                if re.search(pattern, line_lower, re.IGNORECASE):
                    if len(line.strip()) < 100:
                        current_section = section
                        matched = True
                        break
            if not matched:
                sections[current_section].append(line)

        return {k: "\n".join(v).strip() for k, v in sections.items() if v}

    def section_classifier(self, text: str) -> str:
        text_lower = text.lower()
        for section, pattern in SECTION_PATTERNS.items():
            if re.search(pattern, text_lower):
                return section
        return "other"

    def extract_keywords(self, abstract: str) -> List[str]:
        stop_words = {"the", "a", "an", "is", "are", "was", "were", "in", "on",
                      "at", "to", "for", "of", "and", "or", "but", "this", "that",
                      "we", "our", "it", "with", "by", "from", "as", "be", "been"}
        words = re.findall(r'\b[a-zA-Z]{4,}\b', abstract.lower())
        freq: Dict[str, int] = {}
        for w in words:
            if w not in stop_words:
                freq[w] = freq.get(w, 0) + 1
        sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [w for w, _ in sorted_words[:15]]

    def extract_references(self, text: str) -> List[Dict[str, Any]]:
        ref_section = re.search(
            r'(?:References|REFERENCES|Bibliography)\s*\n(.*?)$',
            text, re.DOTALL | re.IGNORECASE
        )
        if not ref_section:
            return []
        refs_text = ref_section.group(1)
        raw_refs = re.split(r'\n\[?\d+\]?[\.\s]+', refs_text)
        parsed = []
        for ref in raw_refs[:100]:
            ref = ref.strip()
            if len(ref) < 20:
                continue
            authors = re.findall(r'[A-Z][a-z]+,?\s+[A-Z]\.?', ref)
            year_match = re.search(r'\b(19|20)\d{2}\b', ref)
            parsed.append({
                "raw": ref,
                "authors": authors[:5],
                "year": year_match.group() if year_match else None,
                "title": ref[:200],
            })
        return parsed
