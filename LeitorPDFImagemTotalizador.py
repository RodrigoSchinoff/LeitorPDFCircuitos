import tkinter as tk
from tkinter import filedialog
from collections import defaultdict
from pdf2image import convert_from_path
import pytesseract
import os
import tempfile

# Se necessário, aponte para o executável do Tesseract:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def selecionar_pdf():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Selecione o PDF (imagem)",
        filetypes=[("PDF Files", "*.pdf")]
    )
    return file_path

def main():
    pdf_path = selecionar_pdf()
    if not pdf_path:
        print("Nenhum PDF selecionado.")
        return

    conteudo = []
    print("Convertendo PDF para imagens...")
    with tempfile.TemporaryDirectory() as tempdir:
        pages = convert_from_path(pdf_path, dpi=400, output_folder=tempdir)
        print(f"{len(pages)} página(s) encontrada(s) no PDF.")

        for i, img in enumerate(pages, 1):
            print(f"OCR página {i}...")
            texto = pytesseract.image_to_string(img, lang="por")  # ou 'eng' se o texto for inglês
            linhas = [linha.strip() for linha in texto.split('\n') if linha.strip()]
            conteudo.extend(linhas)

    # Totalizador por linha
    totalizador = defaultdict(list)
    for idx, linha in enumerate(conteudo, 1):
        totalizador[linha].append(idx)

    print("\nResumo dos termos encontrados via OCR:\n")
    for termo, indices in sorted(totalizador.items(), key=lambda x: -len(x[1])):
        print(f'"{termo}": {len(indices)} vez(es) — Linhas {indices}')

    print("\nTotal de linhas OCR lidas:", len(conteudo))

if __name__ == "__main__":
    main()
