import io
from io import BufferedReader, BytesIO
from pathlib import Path
from typing import IO, Dict, List, Union, Callable, TypedDict, Match
import pdfplumber
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen.canvas import Canvas
import re

MIN_FONT_SIZE: float = 2.0  # minimum font size

PdfInput = Union[str, Path, BytesIO, BufferedReader]
PdfOutput = IO[bytes]  # BytesIO already implements IO[bytes]


class PdfAnonymizerConfig(TypedDict):
    terms_to_anonymize: List[str]
    replacement: str
    anonymize_alphanumeric: bool
    anonymize_letters_special: bool


class PdfAnonymizer:
    def __init__(self, config: PdfAnonymizerConfig) -> None:
        self.config: PdfAnonymizerConfig = {
            "terms_to_anonymize": config.get("terms_to_anonymize", []),
            "replacement": config.get("replacement", "[REDACTED]"),
            "anonymize_alphanumeric": config.get("anonymize_alphanumeric", True),
            "anonymize_letters_special": config.get("anonymize_letters_special", True),
        }

    def should_anonymize(self, word: str, replacement: str) -> bool:
        if len(word) < 6 or replacement in word:
            return False

        has_alpha: bool = any(c.isalpha() for c in word)
        has_digit: bool = any(c.isdigit() for c in word)

        # special chars only if inside the word (not just at start/end)
        middle = word[1:-1] if len(word) > 2 else ""
        has_special: bool = any(not c.isalnum() for c in middle)

        if self.config["anonymize_alphanumeric"] and has_alpha and has_digit:
            return True
        if self.config["anonymize_letters_special"] and has_alpha and has_special:
            return True
        return False

    def anonymize_text(self, text: str) -> str:
        """Replace all terms and apply heuristics, preserving punctuation."""

        # Explicit replacement from config
        replacement: str = self.config.get("replacement", "[REDACTED]")

        # Replace explicit terms with regex \b boundaries
        for term in self.config.get("terms_to_anonymize", []):
            pattern: str = r"\b" + re.escape(term) + r"\b"
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        # Heuristic replacement: match word + optional trailing punctuation
        def repl(m: Match[str]) -> str:
            # Capture groups: word + trailing punctuation
            word: str = m.group(0)
            # punct: str = m.group(2)
            if self.should_anonymize(word, replacement):
                return replacement
            return word

        # Match: (\w[\w\d]*?) = word part, (\W*) = trailing punctuation
        pattern = r"[A-Za-z0-9][A-Za-z0-9@#.!]*"
        return re.sub(pattern, repl, text)

    def draw_anonymized_word(
        self,
        can: Canvas,
        word_info: Dict[str, float],
        page_height: float,
        anonymize_func: Callable[[str], str],
        font_name: str = "Helvetica",
    ) -> None:
        x0: float = float(word_info["x0"])
        y0: float = float(word_info["bottom"])
        word_width: float = float(word_info["width"])
        word_height: float = float(word_info["height"])

        text: str = str(word_info.get("text", ""))
        anonymized_text: str = anonymize_func(text)

        max_font_size: float = word_height
        font_size: float = max_font_size

        text_width: float = stringWidth(anonymized_text, font_name, font_size)
        if text_width > 0:
            font_size *= min(1.0, word_width / text_width)
        font_size = max(MIN_FONT_SIZE, font_size)

        text_width = stringWidth(anonymized_text, font_name, font_size)
        text_x: float = x0 + (word_width - text_width) / 2
        text_y: float = page_height - y0 - (word_height + font_size) / 2

        can.saveState()
        can.setFont(font_name, font_size)
        can.drawString(text_x, text_y, anonymized_text)
        can.restoreState()

    def anonymize_pdf_streams(
        self, input_stream: PdfInput, output_stream: PdfOutput
    ) -> None:
        writer: PdfWriter = PdfWriter()

        with pdfplumber.open(input_stream) as pdf:
            for page in pdf.pages:
                width: float = page.width
                height: float = page.height
                packet: BytesIO = io.BytesIO()
                can: Canvas = canvas.Canvas(packet, pagesize=(width, height))

                for word_info in (
                    page.extract_words(
                        x_tolerance=1.0, keep_blank_chars=True, use_text_flow=True
                    )
                    or []
                ):
                    self.draw_anonymized_word(
                        can, word_info, height, self.anonymize_text
                    )

                can.save()
                packet.seek(0)
                new_pdf: PdfReader = PdfReader(packet)
                writer.add_page(new_pdf.pages[0])

        writer.write(output_stream)  # type: ignore

    def anonymize_pdf(
        self, input_path: Union[str, Path], output_path: Union[str, Path]
    ) -> None:
        input_path = Path(input_path)
        output_path = Path(output_path)

        if not input_path.exists():
            raise FileNotFoundError(f"Input file {input_path} does not exist")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with input_path.open("rb") as f_in, output_path.open("wb") as f_out:
            self.anonymize_pdf_streams(f_in, f_out)
