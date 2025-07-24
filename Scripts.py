import pdfplumber
import tkinter as tk
from tkinter import filedialog
from collections import defaultdict

def selecionar_pdf():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Selecione o PDF",
        filetypes=[("PDF Files", "*.pdf")]
    )
    return file_path

def main():
    pdf_path = selecionar_pdf()
    if not pdf_path:
        print("Nenhum PDF selecionado.")
        return

    conteudo = []
    with pdfplumber.open(pdf_path) as pdf:
        for pagina in pdf.pages:
            linhas = pagina.extract_text().split('\n')
            for linha in linhas:
                linha = linha.strip()
                if linha:
                    conteudo.append(linha)

    totalizador = defaultdict(list)
    for idx, linha in enumerate(conteudo, 1):
        totalizador[linha].append(idx)

    print("\nResumo dos termos encontrados:\n")
    for termo, indices in sorted(totalizador.items(), key=lambda x: -len(x[1])):
        print(f'"{termo}": {len(indices)} vez(es) — Linhas {indices}')

    print("\nTotal de linhas lidas:", len(conteudo))

if __name__ == "__main__":
    main()
