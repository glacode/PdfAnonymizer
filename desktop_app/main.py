import os
import tkinter as tk
from tkinter import filedialog, messagebox
from pdfanonymizer.core import PdfAnonymizer, PdfAnonymizerConfig

# --- Load default/sample config ---
from .config_sample import REDACT_WORDS as sample_words, HEURISTIC_RULES as sample_rules

# --- Load local overrides if present ---
try:
    from .config_local import (
        REDACT_WORDS as local_words,
        HEURISTIC_RULES as local_rules,
    )
except ImportError:
    local_words = None
    local_rules = {}

# Merge words: local overrides take precedence
terms_to_anonymize = local_words if local_words is not None else sample_words

# Merge heuristic rules: local overrides take precedence
heuristic_rules = {**sample_rules, **local_rules}

# Build final TypedDict config for PdfAnonymizer
config: PdfAnonymizerConfig = {
    "terms_to_anonymize": terms_to_anonymize,
    "replacement": "[REDACTED]",
    "anonymize_alphanumeric": heuristic_rules.get("alphanumeric_words", True),
    "anonymize_letters_special": heuristic_rules.get("letters_special_chars", True),
    "anonymize_numeric_codes": heuristic_rules.get("numeric_codes", True),
}


# --- GUI callbacks ---
def select_file():
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    file_path = filedialog.askopenfilename(
        initialdir=desktop, filetypes=[("PDF Files", "*.pdf")]
    )
    entry_file.delete(0, tk.END)
    entry_file.insert(0, file_path)


def anonymize_pdf():
    input_file = entry_file.get()
    if not input_file:
        messagebox.showwarning("Missing file", "Please select a PDF file.")
        return
    # Create default output filename from input filename
    input_basename = os.path.splitext(os.path.basename(input_file))[0]
    default_output = f"{input_basename}_anonymized.pdf"
    output_file = filedialog.asksaveasfilename(
        initialdir=os.path.dirname(input_file) or os.getcwd(),
        initialfile=default_output,
        defaultextension=".pdf",
        filetypes=[("PDF Files", "*.pdf")],
    )
    if not output_file:
        return

    anonymizer = PdfAnonymizer(config)
    anonymizer.anonymize_pdf(input_file, output_file)
    messagebox.showinfo("Done", f"Anonymized PDF saved to {output_file}")


# --- GUI layout ---
root = tk.Tk()
root.title("PDF Anonymizer")

tk.Label(root, text="PDF File:").grid(row=0, column=0, sticky="e")
entry_file = tk.Entry(root, width=50)
entry_file.grid(row=0, column=1)
tk.Button(root, text="Browse", command=select_file).grid(row=0, column=2)

tk.Button(root, text="Anonymize PDF", command=anonymize_pdf).grid(row=2, column=1)

root.mainloop()
