"""Cena, animação (FuncAnimation) e gráficos de barras da colisão."""
import itertools

import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle

from fisica import calcular_resultados, instante_contato, momento_total, cinetica

X1_0, X2_0 = 1.0, 8.0          # posições iniciais dos centros (m)
INTERVALO_MS = 30              # intervalo entre quadros (ms)
DURACAO_REPRODUCAO = 7.0       # duração de um ciclo na tela (s reais)
COR1, COR2 = "#2878B5", "#E58A28"


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
    xmin, xmax = min(esq) - 1.0, max(dire) + 1.0
    if xmax - xmin < 12:
        meio = (xmin + xmax) / 2
        xmin, xmax = meio - 6, meio + 6
    return xmin, xmax


# -------------------------------- desenho ---------------------------------
def montar_cena(ax, c):
    """Limpa o eixo, cria os blocos e devolve os artistas atualizáveis."""
    ax.clear()
    ax.set_xlim(*limites_x(c))
    ax.set_ylim(-0.4, 3.1)
    ax.set_yticks([])
    ax.set_xlabel("Posição (m) — escala visual ilustrativa")
    ax.set_title("Colisão Frontal Perfeitamente Inelástica", loc="center", x=0.75, fontsize=24)
    ax.axhline(0, color="gray", lw=1.5)


    r1 = Rectangle((0, 0), c["w1"], c["h1"], fc=COR1, ec="black", lw=1.2)
    r2 = Rectangle((0, 0), c["w2"], c["h2"], fc=COR2, ec="black", lw=1.2)
    ax.add_patch(r1)
    ax.add_patch(r2)
    t1 = ax.text(0, 0, "", ha="center", va="bottom", fontsize=9)
    t2 = ax.text(0, 0, "", ha="center", va="bottom", fontsize=9)
    status = ax.text(0.01, 0.93, "", transform=ax.transAxes, fontsize=10,
                     va="top", family="monospace")
    art = dict(r1=r1, r2=r2, t1=t1, t2=t2, status=status)

    if not c["colide"]:   # R5: caso sem colisão
        ax.text(0.5, 0.62, "Sem colisão: é necessário v1 > v2.\n"
                "Ajuste as velocidades para que o bloco 1 alcance o bloco 2.",
                transform=ax.transAxes, ha="center", va="center",
                color="firebrick", fontsize=12,
                bbox=dict(fc="white", ec="firebrick", boxstyle="round"))
    desenhar_quadro(c, art, 0.0)
    return art


def desenhar_quadro(c, art, t):
    """Atualiza blocos, rótulos e status para o instante t."""
    x1, x2 = posicoes(c, t)
    art["r1"].set_xy((x1 - c["w1"] / 2, 0))
    art["r2"].set_xy((x2 - c["w2"] / 2, 0))

    if c["colide"]:
        tc, V = c["tc"], c["res"]["V"]
        em_contato = tc <= t < tc + c["dt_ms"] / 1000.0
        if t < tc:
            fase, va, vb = "Antes do choque", c["v1"], c["v2"]
        else:
            fase = "CONTATO" if em_contato else "Depois do choque (unidos)"
            va = vb = V
        for r in (art["r1"], art["r2"]):
            r.set_edgecolor("red" if em_contato else "black")
            r.set_linewidth(3 if em_contato else 1.2)
        art["status"].set_text(f"t = {t:5.2f} s  |  {fase}\n"
                               f"reprodução ×{c['escala']:.2f} do tempo real")
        art["status"].set_color("red" if em_contato else "black")
    else:
        va, vb = c["v1"], c["v2"]

    if c["colide"] and t >= c["tc"]:
        art["t1"].set_position(((x1 + x2) / 2, max(c["h1"], c["h2"]) + 0.08))
        art["t1"].set_text(f"m1 + m2 = {c['m1'] + c['m2']:.1f} kg\nV = {va:+.2f} m/s")
        art["t2"].set_text("")
    else:
        art["t1"].set_position((x1, c["h1"] + 0.08))
        art["t2"].set_position((x2, c["h2"] + 0.08))
        art["t1"].set_text(f"m1 = {c['m1']:.1f} kg\nv = {va:+.2f} m/s")
        art["t2"].set_text(f"m2 = {c['m2']:.1f} kg\nv = {vb:+.2f} m/s")


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
        nomes = ["Antes"] if depois is None else ["Antes", "Depois"]
        vals = [antes] if depois is None else [antes, depois]
        barras = ax.bar(nomes, vals, color=[COR1, COR2][:len(vals)])
        ax.bar_label(barras, fmt="%.2f", padding=2)
        ax.axhline(0, color="black", lw=0.7)
        ax.set_title(titulo, fontsize=10)
        ax.set_ylabel(ylabel)
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