import cv2
import numpy as np
from pdf2image import convert_from_path
import os
from tkinter import Tk, filedialog

# --- CONFIGURAÇÕES ---
TEMPLATE_PATH = "template_flipflopT.png"
POPPLER_PATH = r"C:\poppler-24.02.0\Library\bin"  # ajuste para seu PC

def selecionar_pdf():
    root = Tk()
    root.withdraw()
    arquivo_pdf = filedialog.askopenfilename(
        title="Selecione o PDF",
        filetypes=[("PDF files", "*.pdf")],
    )
    return arquivo_pdf

def detectar_template(imagem, template, thres=0.7):
    img_gray = cv2.cvtColor(imagem, cv2.COLOR_RGB2GRAY)
    result = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    locais = np.where(result >= thres)
    pontos = list(zip(*locais[::-1]))
    return pontos

def main():
    pdf_path = selecionar_pdf()
    if not pdf_path:
        print("Nenhum PDF selecionado.")
        return

    # Carrega o template
    template = cv2.imread(TEMPLATE_PATH, cv2.IMREAD_GRAYSCALE)
    if template is None:
        print(f"Template '{TEMPLATE_PATH}' não encontrado!")
        return

    # Converte todas as páginas do PDF
    paginas = convert_from_path(pdf_path, dpi=300, poppler_path=POPPLER_PATH)
    print(f"{len(paginas)} página(s) encontrada(s) no PDF.")

    for idx, pagina_pil in enumerate(paginas):
        img = np.array(pagina_pil)
        pontos = detectar_template(img, template, thres=0.7)
        print(f"\n--- Página {idx+1} ---")
        if pontos:
            print(f"Encontrados {len(pontos)} símbolo(s) FlipFlopT")
            for pt in pontos:
                print(f"  Localização (x={pt[0]}, y={pt[1]})")
                # Desenhar retângulo para visualizar
                h, w = template.shape
                cv2.rectangle(img, pt, (pt[0]+w, pt[1]+h), (0, 0, 255), 2)
        else:
            print("Nenhum símbolo FlipFlopT encontrado!")

        # Salva imagem de depuração
        saida_img = f"pagina_{idx+1}_detected.png"
        cv2.imwrite(saida_img, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        print(f"  Arquivo salvo: {saida_img}")

if __name__ == "__main__":
    main()
