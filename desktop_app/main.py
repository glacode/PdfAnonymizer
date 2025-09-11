# desktop_app/main.py
import tkinter as tk
from tkinter import filedialog, messagebox
from pdfanonymizer.core import PdfAnonymizer

# Hardcoded words to redact
REDACT_WORDS = ["assicurazione","John Doe", "Secret Company", "123 Main St"]

def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    entry_file.delete(0, tk.END)
    entry_file.insert(0, file_path)

def anonymize_pdf():
    input_file = entry_file.get()
    if not input_file:
        messagebox.showwarning("Missing file", "Please select a PDF file.")
        return

    output_file = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
    if not output_file:
        return

    anonymizer = PdfAnonymizer(terms_to_anonymize=REDACT_WORDS)
    anonymizer.anonymize_pdf(input_file, output_file)
    messagebox.showinfo("Done", "Anonymized PDF saved to {}".format(output_file))

root = tk.Tk()
root.title("PDF Anonymizer")

tk.Label(root, text="PDF File:").grid(row=0, column=0, sticky="e")
entry_file = tk.Entry(root, width=50)
entry_file.grid(row=0, column=1)
tk.Button(root, text="Browse", command=select_file).grid(row=0, column=2)

tk.Button(root, text="Anonymize PDF", command=anonymize_pdf).grid(row=2, column=1)

root.mainloop()
