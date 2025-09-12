import io
from io import BufferedReader, BytesIO
from pathlib import Path
from typing import IO, List, Union
import pdfplumber
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter


# Inputs accepted by pdfplumber.open
PdfInput = Union[str, Path, BytesIO, BufferedReader]
PdfOutput = IO[bytes]  # BytesIO already implements IO[bytes]


class PdfAnonymizer:
    def __init__(self, terms_to_anonymize: List[str], replacement: str = "[REDACTED]") -> None:
        self.terms_to_anonymize = terms_to_anonymize
        self.replacement = replacement

    def anonymize_text(self, text: str) -> str:
        """Replace all terms in the text with the replacement string."""
        for term in self.terms_to_anonymize:
            text = text.replace(term, self.replacement)
        return text

    def anonymize_pdf_streams(
        self,
        input_stream: PdfInput,
        output_stream: PdfOutput
    ) -> None:
        """
        Core PDF anonymization that works on binary streams.
        """
        writer: PdfWriter = PdfWriter()

        # pdfplumber.open already supports str | Path | BytesIO | BufferedReader
        pdf_file: PdfInput = input_stream

        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                width, height = page.width, page.height
                packet = io.BytesIO()
                can = canvas.Canvas(packet, pagesize=(width, height))

                # Anonymize words
                for word_info in page.extract_words() or []:
                    x0 = float(word_info["x0"])
                    y0 = float(word_info["bottom"])
                    text = word_info.get("text", "")
                    anonymized_text = self.anonymize_text(text)
                    can.drawString(x0, height - y0, anonymized_text)

                can.save()
                packet.seek(0)

                new_pdf = PdfReader(packet)
                writer.add_page(new_pdf.pages[0])

        # Explicitly annotate return type as None for clarity
        writer.write(output_stream)  # type: ignore

    def anonymize_pdf(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path]
    ) -> None:
        """
        File-based PDF anonymization. Opens files as streams and calls `anonymize_pdf_streams`.
        """
        input_path = Path(input_path)
        output_path = Path(output_path)

        if not input_path.exists():
            raise FileNotFoundError(f"Input file {input_path} does not exist")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with input_path.open("rb") as f_in, output_path.open("wb") as f_out:
            self.anonymize_pdf_streams(f_in, f_out)
