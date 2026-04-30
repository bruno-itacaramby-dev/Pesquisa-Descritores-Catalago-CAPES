"""
Captura a janela do gui_app que esta rodando em background.
Salva como docs/screenshots/<nome>.png

Uso:
    python docs/capturar_janela.py <nome_arquivo>

Ex:
    python docs/capturar_janela.py 02b_scroll_baixo
"""

import os
import sys
import time

import win32gui
import win32con
from PIL import ImageGrab

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "docs", "screenshots")
os.makedirs(OUT_DIR, exist_ok=True)


def main():
    if len(sys.argv) < 2:
        print("uso: python capturar_janela.py <nome_arquivo>")
        sys.exit(1)
    nome = sys.argv[1]
    if not nome.endswith(".png"):
        nome += ".png"

    titulo = "Pesquisa Descritores - Catalogo CAPES"
    hwnd = win32gui.FindWindow(None, titulo)
    if not hwnd:
        # tenta busca parcial
        results = []
        def cb(h, lparam):
            t = win32gui.GetWindowText(h)
            if "Pesquisa" in t and "CAPES" in t:
                results.append((h, t))
        win32gui.EnumWindows(cb, None)
        if results:
            hwnd = results[0][0]
            print(f"Janela encontrada: '{results[0][1]}'")

    if not hwnd:
        print("ERRO: janela nao encontrada. Esta rodando o app?")
        sys.exit(2)

    # Restaura caso esteja minimizada e traz para frente
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    except Exception:
        pass
    try:
        win32gui.SetForegroundWindow(hwnd)
    except Exception:
        pass

    # Aguarda um pouco apos focar
    time.sleep(0.4)

    rect = win32gui.GetWindowRect(hwnd)
    print(f"bbox janela: {rect}")
    img = ImageGrab.grab(bbox=rect)

    out = os.path.join(OUT_DIR, nome)
    img.save(out, "PNG", optimize=True)
    print(f"salvo: {out}")


if __name__ == "__main__":
    main()
