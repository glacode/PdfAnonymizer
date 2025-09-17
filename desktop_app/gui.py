import tkinter as tk
from tkinter import messagebox
from pdfanonymizer.core import PdfAnonymizer

from .config_loader import build_config
from .file_selector import FileSelector


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
