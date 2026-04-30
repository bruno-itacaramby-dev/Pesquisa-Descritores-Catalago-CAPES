"""
Gera os screenshots usados no README.md em docs/screenshots/.

Manipula o estado da GUI direto (sem rodar a coleta real) para simular
cada etapa do fluxo, captura a janela e desenha anotacoes (setas + caixas)
com PIL.

Como usar:
    python docs/gerar_screenshots.py
"""

import os
import sys
import time

# Permite importar gui_app a partir da pasta raiz
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from PIL import Image, ImageDraw, ImageFont
import gui_app

OUT_DIR = os.path.join(ROOT, "docs", "screenshots")
os.makedirs(OUT_DIR, exist_ok=True)

# ============================================================
# HELPERS
# ============================================================

def _wait(app, ms=400):
    """Aguarda ms milissegundos processando eventos da UI."""
    end = time.time() + (ms / 1000.0)
    while time.time() < end:
        app.update_idletasks()
        app.update()


def _grab_window(app):
    """Captura a janela atual do app como PIL.Image."""
    from PIL import ImageGrab
    app.update_idletasks()
    app.update()
    x = app.winfo_rootx()
    y = app.winfo_rooty()
    w = app.winfo_width()
    h = app.winfo_height()
    img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
    # Remove os ultimos pixels (barra de tarefas que pode ter vazado em capturas com DPI)
    crop_bottom = 60
    img = img.crop((0, 0, img.size[0], max(100, img.size[1] - crop_bottom)))
    return img


def _font(size=18, bold=False):
    """Retorna uma fonte legivel (Segoe UI no Windows)."""
    candidates = [
        ("segoeuib.ttf" if bold else "segoeui.ttf", size),
        ("arial.ttf", size),
    ]
    for name, sz in candidates:
        try:
            return ImageFont.truetype(name, sz)
        except OSError:
            continue
    return ImageFont.load_default()


# ----- desenho de anotacoes -----
RED = (220, 38, 38)
YELLOW = (251, 191, 36)
GREEN = (34, 197, 94)
WHITE = (255, 255, 255)
SHADOW = (0, 0, 0)


def draw_box(img, xy, color=RED, width=4, label=None, label_pos="top"):
    """Desenha uma caixa vermelha. Opcionalmente um label numerado."""
    draw = ImageDraw.Draw(img)
    x1, y1, x2, y2 = xy
    draw.rectangle((x1, y1, x2, y2), outline=color, width=width)
    if label:
        font = _font(20, bold=True)
        # background pill
        bbox = font.getbbox(str(label))
        tw = bbox[2] - bbox[0] + 14
        th = bbox[3] - bbox[1] + 8
        if label_pos == "top":
            lx, ly = x1 - 4, y1 - th - 2
        elif label_pos == "left":
            lx, ly = x1 - tw - 4, y1
        elif label_pos == "right":
            lx, ly = x2 + 4, y1
        else:
            lx, ly = x1, y2 + 2
        draw.rounded_rectangle((lx, ly, lx + tw, ly + th), radius=6, fill=color)
        draw.text((lx + 7, ly + 2), str(label), fill=WHITE, font=font)


def draw_arrow(img, start, end, color=RED, width=5):
    """Desenha uma seta com cabeca."""
    draw = ImageDraw.Draw(img)
    draw.line([start, end], fill=color, width=width)
    # Cabeca da seta
    import math
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    head_len = 18
    for off in (-math.pi / 7, math.pi / 7):
        hx = end[0] - head_len * math.cos(angle + off)
        hy = end[1] - head_len * math.sin(angle + off)
        draw.line([end, (hx, hy)], fill=color, width=width)


def draw_caption(img, xy, text, color=YELLOW, font_size=22):
    """Desenha um texto com sombra para legenda."""
    draw = ImageDraw.Draw(img)
    font = _font(font_size, bold=True)
    x, y = xy
    # Sombra
    draw.text((x + 2, y + 2), text, fill=SHADOW, font=font)
    draw.text((x, y), text, fill=color, font=font)


def widget_bbox(app, widget, expand=4):
    """Retorna o bbox de um widget relativo a janela (com pequena margem)."""
    app.update_idletasks()
    rx = widget.winfo_rootx() - app.winfo_rootx()
    ry = widget.winfo_rooty() - app.winfo_rooty()
    rw = widget.winfo_width()
    rh = widget.winfo_height()
    return (rx - expand, ry - expand, rx + rw + expand, ry + rh + expand)


def save(img, name, crop=None):
    """Salva a imagem em docs/screenshots/<name>.

    crop: pode ser
       - None (nao corta)
       - "left": pega a metade esquerda (com 40px de folga ao centro)
       - "right": pega a metade direita
       - tupla (l, t, r, b): coordenadas absolutas
    """
    if crop:
        w, h = img.size
        if crop == "left":
            img = img.crop((0, 0, w // 2 + 60, h))
        elif crop == "right":
            # comeca um pouco antes da metade para nao cortar titulos com padx
            img = img.crop((max(0, w // 2 - 80), 0, w, h))
        elif isinstance(crop, tuple):
            img = img.crop(crop)
    path = os.path.join(OUT_DIR, name)
    img.save(path, "PNG", optimize=True)
    print(f"  + {path}")
    return path


# ============================================================
# MOCKS
# ============================================================

def mock_agregacoes():
    """Agregacoes fake para o painel de sugestoes."""
    return [
        {
            "campo": "Grande Àrea Conhecimento",
            "total": 1,
            "agregados": [{"valor": "CIÊNCIAS HUMANAS", "total": 350}],
        },
        {
            "campo": "Área Conhecimento",
            "total": 1,
            "agregados": [{"valor": "EDUCAÇÃO", "total": 350}],
        },
        {
            "campo": "Nome Programa",
            "total": 4,
            "agregados": [
                {"valor": "EDUCAÇÃO", "total": 187},
                {"valor": "Educação", "total": 92},
                {"valor": "EDUCAÇÃO ESCOLAR", "total": 38},
                {"valor": "EDUCAÇÃO BÁSICA", "total": 33},
            ],
        },
        {
            "campo": "Ano",
            "total": 5,
            "agregados": [
                {"valor": "2023", "total": 71},
                {"valor": "2022", "total": 64},
                {"valor": "2021", "total": 57},
                {"valor": "2020", "total": 45},
                {"valor": "2019", "total": 39},
            ],
        },
        {
            "campo": "Grau Acadêmico",
            "total": 2,
            "agregados": [
                {"valor": "Mestrado", "total": 218},
                {"valor": "Doutorado", "total": 132},
            ],
        },
    ]


# ============================================================
# CENAS
# ============================================================

def _find_section_titles(app):
    """Retorna lista (idx, label_widget) dos titulos numerados '1. ', '2. ', ..."""
    found = []
    def walk(w):
        for c in w.winfo_children():
            if c.__class__.__name__ == "CTkLabel":
                txt = (c.cget("text") or "")
                if any(txt.startswith(p) for p in ("1. ", "2. ", "3. ", "4. ", "5. ")):
                    found.append((txt, c))
            walk(c)
    walk(app)
    found.sort(key=lambda t: t[0])
    return found


def _scroll_left(app, frac):
    """Rola o scrollable da coluna esquerda. frac=0.0 topo, 1.0 fim."""
    if hasattr(app, "left_scroll"):
        canvas = app.left_scroll._parent_canvas
        canvas.update_idletasks()
        canvas.yview_moveto(frac)
        canvas.update_idletasks()


def cena_01_tela_inicial(app):
    """Tela inicial com numeracao das secoes 1-3 (parte superior)."""
    _scroll_left(app, 0.0)
    _settle(app)
    img = _grab_window(app)

    titles = _find_section_titles(app)
    # Numera so os que estao visiveis (acima do limite vertical)
    img_h = img.size[1]
    for idx, (txt, lbl) in enumerate(titles, start=1):
        card = lbl.master
        bbox = widget_bbox(app, card, expand=2)
        # so anota se o topo do card esta visivel
        if bbox[1] < img_h - 80:
            draw_box(img, bbox, color=YELLOW, width=3,
                     label=str(idx), label_pos="left")

    save(img, "01_tela_inicial.png")


def cena_02_termo_filtros(app):
    """Termo preenchido + filtros — destaque no campo termo e nos filtros."""
    _scroll_left(app, 0.0)
    _settle(app)
    img = _grab_window(app)

    termo_bbox = widget_bbox(app, app.termo_entry, expand=4)
    draw_box(img, termo_bbox, color=RED, width=4)

    if app.filter_rows:
        first = app.filter_rows[0]
        last = app.filter_rows[-1]
        x1 = first.winfo_rootx() - app.winfo_rootx() - 8
        y1 = first.winfo_rooty() - app.winfo_rooty() - 8
        x2 = last.winfo_rootx() - app.winfo_rootx() + last.winfo_width() + 8
        y2 = last.winfo_rooty() - app.winfo_rooty() + last.winfo_height() + 8
        draw_box(img, (x1, y1, x2, y2), color=RED, width=4)

    save(img, "02_termo_e_filtros.png", crop="left")


def cena_02b_botoes(app):
    """Mostra a parte inferior com botoes ANALISAR/EXECUTAR/PARAR (apos scroll)."""
    _scroll_left(app, 1.0)
    _settle(app)
    img = _grab_window(app)

    # Seta grande apontando ANALISAR
    btn_bbox = widget_bbox(app, app.btn_analisar, expand=4)
    draw_box(img, btn_bbox, color=GREEN, width=5)
    cx = (btn_bbox[0] + btn_bbox[2]) // 2
    arr_start = (cx, btn_bbox[1] - 80)
    arr_end = (cx, btn_bbox[1] - 8)
    draw_arrow(img, arr_start, arr_end, color=GREEN, width=6)
    draw_caption(img, (cx - 80, arr_start[1] - 30),
                 "Clique para analisar", color=GREEN, font_size=20)

    save(img, "02b_botao_analisar.png", crop="left")


def cena_03_analise(app):
    """Apos ANALISAR — mostra total e sugestoes."""
    # Simula resultado da analise sem rodar request real
    app._show_analyze_result(350, mock_agregacoes())
    app._log("Analisando termo 'gerencialismo' com 3 filtro(s)...", "info")
    app._log("Resposta recebida em 0.84s. Total de resultados: 350", "success")
    _settle(app)

    img = _grab_window(app)

    # Caixa em volta do total
    total_bbox = widget_bbox(app, app.total_label, expand=2)
    draw_box(img, total_bbox, color=GREEN, width=4)
    draw_caption(img, (total_bbox[0], total_bbox[3] + 6),
                 "Total de teses que serao coletadas",
                 color=GREEN, font_size=15)

    # Caixa nas sugestoes
    sug_bbox = widget_bbox(app, app.agregacoes_frame, expand=2)
    draw_box(img, sug_bbox, color=YELLOW, width=3)
    draw_caption(img, (sug_bbox[0], sug_bbox[1] - 26),
                 "Sugestoes de filtros — clique em + para refinar a busca",
                 color=YELLOW, font_size=15)

    # Seta apontando pro botao EXECUTAR
    btn_bbox = widget_bbox(app, app.btn_executar, expand=2)
    draw_box(img, btn_bbox, color=GREEN, width=4)
    arr_start = (btn_bbox[0] + (btn_bbox[2] - btn_bbox[0]) // 2, btn_bbox[1] - 60)
    arr_end = (btn_bbox[0] + (btn_bbox[2] - btn_bbox[0]) // 2, btn_bbox[1] - 4)
    draw_arrow(img, arr_start, arr_end, color=GREEN, width=5)
    draw_caption(img, (arr_start[0] - 100, arr_start[1] - 22),
                 "Agora clique em EXECUTAR",
                 color=GREEN, font_size=16)

    save(img, "03_analise.png", crop="right")


def cena_04_execucao(app):
    """Durante a execucao — barra de progresso e log."""
    # Simula progresso na etapa 2
    app.progress.set(0.45)
    app.progress_status.configure(text="45%  •  Extraindo resumos - 26/57 (ETA 38s)")
    app.progress_detail.configure(
        text="A subjetivacao capitalistica como mecanismo de precarizacao do trabalho docente..."
    )
    # Adiciona algumas linhas de log
    app._clear_log()
    log_entries = [
        ("info", "Pasta de saida: C:/Users/Bruno/Documents/.../gerencialismo"),
        ("info", "Etapa 1/3: coletando metadados das teses..."),
        ("success", "Total da API: 350 teses, distribuidas em 18 paginas (20 por pagina)"),
        ("info", "Etapa 1/3 concluida: 350 tese(s) coletada(s)"),
        ("info", "Etapa 2/3: extraindo palavras-chave e resumos de 350 tese(s)..."),
    ]
    for level, text in log_entries:
        app._log(text, level)
    _settle(app)

    img = _grab_window(app)

    # Caixa na barra de progresso
    prog_bbox = widget_bbox(app, app.progress, expand=4)
    draw_box(img, prog_bbox, color=GREEN, width=3)

    # Caixa no status detalhado
    status_bbox = widget_bbox(app, app.progress_status, expand=2)
    detail_bbox = widget_bbox(app, app.progress_detail, expand=2)
    full_bbox = (
        min(status_bbox[0], detail_bbox[0]),
        status_bbox[1],
        max(status_bbox[2], detail_bbox[2]),
        detail_bbox[3],
    )
    draw_box(img, full_bbox, color=YELLOW, width=3)
    draw_caption(img, (full_bbox[0], full_bbox[3] + 4),
                 "Status atual + ETA + tese sendo processada",
                 color=YELLOW, font_size=14)

    # Caixa no log
    log_bbox = widget_bbox(app, app.log_text, expand=4)
    draw_box(img, log_bbox, color=RED, width=3)
    draw_caption(img, (log_bbox[0], log_bbox[1] - 22),
                 "Log detalhado de cada etapa",
                 color=RED, font_size=14)

    save(img, "04_execucao.png", crop="right")


def cena_05_concluido(app):
    """Estado final — concluido."""
    app.progress.set(1.0)
    app.progress_status.configure(text="Concluido. 350 tese(s) salvas.")
    app.progress_detail.configure(text="C:/Users/Bruno/Documents/.../gerencialismo")
    app._log("Etapa 3/3: salvando arquivos...", "info")
    app._log("JSON salvo: gerencialismo.json", "success")
    app._log("Excel salvo: gerencialismo.xlsx", "success")
    app._log("Concluido! 350 tese(s) salvas em 'gerencialismo'", "success")
    app._set_status("Concluido. Arquivos em: .../gerencialismo")
    _settle(app)

    img = _grab_window(app)

    # Caixa no painel de progresso
    prog_card = app.progress.master
    prog_bbox = widget_bbox(app, prog_card, expand=2)
    draw_box(img, prog_bbox, color=GREEN, width=4)
    draw_caption(img, (prog_bbox[0], prog_bbox[1] - 26),
                 "Coleta finalizada com sucesso",
                 color=GREEN, font_size=16)

    save(img, "05_concluido.png", crop="right")


# ============================================================
# MAIN
# ============================================================

def _settle(app):
    """Forca multiplas atualizacoes de layout + wraplength para garantir que esteja renderizado."""
    for _ in range(3):
        app.update_idletasks()
        app.update()
        _wait(app, 100)
        app._update_all_wraplengths()
    _wait(app, 200)


def main():
    print(f"Gerando screenshots em {OUT_DIR}/")
    app = gui_app.App()
    # App abre maximizado por padrao (state="zoomed" no __init__).
    # Em maximizado, a coluna esquerda tera overflow (scroll funciona).
    _settle(app)

    # Cena 1: tela limpa (sem termo preenchido)
    app.termo_var.set("")
    _settle(app)
    cena_01_tela_inicial(app)

    # Cena 2: termo + filtros configurados (parte de cima)
    app.termo_var.set("gerencialismo")
    _settle(app)
    cena_02_termo_filtros(app)

    # Cena 2b: scroll para baixo, botoes ANALISAR/EXECUTAR/PARAR
    cena_02b_botoes(app)

    # Cena 3: apos analise
    _scroll_left(app, 0.0)
    _settle(app)
    cena_03_analise(app)
    _settle(app)

    # Cena 4: durante execucao
    cena_04_execucao(app)
    _settle(app)

    # Cena 5: concluido
    cena_05_concluido(app)

    app.destroy()
    print("Concluido.")


if __name__ == "__main__":
    main()
