import io
import tempfile
from pathlib import Path
from pdfanonymizer.core import PdfAnonymizer, PdfAnonymizerConfig

def create_sample_pdf() -> bytes:
    """Return bytes of a minimal PDF with some text."""
    from reportlab.pdfgen import canvas
    packet = io.BytesIO()
    can = canvas.Canvas(packet)
    can.drawString(100, 750, "This is a secret document.")
    can.save()
    packet.seek(0)
    return packet.read()

def make_config(terms: list[str]) -> PdfAnonymizerConfig:
    """Helper to create a TypedDict config with all keys set."""
    return {
        "terms_to_anonymize": terms,
        "replacement": "[REDACTED]",
        "anonymize_alphanumeric": True,
        "anonymize_letters_special": True,
    }

def test_anonymize_pdf_streams():
    pdf_bytes = create_sample_pdf()
    pdf_in = io.BytesIO(pdf_bytes)
    pdf_out = io.BytesIO()

    # Instantiate PdfAnonymizer with TypedDict config
    anonymizer = PdfAnonymizer(make_config(["secret"]))
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

        # Instantiate PdfAnonymizer with TypedDict config
        anonymizer = PdfAnonymizer(make_config(["secret"]))
        anonymizer.anonymize_pdf(input_path, output_path)

        # Check output file exists and is not empty
        assert output_path.exists()
        assert output_path.stat().st_size > 0

def test_first_and_final_terms_are_anonymized():
    # Arrange
    terms_to_anonymize = ["Hello", "Doe"]
    text = "Hello John Doe"
    anonymizer = PdfAnonymizer(make_config(terms_to_anonymize))

    # Act
    result = anonymizer.anonymize_text(text)

    expected = "[REDACTED] John [REDACTED]"
    assert result == expected


# tests/test_breaking.py
def test_word_boundaries_lost():
    # Arrange
    terms_to_anonymize = ["John", "Doe"]
    text = "Hello John Doe!"
    anonymizer = PdfAnonymizer(make_config(terms_to_anonymize))

    # Act
    result = anonymizer.anonymize_text(text)

    # Assert
    # Current behavior may produce "Hello [REDACTED][REDACTED]!"
    # Correct behavior should preserve spaces: "Hello [REDACTED] [REDACTED]!"
    expected = "Hello [REDACTED] [REDACTED]!"
    assert result == expected

# anonymize full word only
def test_anonimize_full_word_only():
    # Arrange
    terms_to_anonymize = ["fix"]
    text = "fix and suffix"
    anonymizer = PdfAnonymizer(make_config(terms_to_anonymize))

    # Act
    result = anonymizer.anonymize_text(text)

    # Assert
    expected = "[REDACTED] and suffix"
    assert result == expected

# anonymize is not case sensitive
def test_anonimize_is_not_case_sensitive():
    # Arrange
    terms_to_anonymize = ["fix"]
    text = "fix and Fix"
    anonymizer = PdfAnonymizer(make_config(terms_to_anonymize))

    # Act
    result = anonymizer.anonymize_text(text)

    # Assert
    expected = "[REDACTED] and [REDACTED]"
    assert result == expected

# anonymize does not break words with punctuation
def test_anonimize_does_not_break_words_with_punctuation():
    # Arrange
    terms_to_anonymize = ["fix"]
    text = "fix, and ,fix and fix."
    anonymizer = PdfAnonymizer(make_config(terms_to_anonymize))

    # Act
    result = anonymizer.anonymize_text(text)

    # Assert
    expected = "[REDACTED], and ,[REDACTED] and [REDACTED]."
    assert result == expected

# anonymize does not break words with new lines
def test_anonimize_does_not_break_words_with_new_lines():
    # Arrange
    terms_to_anonymize = ["fix"]
    text = """\
fix
and
fix"""
    anonymizer = PdfAnonymizer(make_config(terms_to_anonymize))

    # Act
    result = anonymizer.anonymize_text(text)

    # Assert
    expected = "[REDACTED]\nand\n[REDACTED]"
    assert result == expected

# anonymize does not break words with tabs
def test_anonimize_does_not_break_words_with_tabs():
    # Arrange
    terms_to_anonymize = ["fix"]
    text = "fix\tand\tfix"
    anonymizer = PdfAnonymizer(make_config(terms_to_anonymize))

    # Act
    result = anonymizer.anonymize_text(text)

    # Assert
    expected = "[REDACTED]\tand\t[REDACTED]"
    assert result == expected

# anonymize does not break words with multiple spaces
def test_anonimize_does_not_break_words_with_multiple_spaces():
    # Arrange
    terms_to_anonymize = ["fix"]
    text = "fix  and   fix"
    anonymizer = PdfAnonymizer(make_config(terms_to_anonymize))

    # Act
    result = anonymizer.anonymize_text(text)

    # Assert
    expected = "[REDACTED]  and   [REDACTED]"
    assert result == expected

# anonymize does not break words with hyphens
def test_anonimize_does_not_break_words_with_hyphens():
    # Arrange
    terms_to_anonymize = ["fix"]
    text = "fix-and-fix"
    anonymizer = PdfAnonymizer(make_config(terms_to_anonymize))

    # Act
    result = anonymizer.anonymize_text(text)

    # Assert
    expected = "[REDACTED]-and-[REDACTED]"
    assert result == expected

def test_no_anonimization_if_special_character_only_at_start_or_end():
    # Arrange
    terms_to_anonymize = ["none"]
    text = "-JohnLongLong ,middleLongLong, DoeLongLong."
    anonymizer = PdfAnonymizer(make_config(terms_to_anonymize))

    # Act
    result = anonymizer.anonymize_text(text)

    # Assert
    assert result == "-JohnLongLong ,middleLongLong, DoeLongLong."

# test anonymize_alphanumeric
def test_anonymize_alphanumeric():
    # Arrange
    terms_to_anonymize: list[str]  = []
    text = "My code is abc123 and xy6z890."
    config = make_config(terms_to_anonymize)
    config["anonymize_alphanumeric"] = True
    anonymizer = PdfAnonymizer(config)

    # Act
    result = anonymizer.anonymize_text(text)

    # Assert
    expected = "My code is [REDACTED] and [REDACTED]"
    assert result == expected

# test anonymize_letters_special
def test_anonymize_letters_special():
    # Arrange
    terms_to_anonymize: list[str]  = []
    text = "My password is pass@word! and hello#world."
    config = make_config(terms_to_anonymize)
    config["anonymize_letters_special"] = True
    anonymizer = PdfAnonymizer(config)

    # Act
    result = anonymizer.anonymize_text(text)

    # Assert
    expected = "My password is [REDACTED] and [REDACTED]"
    assert result == expected