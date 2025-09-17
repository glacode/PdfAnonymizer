import os
import tkinter as tk
from tkinter import filedialog


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
