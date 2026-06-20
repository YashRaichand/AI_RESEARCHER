from typing import Dict, Any, List
import re


class CitationGenerator:
    def generate_apa(self, meta: Dict[str, Any]) -> str:
        authors = meta.get("authors", [])
        year = meta.get("year", "n.d.")
        title = meta.get("title", "Untitled")
        journal = meta.get("journal", "")
        volume = meta.get("volume", "")
        pages = meta.get("pages", "")
        doi = meta.get("doi", "")
        author_str = self._format_authors_apa(authors)
        citation = f"{author_str} ({year}). {title}."
        if journal:
            citation += f" *{journal}*"
            if volume:
                citation += f", *{volume}*"
            if pages:
                citation += f", {pages}"
            citation += "."
        if doi:
            citation += f" https://doi.org/{doi}"
        return citation

    def generate_mla(self, meta: Dict[str, Any]) -> str:
        authors = meta.get("authors", [])
        title = meta.get("title", "Untitled")
        journal = meta.get("journal", "")
        year = meta.get("year", "n.d.")
        pages = meta.get("pages", "")
        author_str = self._format_authors_mla(authors)
        citation = f'{author_str} "{title}."'
        if journal:
            citation += f" *{journal}*,"
        citation += f" {year}"
        if pages:
            citation += f", pp. {pages}"
        citation += "."
        return citation

    def generate_ieee(self, meta: Dict[str, Any]) -> str:
        authors = meta.get("authors", [])
        title = meta.get("title", "Untitled")
        journal = meta.get("journal", "")
        year = meta.get("year", "n.d.")
        volume = meta.get("volume", "")
        pages = meta.get("pages", "")
        doi = meta.get("doi", "")
        initials = ", ".join([self._to_initials(a) for a in authors[:6]])
        citation = f'{initials}, "{title},"'
        if journal:
            citation += f" *{journal}*,"
        if volume:
            citation += f" vol. {volume},"
        if pages:
            citation += f" pp. {pages},"
        citation += f" {year}."
        if doi:
            citation += f" doi: {doi}."
        return citation

    def generate_chicago(self, meta: Dict[str, Any]) -> str:
        authors = meta.get("authors", [])
        title = meta.get("title", "Untitled")
        journal = meta.get("journal", "")
        year = meta.get("year", "n.d.")
        pages = meta.get("pages", "")
        author_str = self._format_authors_chicago(authors)
        citation = f'{author_str} "{title}."'
        if journal:
            citation += f" *{journal}*"
        citation += f" ({year})"
        if pages:
            citation += f": {pages}"
        citation += "."
        return citation

    def generate_bibtex(self, meta: Dict[str, Any]) -> str:
        authors = meta.get("authors", [])
        title = meta.get("title", "Untitled")
        year = meta.get("year", "2024")
        journal = meta.get("journal", "")
        doi = meta.get("doi", "")
        key = self._make_bibtex_key(authors, year, title)
        entry_type = "article" if journal else "misc"
        lines = [f"@{entry_type}{{{key},"]
        lines.append(f'  title = {{{title}}},')
        if authors:
            lines.append(f'  author = {{{" and ".join(authors)}}},')
        lines.append(f'  year = {{{year}}},')
        if journal:
            lines.append(f'  journal = {{{journal}}},')
        if doi:
            lines.append(f'  doi = {{{doi}}},')
        lines.append("}")
        return "\n".join(lines)

    def generate_all(self, meta: Dict[str, Any]) -> Dict[str, str]:
        return {
            "apa": self.generate_apa(meta),
            "mla": self.generate_mla(meta),
            "ieee": self.generate_ieee(meta),
            "chicago": self.generate_chicago(meta),
            "bibtex": self.generate_bibtex(meta),
        }

    def _format_authors_apa(self, authors: List[str]) -> str:
        if not authors:
            return "Unknown Author"
        if len(authors) > 7:
            return f"{authors[0]}, et al."
        return ", ".join(authors)

    def _format_authors_mla(self, authors: List[str]) -> str:
        if not authors:
            return "Unknown Author"
        if len(authors) == 1:
            return authors[0]
        return f"{authors[0]}, et al."

    def _format_authors_chicago(self, authors: List[str]) -> str:
        if not authors:
            return "Unknown Author"
        return ", ".join(authors[:3]) + ("." if len(authors) <= 3 else ", et al.")

    def _to_initials(self, name: str) -> str:
        parts = name.split()
        if len(parts) >= 2:
            return f"{' '.join(p[0] + '.' for p in parts[:-1])} {parts[-1]}"
        return name

    def _make_bibtex_key(self, authors: List[str], year: str, title: str) -> str:
        author_part = authors[0].split()[-1].lower() if authors else "unknown"
        title_word = re.sub(r'[^a-z]', '', title.split()[0].lower()) if title else "paper"
        return f"{author_part}{year}{title_word}"
