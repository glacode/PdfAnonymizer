import io
from pathlib import Path
from typing import List, Union
import pdfplumber
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter


class PdfAnonymizer:
    def __init__(self, terms_to_anonymize: List[str], replacement: str = "[REDACTED]") -> None:
        self.terms_to_anonymize = terms_to_anonymize
        self.replacement = replacement

    def anonymize_text(self, text: str) -> str:
        for term in self.terms_to_anonymize:
            text = text.replace(term, self.replacement)
        return text

    def anonymize_pdf(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path]
    ) -> None:
        input_path = Path(input_path)
        output_path = Path(output_path)

        if not input_path.exists():
            raise FileNotFoundError(f"Input file {input_path} does not exist")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        writer = PdfWriter()

        with pdfplumber.open(str(input_path)) as pdf:
            for _, page in enumerate(pdf.pages):
                width, height = page.width, page.height
                packet = io.BytesIO()
                can = canvas.Canvas(packet, pagesize=(width, height))

                if hasattr(page, 'chars') and page.chars:
                    for char in page.chars:
                        x0 = char['x0']
                        y1 = char['bottom']
                        text = char.get('text', '')
                        anonymized_text = self.anonymize_text(text)
                        can.drawString(x0, height - y1, anonymized_text)

                can.save()
                packet.seek(0)

                new_pdf = PdfReader(packet)
                page_obj = new_pdf.pages[0]
                writer.add_page(page_obj)

        with open(output_path, "wb") as f_out:
            writer.write(f_out)    # type: ignore[arg-type]
