# PdfAnonymizer

PdfAnonymizer is a lightweight Python tool to **anonymize PDF documents** by replacing sensitive terms with a custom placeholder. It works as a **Python library** and a **desktop GUI application**.

---

## Features

- Anonymize PDFs based on a list of sensitive words.
- Works on PDFs in **file-based** or **in-memory streams**.
- Preserves original layout, word positions, and page sizes.
- Supports custom replacement text (default: `[REDACTED]`).
- Includes a simple **Tkinter GUI**.
- Supports local and sample configuration for flexible word lists.

---

## Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/glacode/PdfAnonymizer.git
cd PdfAnonymizer
pip install -r requirements.txt
```

For editable mode:

```bash
pip install -e .
```

---

## Usage

### Python Library

```python
from pdfanonymizer.core import PdfAnonymizer

# List of words to redact
terms_to_anonymize = ["John Doe", "Secret Company", "123 Main St"]

anonymizer = PdfAnonymizer(terms_to_anonymize)
anonymizer.anonymize_pdf("input.pdf", "output.pdf")
```

### Desktop GUI

```bash
python -m desktop_app.main
```

- Click **Browse** to select a PDF.
- Click **Anonymize PDF** to save the anonymized version.

---

## Configuration

- **Sample config:** `desktop_app/config_sample.py` contains example words.
- **Local config (optional):** `desktop_app/config_local.py` can override sample config.  
  **Note:** This file is ignored by Git to keep sensitive words private.

```python
# config_sample.py
REDACT_WORDS = ["John Doe", "Secret Company", "123 Main St"]

# config_local.py
REDACT_WORDS = ["Private Word"]
```

The application merges `config_sample` and `config_local` automatically.

---

## Testing

Run tests with **pytest**:

```bash
pytest
```

Tests are fully in-memory and do not require writing files to disk.

---

## Dependencies

- Python ≥ 3.8
- [pdfplumber](https://github.com/jsvine/pdfplumber)
- [PyPDF2](https://pypi.org/project/PyPDF2/)
- [reportlab](https://www.reportlab.com/)
- Tkinter (for GUI)

Install all dependencies:

```bash
pip install pdfplumber PyPDF2 reportlab
```

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Author

Glauco Siliprandi  
[GitHub Profile](https://github.com/glacode)
