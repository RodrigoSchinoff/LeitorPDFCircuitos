import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog
from collections import defaultdict
import os
from datetime import datetime

# 🔐 Validação de data
data_limite = datetime(2025, 6, 20)
hoje = datetime.today()

# if hoje >= data_limite:
#     print("⛔ Este script expirou em 20/06/2025 e não pode mais ser executado.")
#     exit()

# Abrir janela para selecionar PDF
root = tk.Tk()
root.withdraw()
root.attributes('-topmost', True)  # Garante que fique no topo
root.lift()
root.focus_force()

pdf_path = filedialog.askopenfilename(
    title="Selecione um PDF", filetypes=[("PDF files", "*.pdf")]
)

if not pdf_path:
    print("Nenhum arquivo selecionado.")
    exit()

base_name = os.path.splitext(os.path.basename(pdf_path))[0]
output_dir = os.path.dirname(pdf_path)
doc = fitz.open(pdf_path)
full_text = ""

def agrupar_por_linha(spans, tolerancia=2):
    linhas = defaultdict(list)
    for span in spans:
        y = round(span["origin"][1] / tolerancia) * tolerancia
        linhas[y].append(span)
    return linhas

for i, page in enumerate(doc):
    page_dict = page.get_text("dict")
    spans = []
    for block in page_dict["blocks"]:
        for line in block.get("lines", []):
            for span in line["spans"]:
                spans.append({
                    "text": span["text"],
                    "origin": span["bbox"][:2]
                })
    linhas = agrupar_por_linha(spans)
    page_text = ""
    for y in sorted(linhas):
        linha = sorted(linhas[y], key=lambda s: s["origin"][0])
        page_text += " ".join(span["text"] for span in linha) + "\n"
    full_text += f"\n--- Página {i+1} ---\n{page_text}"

    # Salvar por página
    with open(os.path.join(output_dir, f"{base_name}_pagina_{i+1}.txt"), "w", encoding="utf-8") as f:
        f.write(page_text)

# Salvar texto completo
with open(os.path.join(output_dir, f"{base_name}.txt"), "w", encoding="utf-8") as f:
    f.write(full_text)

print("✅ Extração concluída.")