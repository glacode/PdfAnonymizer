import io
import tempfile
from pathlib import Path
from pdfanonymizer.core import PdfAnonymizer

def create_sample_pdf() -> bytes:
    """Return bytes of a minimal PDF with some text."""
    from reportlab.pdfgen import canvas
    packet = io.BytesIO()
    can = canvas.Canvas(packet)
    can.drawString(100, 750, "This is a secret document.")
    can.save()
    packet.seek(0)
    return packet.read()

def test_anonymize_pdf_streams():
    pdf_bytes = create_sample_pdf()
    pdf_in = io.BytesIO(pdf_bytes)
    pdf_out = io.BytesIO()

    anonymizer = PdfAnonymizer(terms_to_anonymize=["secret"])
    anonymizer.anonymize_pdf_streams(pdf_in, pdf_out)

    # Check output is not empty
    pdf_out.seek(0)
    output_bytes = pdf_out.read()
    assert len(output_bytes) > 0

def test_anonymize_pdf_with_temp_files():
    pdf_bytes = create_sample_pdf()

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_in, \
         tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_out:

        input_path = Path(tmp_in.name)
        output_path = Path(tmp_out.name)

        # Write sample PDF bytes to input file
        tmp_in.write(pdf_bytes)
        tmp_in.flush()

        anonymizer = PdfAnonymizer(terms_to_anonymize=["secret"])
        anonymizer.anonymize_pdf(input_path, output_path)

        # Check output file exists and is not empty
        assert output_path.exists()
        assert output_path.stat().st_size > 0

# tests/test_breaking.py
def test_word_boundaries_lost():
    # Arrange
    terms_to_anonymize = ["John", "Doe"]
    text = "Hello John Doe!"
    anonymizer = PdfAnonymizer(terms_to_anonymize=terms_to_anonymize)

    # Act
    result = anonymizer.anonymize_text(text)

    # Assert
    # Current behavior may produce "Hello [REDACTED][REDACTED]!"
    # Correct behavior should preserve spaces: "Hello [REDACTED] [REDACTED]!"
    expected = "Hello [REDACTED] [REDACTED]!"
    assert result == expected
