"""Cena, animação (FuncAnimation) e gráficos de barras da colisão."""
import itertools

import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.patches import FancyBboxPatch

from fisica import calcular_resultados, instante_contato, momento_total, cinetica

X1_0, X2_0 = 1.0, 8.0          # posições iniciais dos centros (m)
INTERVALO_MS = 30              # intervalo entre quadros (ms)
DURACAO_REPRODUCAO = 7.0       # duração de um ciclo na tela (s reais)
FLASH_S = 0.30                 # duração (tempo simulado) da faísca do choque

# ------------------------------- paleta ------------------------------------
BG = "#f4f6fb"        # fundo da figura
CARD = "#ffffff"      # fundo dos "cartões"
BORDA = "#d9dfeb"
TXT = "#1f2a44"
MUTED = "#6b7690"
CHAO = "#e3e8f0"
COR1, COR2 = "#2F80ED", "#F2994A"
ACENTO = "#E5484D"


def estilizar_eixo(ax, grade_y=False):
    """Visual limpo: sem bordas superior/direita, cores suaves."""
    ax.set_facecolor(CARD)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color(BORDA)
    ax.tick_params(colors=MUTED, labelsize=9)
    if grade_y:
        ax.grid(axis="y", color="#eef1f6", lw=1)
        ax.set_axisbelow(True)


# ------------------------------ geometria ---------------------------------
def largura_bloco(m):
    return 0.6 + 0.30 * np.sqrt(m)


def altura_bloco(m):
    return 0.5 + 0.25 * np.sqrt(m)


def preparar_cenario(m1, m2, v1, v2, dt_ms):
    """Reúne tudo o que a animação e o painel precisam."""
    c = dict(m1=m1, m2=m2, v1=v1, v2=v2, dt_ms=dt_ms,
             w1=largura_bloco(m1), w2=largura_bloco(m2),
             h1=altura_bloco(m1), h2=altura_bloco(m2),
             colide=v1 > v2)
    if c["colide"]:
        folga = X2_0 - X1_0 - (c["w1"] + c["w2"]) / 2
        c["tc"] = instante_contato(folga, v1, v2)
        c["res"] = calcular_resultados(m1, m2, v1, v2, dt_ms)
        c["t_final"] = c["tc"] + max(1.0, 0.5 * c["tc"])
        c["escala"] = c["t_final"] / DURACAO_REPRODUCAO   # s simulados por s real
    return c


def posicoes(c, t):
    """Centros dos blocos em t: MRU antes de tc; velocidade V (unidos) depois."""
    if not c["colide"]:
        return X1_0, X2_0
    tc, V = c["tc"], c["res"]["V"]
    if t <= tc:
        return X1_0 + c["v1"] * t, X2_0 + c["v2"] * t
    return (X1_0 + c["v1"] * tc + V * (t - tc),
            X2_0 + c["v2"] * tc + V * (t - tc))


def limites_x(c):
    """Janela fixa que contém toda a trajetória."""
    esq, dire = [], []
    tempos = [0.0, c["tc"], c["t_final"]] if c["colide"] else [0.0]
    for t in tempos:
        x1, x2 = posicoes(c, t)
        esq += [x1 - c["w1"] / 2, x2 - c["w2"] / 2]
        dire += [x1 + c["w1"] / 2, x2 + c["w2"] / 2]
    xmin, xmax = min(esq) - 1.5, max(dire) + 1.5
    if xmax - xmin < 12:
        meio = (xmin + xmax) / 2
        xmin, xmax = meio - 6, meio + 6
    return xmin, xmax


# -------------------------------- desenho ---------------------------------
def _bloco(cor):
    return FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0,rounding_size=0.08",
                          fc=cor, ec="#1f2a44", lw=1.4, zorder=3)


def _rotulo(ax, cor):
    return ax.text(0, 0, "", ha="center", va="bottom", fontsize=9, color=TXT,
                   zorder=5,
                   bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=cor, lw=1.2,
                             alpha=0.95))


def _seta(ax, cor):
    return ax.annotate("", xy=(0, 0), xytext=(0, 0), annotation_clip=False, zorder=4,
                       arrowprops=dict(arrowstyle="-|>", color=cor, lw=2.6,
                                       shrinkA=0, shrinkB=0, mutation_scale=16))


def montar_cena(ax, c):
    """Limpa o eixo, cria os blocos e devolve os artistas atualizáveis."""
    ax.clear()
    estilizar_eixo(ax)
    ax.spines["left"].set_visible(False)
    ax.set_xlim(*limites_x(c))
    ax.set_ylim(-0.4, 3.2)
    ax.set_yticks([])
    ax.set_xlabel("Posição (m) — escala visual ilustrativa", color=MUTED, fontsize=9, x = 0.16)
    ax.set_title("Colisão Frontal Perfeitamente Inelástica",
                 fontsize=17, fontweight="bold", color=TXT, pad=12, x = 0.75)

    # chão
    ax.axhspan(-0.4, 0, color=CHAO, zorder=0)
    ax.axhline(0, color="#8a94a6", lw=2, zorder=1)

    r1, r2 = _bloco(COR1), _bloco(COR2)
    ax.add_patch(r1)
    ax.add_patch(r2)

    t1, t2 = _rotulo(ax, COR1), _rotulo(ax, COR2)
    a1, a2 = _seta(ax, COR1), _seta(ax, COR2)
    flash, = ax.plot([], [], marker="*", ms=30, color="#FFD43B", mec=ACENTO,
                     mew=1.5, ls="none", zorder=6, visible=False)
    status = ax.text(0.015, 0.95, "", transform=ax.transAxes, fontsize=9.5,
                     va="top", family="monospace", color=TXT, zorder=7,
                     bbox=dict(boxstyle="round,pad=0.5", fc="white", ec=BORDA))
    art = dict(r1=r1, r2=r2, t1=t1, t2=t2, a1=a1, a2=a2,
               flash=flash, status=status)

    if not c["colide"]:   # R5: caso sem colisão
        ax.text(0.5, 0.60, "Sem colisão: é necessário v1 > v2.\n"
                "Ajuste as velocidades para que o bloco 1 alcance o bloco 2.",
                transform=ax.transAxes, ha="center", va="center",
                color=ACENTO, fontsize=12, zorder=8,
                bbox=dict(fc="#fff5f5", ec=ACENTO, boxstyle="round,pad=0.6"))
    desenhar_quadro(c, art, 0.0)
    return art


def _posicionar_seta(a, x, y, v):
    """Seta horizontal proporcional à velocidade (escondida se v ≈ 0)."""
    if abs(v) < 0.05:
        a.set_visible(False)
        return
    a.set_visible(True)
    a.set_position((x, y))
    a.xy = (x + float(np.clip(0.22 * v, -2.2, 2.2)), y)


def desenhar_quadro(c, art, t):
    """Atualiza blocos, rótulos e status para o instante t."""
    x1, x2 = posicoes(c, t)
    art["r1"].set_bounds(x1 - c["w1"] / 2, 0, c["w1"], c["h1"])
    art["r2"].set_bounds(x2 - c["w2"] / 2, 0, c["w2"], c["h2"])

    flash_on = False
    if c["colide"]:
        tc, V = c["tc"], c["res"]["V"]
        em_contato = tc <= t < tc + c["dt_ms"] / 1000.0
        if t < tc:
            fase, va, vb = "Antes do choque", c["v1"], c["v2"]
        else:
            fase = "CONTATO" if em_contato else "Depois do choque (unidos)"
            va = vb = V
        for r in (art["r1"], art["r2"]):
            r.set_edgecolor(ACENTO if em_contato else TXT)
            r.set_linewidth(3.2 if em_contato else 1.4)
        art["status"].set_text(f"t = {t:5.2f} s  |  {fase}\n"
                               f"reprodução ×{c['escala']:.2f} do tempo real")
        art["status"].set_color(ACENTO if em_contato else TXT)

        if tc <= t < tc + FLASH_S:       # faísca visual do choque
            f = (t - tc) / FLASH_S
            art["flash"].set_data([x1 + c["w1"] / 2], [min(c["h1"], c["h2"]) / 2])
            art["flash"].set_markersize(18 + 34 * f)
            art["flash"].set_alpha(1 - f)
            flash_on = True
    else:
        va, vb = c["v1"], c["v2"]
    art["flash"].set_visible(flash_on)

    if c["colide"] and t >= c["tc"]:      # blocos unidos
        h = max(c["h1"], c["h2"])
        xm = (x1 + x2) / 2
        art["t1"].set_position((xm, h + 0.5))
        art["t1"].set_text(f"m1 + m2 = {c['m1'] + c['m2']:.1f} kg\nV = {va:+.2f} m/s")
        art["t1"].get_bbox_patch().set_edgecolor("#555555")
        art["t2"].set_text("")
        _posicionar_seta(art["a1"], xm, h + 0.28, va)
        art["a1"].arrow_patch.set_color("#555555")
        art["a2"].set_visible(False)
    else:
        art["t1"].set_position((x1, c["h1"] + 0.5))
        art["t2"].set_position((x2, c["h2"] + 0.5))
        art["t1"].set_text(f"m1 = {c['m1']:.1f} kg\nv = {va:+.2f} m/s")
        art["t2"].set_text(f"m2 = {c['m2']:.1f} kg\nv = {vb:+.2f} m/s")
        art["t1"].get_bbox_patch().set_edgecolor(COR1)
        art["a1"].arrow_patch.set_color(COR1)
        _posicionar_seta(art["a1"], x1, c["h1"] + 0.28, va)
        _posicionar_seta(art["a2"], x2, c["h2"] + 0.28, vb)


def desenhar_barras(ax_p, ax_k, c):
    """R4: barras de momento e energia, antes e depois."""
    if c["colide"]:
        r = c["res"]
        dados = [(ax_p, "Momento linear total", "p (kg·m/s)", r["p_antes"], r["p_depois"]),
                 (ax_k, "Energia cinética total", "K (J)", r["k_antes"], r["k_depois"])]
    else:
        dados = [(ax_p, "Momento linear total", "p (kg·m/s)",
                  momento_total(c["m1"], c["m2"], c["v1"], c["v2"]), None),
                 (ax_k, "Energia cinética total", "K (J)",
                  cinetica(c["m1"], c["m2"], c["v1"], c["v2"]), None)]
    for ax, titulo, ylabel, antes, depois in dados:
        ax.clear()
        estilizar_eixo(ax, grade_y=True)
        nomes = ["Antes"] if depois is None else ["Antes", "Depois"]
        vals = [antes] if depois is None else [antes, depois]
        barras = ax.bar(nomes, vals, color=[COR1, COR2][:len(vals)], width=0.55,
                        zorder=3)
        ax.bar_label(barras, fmt="%.2f", padding=3, fontsize=9, color=TXT,
                     fontweight="bold")
        ax.axhline(0, color=MUTED, lw=0.8, zorder=4)
        ax.set_title(titulo, fontsize=11, fontweight="bold", color=TXT, pad=8)
        ax.set_ylabel(ylabel, color=MUTED, fontsize=9)
        lo, hi = min(0, *vals), max(0, *vals)
        pad = 0.25 * ((hi - lo) or 1.0)
        ax.set_ylim(lo - (pad if lo < 0 else 0), hi + pad)


# ------------------------------- animação ---------------------------------
def criar_animacao(fig, estado):
    """FuncAnimation que avança o tempo simulado em `estado` (R1).

    estado: dict com as chaves 'cen', 'art', 't' e 'pausado'.
    Devolve (anim, atualizar).
    """
    def atualizar(_quadro):
        c = estado["cen"]
        if not c["colide"]:
            return
        if not estado["pausado"]:
            estado["t"] += c["escala"] * INTERVALO_MS / 1000.0
            if estado["t"] > c["t_final"]:
                estado["t"] = 0.0          # recomeça o ciclo
        desenhar_quadro(c, estado["art"], estado["t"])

    anim = FuncAnimation(fig, atualizar, frames=itertools.count(),
                         interval=INTERVALO_MS, blit=False, cache_frame_data=False)
    return anim, atualizar