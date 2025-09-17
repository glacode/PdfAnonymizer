import tkinter as tk
from .gui import PdfAnonymizerApp


def main():
    root = tk.Tk()
    PdfAnonymizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
