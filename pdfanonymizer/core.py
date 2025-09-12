import io
from io import BufferedReader, BytesIO
from pathlib import Path
from typing import IO, Callable, Dict, List, Union
import pdfplumber
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from PyPDF2 import PdfReader, PdfWriter

MIN_FONT_SIZE: float = 2.0  # minimum font size

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
    
    from reportlab.pdfgen.canvas import Canvas

    def draw_anonymized_word(
        self,
        can: Canvas,
        word_info: Dict[str, float],
        page_height: float,
        anonymize_func: Callable[[str], str],
        font_name: str = "Helvetica"
    ) -> None:
        """
        Draw an anonymized version of a word on a ReportLab canvas,
        centered inside its original bounding box.

        Parameters:
            can: ReportLab canvas
            word_info: dictionary from page.extract_words(), must include
                    keys: "x0", "bottom", "width", "height", "text"
            page_height: total height of the PDF page
            anonymize_func: function to anonymize the text
            font_name: font to use for drawing
        """
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

        # Recompute text width with final font size
        text_width = stringWidth(anonymized_text, font_name, font_size)
        text_x: float = x0 + (word_width - text_width) / 2
        text_y: float = page_height - y0 - (word_height + font_size) / 2  # vertical centering

        can.saveState()
        can.setFont(font_name, font_size)
        can.drawString(text_x, text_y, anonymized_text)
        can.restoreState()

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
                    self.draw_anonymized_word(can, word_info, height, self.anonymize_text)
                    # x0 = float(word_info["x0"])
                    # y0 = float(word_info["bottom"])
                    # text = word_info.get("text", "")
                    # anonymized_text = self.anonymize_text(text)
                    # can.drawString(x0, height - y0, anonymized_text)

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
