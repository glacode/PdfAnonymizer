import os
import tkinter as tk
from tkinter import filedialog, messagebox
from pdfanonymizer.core import PdfAnonymizer, PdfAnonymizerConfig

from .config_sample import REDACT_WORDS as sample_words, HEURISTIC_RULES as sample_rules

try:
    from .config_local import (
        REDACT_WORDS as local_words,
        HEURISTIC_RULES as local_rules,
    )
except ImportError:
    local_words = None
    local_rules = {}


def build_config() -> PdfAnonymizerConfig:
    terms_to_anonymize = local_words if local_words is not None else sample_words
    heuristic_rules = {**sample_rules, **local_rules}
    return {
        "terms_to_anonymize": terms_to_anonymize,
        "replacement": "[REDACTED]",
        "anonymize_alphanumeric": heuristic_rules.get("alphanumeric_words", True),
        "anonymize_letters_special": heuristic_rules.get("letters_special_chars", True),
        "anonymize_numeric_codes": heuristic_rules.get("numeric_codes", True),
    }


class FileSelector:
    @staticmethod
    def select_pdf_file(entry_widget: tk.Entry):
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        file_path = filedialog.askopenfilename(
            initialdir=desktop, filetypes=[("PDF Files", "*.pdf")]
        )
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, file_path)

    @staticmethod
    def get_output_filename(input_file: str) -> str:
        input_basename = os.path.splitext(os.path.basename(input_file))[0]
        default_output = f"{input_basename}_anonymized.pdf"
        return filedialog.asksaveasfilename(
            initialdir=os.path.dirname(input_file) or os.getcwd(),
            initialfile=default_output,
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
        )


class PdfAnonymizerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.config = build_config()
        self.setup_gui()

    def setup_gui(self):
        self.root.title("PDF Anonymizer")
        tk.Label(self.root, text="PDF File:").grid(row=0, column=0, sticky="e")
        self.entry_file = tk.Entry(self.root, width=50)
        self.entry_file.grid(row=0, column=1)
        tk.Button(self.root, text="Browse", command=self.select_file).grid(
            row=0, column=2
        )
        tk.Button(self.root, text="Anonymize PDF", command=self.anonymize_pdf).grid(
            row=2, column=1
        )

    def select_file(self):
        FileSelector.select_pdf_file(self.entry_file)

    def anonymize_pdf(self):
        input_file = self.entry_file.get()
        if not input_file:
            messagebox.showwarning("Missing file", "Please select a PDF file.")
            return
        output_file = FileSelector.get_output_filename(input_file)
        if not output_file:
            return
        anonymizer = PdfAnonymizer(self.config)
        anonymizer.anonymize_pdf(input_file, output_file)
        messagebox.showinfo("Done", f"Anonymized PDF saved to {output_file}")


def main():
    root = tk.Tk()
    PdfAnonymizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
