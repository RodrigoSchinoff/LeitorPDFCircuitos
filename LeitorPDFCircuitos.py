import pdfplumber
import pytesseract
import cv2
import re
import tkinter as tk
from tkinter import filedialog
from pdf2image import convert_from_path
import os

# 1. Seleciona o PDF
root = tk.Tk()
root.withdraw()
pdf_path = filedialog.askopenfilename(
    title="Selecione o PDF da matriz lógica",
    filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
)
if not pdf_path:
    print("Nenhum arquivo selecionado.")
    exit()
print(f"PDF selecionado: {pdf_path}")

# 2. Converte a primeira página do PDF em imagem
png_path = "pagina.png"
pages = convert_from_path(pdf_path, dpi=300)
pages[0].save(png_path, "PNG")
print(f"Imagem salva: {png_path}")

# 3. Parâmetros da matriz (Ajuste conforme seu PDF!)
cols = [chr(ord('A') + i) for i in range(26)]
rows = list(range(1, 33))
cell_width = 40      # <-- Ajuste!
cell_height = 25     # <-- Ajuste!
offset_x = 50        # <-- Ajuste!
offset_y = 100       # <-- Ajuste!

# 4. Carrega imagem da página
img = cv2.imread(png_path)
if img is None:
    raise FileNotFoundError("A imagem da página não foi encontrada!")

cabecalho = [
    ":::SOURCE",
    ":FIBD",
    "1:TENK:1:MTX;",
    "2:TMNL:1:T:1:0;",
    "3:ESCA:1:S;"
]
rodape = [
    "41:CLT:HJ:1;",
    "42:CLT:HG:2;"
]

linhas_txt = []
linha_num = 4

# 5. Extrai todos os textos com pdfplumber (para busca por bbox)
with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[0]
    words = page.extract_words()

# 6. Para cada célula da matriz:
for c, col in enumerate(cols):
    for r, row in enumerate(rows):
        x0 = offset_x + c * cell_width
        y0 = offset_y + (row - 1) * cell_height
        x1 = x0 + cell_width
        y1 = y0 + cell_height

        # (A) Busca texto editável com pdfplumber (usando bbox da célula)
        textos_encontrados = []
        for w in words:
            wx0, wx1, wy0, wy1 = w['x0'], w['x1'], w['top'], w['bottom']
            if (x0 <= (wx0 + wx1)/2 <= x1) and (y0 <= (wy0 + wy1)/2 <= y1):
                textos_encontrados.append(w['text'].strip())

        linha_ja_adicionada = False
        for texto in textos_encontrados:
            m = re.match(r"([A-Z0-9_.]+)\s+([A-Z].+)", texto)
            if m:
                tag = m.group(1)
                desc = m.group(2)
                codigo = re.search(r'S\d{5}', texto)
                codigo = codigo.group(0) if codigo else "Sxxxxx"
                linha = f"{linha_num}:MTRX:1:@LOC:{col}{str(row).zfill(2)},{codigo}::{desc},{tag}:@FROM:@TO;"
                linhas_txt.append(linha)
                linha_num += 1
                linha_ja_adicionada = True

        # (B) Se não encontrou texto, tenta OCR na célula para símbolos lógicos ou outros textos
        if not linha_ja_adicionada:
            cell_img = img[y0:y1, x0:x1]
            textos = pytesseract.image_to_string(cell_img, config='--psm 6').split('\n')
            for t in textos:
                t = t.strip()
                if not t:
                    continue
                # Exemplo: busca símbolo lógico e/ou código
                if re.search(r'\b(E|AND|OU|OR)\b', t, re.IGNORECASE):
                    codigo = re.search(r'S\d{5}', t)
                    codigo = codigo.group(0) if codigo else "Sxxxxx"
                    ordem = "8"  # Ajuste a ordem conforme seu caso
                    linha = f"{linha_num}:MTRX:1:@LOC:{col}{str(row).zfill(2)},{codigo}:{ordem}:@FROM:@TO;"
                    linhas_txt.append(linha)
                    linha_num += 1
                m = re.match(r"([A-Z0-9_.]+)\s+([A-Z].+)", t)
                if m:
                    tag = m.group(1)
                    desc = m.group(2)
                    codigo = re.search(r'S\d{5}', t)
                    codigo = codigo.group(0) if codigo else "Sxxxxx"
                    linha = f"{linha_num}:MTRX:1:@LOC:{col}{str(row).zfill(2)},{codigo}::{desc},{tag}:@FROM:@TO;"
                    linhas_txt.append(linha)
                    linha_num += 1

# 7. Escreve o TXT final
saida_txt = "\n".join(cabecalho + linhas_txt + rodape)
saida_arquivo = os.path.splitext(pdf_path)[0] + "_extraido.txt"
with open(saida_arquivo, "w", encoding="utf-8") as f:
    f.write(saida_txt)

print(f"Arquivo TXT gerado: {saida_arquivo}")
