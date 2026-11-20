"""ADO-3 — Física: Práticas Extensivas (opção B: colisão perfeitamente inelástica).

Execução:  python app.py
Bibliotecas: apenas matplotlib e numpy.
"""
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
from matplotlib.patches import FancyBboxPatch
from matplotlib.widgets import Slider, Button

from fisica import momento_total, cinetica
from animacao import (preparar_cenario, montar_cena, desenhar_barras, criar_animacao,
                      BG, CARD, BORDA, TXT, MUTED, COR1, COR2, ACENTO)

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "text.color": TXT,
    "axes.labelcolor": MUTED,
})

VERDE = "#27AE60"


def texto_painel(c):
    """Painel de resultados (R3), em seções: (título, cor, [linhas])."""
    m1, m2, v1, v2 = c["m1"], c["m2"], c["v1"], c["v2"]
    if not c["colide"]:
        p = momento_total(m1, m2, v1, v2)
        k = cinetica(m1, m2, v1, v2)
        return [("SEM COLISÃO (v1 ≤ v2)", ACENTO, []),
                ("Estado inicial:", COR1, [f"p = {p:+.3f} kg·m/s",
                                          f"K = {k:.3f} J"])]
    r = c["res"]
    return [
        ("VELOCIDADES (m/s)", COR1, [
            f"bloco 1: antes {v1:+7.3f} | depois {r['V']:+7.3f}",
            f"bloco 2: antes {v2:+7.3f} | depois {r['V']:+7.3f}"]),
        ("MOMENTO LINEAR (kg·m/s)", COR2, [
            f"p_antes  = {r['p_antes']:+9.3f}",
            f"p_depois = {r['p_depois']:+9.3f}"]),
        ("ENERGIA CINÉTICA (J)", VERDE, [
            f"K_antes  = {r['k_antes']:9.3f}",
            f"K_depois = {r['k_depois']:9.3f}",
            f"ΔK       = {r['delta_k']:+9.3f}",
            f"-½μ(v1-v2)² = {r['delta_k_formula']:+.3f}",
            f"dissipada: {100 * r['fracao']:.1f} % de K_antes"]),
        ("IMPULSO E FORÇA MÉDIA", ACENTO, [
            f"J1 = {r['j1']:+9.3f} N·s",
            f"J2 = {r['j2']:+9.3f} N·s",
            f"Δt = {c['dt_ms']:.0f} ms",
            f"F_med = {r['f_med']:.3f} N"]),
        (f"Instante do choque: tc = {c['tc']:.3f} s", MUTED, []),
    ]


def desenhar_painel(ax, c):
    """Desenha o painel como um cartão com seções coloridas."""
    ax.clear()
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.add_patch(FancyBboxPatch((0.0, 0.0), 1, 1,
                                boxstyle="round,pad=0,rounding_size=0.02",
                                fc=CARD, ec=BORDA, lw=1.2, transform=ax.transAxes))
    y = 0.95
    for titulo, cor, linhas in texto_painel(c):
        ax.text(0.06, y, titulo, color=cor, fontsize=10, fontweight="bold", va="top")
        y -= 0.046
        for linha in linhas:
            ax.text(0.08, y, linha, family="monospace", fontsize=9, va="top", color=TXT)
            y -= 0.042
        y -= 0.026


def construir_interface():
    """Monta a figura, os controles (R2) e liga tudo à animação."""
    fig = plt.figure(figsize=(13, 8.6), facecolor=BG)
    try:
        fig.canvas.manager.set_window_title("ADO-3 — Colisão perfeitamente inelástica")
    except Exception:
        pass

    ax_anim = fig.add_axes([0.05, 0.60, 0.60, 0.33])
    ax_p = fig.add_axes([0.09, 0.31, 0.24, 0.17])
    ax_k = fig.add_axes([0.41, 0.31, 0.24, 0.17])
    ax_txt = fig.add_axes([0.68, 0.29, 0.27, 0.64])

    # cartão de fundo dos controles
    ax_card = fig.add_axes([0.05, 0.02, 0.60, 0.22])
    ax_card.axis("off")
    ax_card.add_patch(FancyBboxPatch((0, 0), 1, 1,
                                     boxstyle="round,pad=0,rounding_size=0.03",
                                     fc=CARD, ec=BORDA, lw=1.2,
                                     transform=ax_card.transAxes))

    def slider(y, rotulo, vmin, vmax, ini, passo, fmt, cor):
        ax = fig.add_axes([0.24, y, 0.34, 0.022], facecolor="#e6ebf2")
        s = Slider(ax, rotulo, vmin, vmax, valinit=ini, valstep=passo, valfmt=fmt,
                   color=cor)
        s.label.set_color(TXT)
        s.label.set_fontsize(10)
        s.valtext.set_color(TXT)
        s.valtext.set_fontweight("bold")
        return s

    s_m1 = slider(0.20, "Massa m1 (kg)", 0.5, 10.0, 2.0, 0.5, "%.1f", COR1)
    s_m2 = slider(0.16, "Massa m2 (kg)", 0.5, 10.0, 3.0, 0.5, "%.1f", COR2)
    s_v1 = slider(0.12, "Velocidade v1 (m/s)", -5.0, 15.0, 5.0, 0.5, "%.1f", COR1)
    s_v2 = slider(0.08, "Velocidade v2 (m/s)", -5.0, 15.0, 0.0, 0.5, "%.1f", COR2)
    s_dt = slider(0.04, "Duração Δt (ms)", 1, 500, 10, 1, "%d", VERDE)

    def botao(rect, texto, cor, hover):
        """Botão com cantos arredondados (forma desenhada dentro do eixo)."""
        ax_b = fig.add_axes(rect)
        b = Button(ax_b, texto, color=cor, hovercolor=hover)
        ax_b.axis("off")                    # remove o retângulo padrão do botão
        prop = (rect[2] * 13) / (rect[3] * 8.6)     # proporção largura/altura
        m = 0.04
        ax_b.set_xlim(-m, prop + m)
        ax_b.set_ylim(-m, 1 + m)
        forma = FancyBboxPatch((0, 0), prop, 1,
                               boxstyle="round,pad=0,rounding_size=0.35",
                               fc=cor, ec=TXT, lw=1.8, zorder=0, clip_on=False)
        ax_b.add_patch(forma)

        def passar_mouse(ev):
            nova = hover if ev.inaxes is ax_b else cor
            if forma.get_facecolor() != to_rgba(nova):
                forma.set_facecolor(nova)
                fig.canvas.draw_idle()
        fig.canvas.mpl_connect("motion_notify_event", passar_mouse)

        b.label.set_color("white")
        b.label.set_fontweight("bold")
        b.label.set_fontsize(10)
        return b

    b_pausa = botao([0.685, 0.100, 0.12, 0.06], "Pausar", COR1, "#1c64c4")
    b_reinicia = botao([0.825, 0.100, 0.12, 0.06], "Reiniciar", COR2, "#d17c35")

    estado = {"cen": None, "art": None, "t": 0.0, "pausado": False}

    def reiniciar(_=None):
        """Recalcula tudo com os valores atuais dos controles e volta a t = 0."""
        estado["cen"] = preparar_cenario(s_m1.val, s_m2.val, s_v1.val, s_v2.val, s_dt.val)
        estado["t"] = 0.0
        estado["pausado"] = False
        b_pausa.label.set_text("Pausar")
        estado["art"] = montar_cena(ax_anim, estado["cen"])
        desenhar_barras(ax_p, ax_k, estado["cen"])
        desenhar_painel(ax_txt, estado["cen"])
        fig.canvas.draw_idle()

    def alternar_pausa(_=None):
        estado["pausado"] = not estado["pausado"]
        b_pausa.label.set_text("Continuar" if estado["pausado"] else "Pausar")
        fig.canvas.draw_idle()

    for s in (s_m1, s_m2, s_v1, s_v2, s_dt):
        s.on_changed(reiniciar)
    b_reinicia.on_clicked(reiniciar)
    b_pausa.on_clicked(alternar_pausa)

    reiniciar()
    anim, atualizar = criar_animacao(fig, estado)
    # devolve tudo para manter as referências vivas
    return fig, anim, dict(sliders=(s_m1, s_m2, s_v1, s_v2, s_dt),
                           botoes=(b_pausa, b_reinicia), estado=estado,
                           atualizar=atualizar)


def main():
    fig, anim, refs = construir_interface()
    plt.show()


if __name__ == "__main__":
    main()