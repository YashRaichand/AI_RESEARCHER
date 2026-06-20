from app.ml.citation_generator import CitationGenerator

SAMPLE = {
    "title": "Attention Is All You Need",
    "authors": ["Vaswani, Ashish", "Shazeer, Noam", "Parmar, Niki"],
    "year": "2017",
    "journal": "NeurIPS",
    "volume": "30",
    "pages": "5998-6008",
    "doi": "10.48550/arXiv.1706.03762"
}

def test_apa():
    gen = CitationGenerator()
    apa = gen.generate_apa(SAMPLE)
    assert "Vaswani" in apa
    assert "2017" in apa
    assert "Attention" in apa

def test_ieee():
    gen = CitationGenerator()
    ieee = gen.generate_ieee(SAMPLE)
    assert "Attention Is All You Need" in ieee

def test_bibtex():
    gen = CitationGenerator()
    bib = gen.generate_bibtex(SAMPLE)
    assert "@article" in bib
    assert "title" in bib

def test_generate_all():
    gen = CitationGenerator()
    all_formats = gen.generate_all(SAMPLE)
    assert set(all_formats.keys()) == {"apa", "mla", "ieee", "chicago", "bibtex"}
    for v in all_formats.values():
        assert len(v) > 10
