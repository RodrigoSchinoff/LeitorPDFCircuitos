import os
import tkinter as tk
from tkinter import filedialog
from pdf2image import convert_from_path
import cv2
import pytesseract
import numpy as np

# Se necessário, ajuste o caminho abaixo para onde o Tesseract está instalado:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def select_pdf():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Selecione o PDF",
        filetypes=[("PDF files", "*.pdf")]
    )
    return file_path

def main():
    pdf_path = select_pdf()
    if not pdf_path:
        print("Nenhum PDF selecionado.")
        return

    # Converte a primeira página do PDF para imagem
    images = convert_from_path(pdf_path, dpi=300)
    img = np.array(images[0])
    cv2.imwrite("pagina.png", cv2.cvtColor(img, cv2.COLOR_RGB2BGR))

    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    _, binary = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)

    # Morfologia para fechar pequenas lacunas
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
    closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)

    # Busca apenas contornos externos (grandes blocos/células)
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cels = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        # Ajuste aqui para pegar as células grandes (modifique se necessário)
        if 100 < w < 1000 and 30 < h < 400:
            cels.append((x, y, w, h))
            print(f"Celula: w={w}, h={h}, x={x}, y={y}")

    print(f"Total de células detectadas: {len(cels)}")

    if len(cels) == 0:
        print("\n⚠️ Nenhuma célula detectada! Ajuste os parâmetros de tamanho na linha:")
        print("if 100 < w < 1000 and 30 < h < 400:  # <-- MUDE ESSES VALORES!\n")
        return

    # (Opcional) Gera imagem de debug com caixas desenhadas nas células
    debug_img = img.copy()
    for (x, y, w, h) in cels:
        cv2.rectangle(debug_img, (x, y), (x + w, y + h), (0, 0, 255), 2)
    cv2.imwrite("debug_celulas.png", cv2.cvtColor(debug_img, cv2.COLOR_RGB2BGR))

    # Ordena as células de cima para baixo, esquerda para direita
    cels_sorted = sorted(cels, key=lambda b: (b[1], b[0]))

    # Estimativa da matriz (apenas para organizar nomes, pode ser ajustada)
    num_cols = 2  # geralmente 2: entrada e saída (input/output)
    num_linhas = len(cels_sorted) // num_cols if num_cols else 0

    col_labels = [chr(65 + i) for i in range(num_cols)]
    row_labels = [str(i+1).zfill(2) for i in range(num_linhas)]

    resultado = []
    n_linha_txt = 4
    for idx, (x, y, w, h) in enumerate(cels_sorted):
        cell_img = img[y:y+h, x:x+w]
        text = pytesseract.image_to_string(cell_img, config="--psm 6").strip().replace('\n', ' ')
        linha = idx // num_cols
        coluna = idx % num_cols

        if coluna == 0:
            cod = "S10201"  # Input
        elif coluna == num_cols-1:
            cod = "S70110"  # Output
        else:
            cod = "S00000"

        loc = f"{col_labels[coluna]}{row_labels[linha]}"
        if text:
            linha_txt = f"{n_linha_txt}:MTRX:1:@LOC:{loc},{cod}::{text}:@FROM:@TO;"
            resultado.append(linha_txt)
            n_linha_txt += 1

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

    saida = "\n".join(cabecalho + resultado + rodape)
    saida_path = os.path.splitext(pdf_path)[0] + "_OCR.txt"
    with open(saida_path, "w", encoding="utf-8") as f:
        f.write(saida)
    print(f"\nArquivo gerado: {saida_path}")
    print("\nPrévia das primeiras linhas extraídas:\n")
    print("\n".join(resultado[:10]))

if __name__ == "__main__":
    main()
