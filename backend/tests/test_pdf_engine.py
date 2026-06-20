import os
import tempfile
from app.ml.pdf_engine import PDFEngine

def test_extract_txt():
    engine = PDFEngine()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("Introduction\nThis is a test paper about machine learning.\n\nReferences\n[1] Test ref")
        path = f.name
    try:
        result = engine.extract(path, "txt")
        assert result["word_count"] > 0
        assert "full_text" in result
    finally:
        os.unlink(path)

def test_detect_equations():
    engine = PDFEngine()
    text = "The loss L = x^2 + y^2 and E=mc^2 are key formulas."
    eqs = engine.detect_equations(text)
    assert isinstance(eqs, list)

def test_extract_keywords():
    from app.ml.paper_parser import ScientificPaperParser
    parser = ScientificPaperParser()
    abstract = "Deep learning transformer attention mechanism self-attention neural network language model"
    kws = parser.extract_keywords(abstract)
    assert len(kws) > 0
    assert isinstance(kws[0], str)
