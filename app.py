"""ADO-3 — Física: Práticas Extensivas (opção B: colisão perfeitamente inelástica).

Execução:  python app.py
Bibliotecas: apenas matplotlib e numpy.
"""
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button

from fisica import momento_total, cinetica
from animacao import preparar_cenario, montar_cena, desenhar_barras, criar_animacao


def texto_painel(c):
    """Painel de resultados (R3)."""
    m1, m2, v1, v2 = c["m1"], c["m2"], c["v1"], c["v2"]
    if not c["colide"]:
        p = momento_total(m1, m2, v1, v2)
        k = cinetica(m1, m2, v1, v2)
        return ("SEM COLISÃO (v1 ≤ v2)\n\n"
                "Estado inicial:\n"
                f"  p = {p:+.3f} kg·m/s\n"
                f"  K = {k:.3f} J\n")
    r = c["res"]
    return (
        "VELOCIDADES (m/s)\n"
        f"  bloco 1: antes {v1:+7.3f} | depois {r['V']:+7.3f}\n"
        f"  bloco 2: antes {v2:+7.3f} | depois {r['V']:+7.3f}\n\n"
        "MOMENTO LINEAR (kg·m/s)\n"
        f"  p_antes  = {r['p_antes']:+9.3f}\n"
        f"  p_depois = {r['p_depois']:+9.3f}\n\n"
        "ENERGIA CINÉTICA (J)\n"
        f"  K_antes  = {r['k_antes']:9.3f}\n"
        f"  K_depois = {r['k_depois']:9.3f}\n"
        f"  ΔK       = {r['delta_k']:+9.3f}\n"
        f"  -½μ(v1-v2)² = {r['delta_k_formula']:+.3f}\n"
        f"  dissipada: {100 * r['fracao']:.1f} % de K_antes\n\n"
        "IMPULSO E FORÇA MÉDIA\n"
        f"  J1 = {r['j1']:+9.3f} N·s\n"
        f"  J2 = {r['j2']:+9.3f} N·s\n"
        f"  Δt = {c['dt_ms']:.0f} ms\n"
        f"  F_med = {r['f_med']:.3f} N\n\n"
        f"Instante do choque: tc = {c['tc']:.3f} s"
    )


def construir_interface():
    """Monta a figura, os controles (R2) e liga tudo à animação."""
    fig = plt.figure(figsize=(13, 8.6), facecolor="#f7f9fc")
    try:
        fig.canvas.manager.set_window_title("ADO-3 — Colisão perfeitamente inelástica")
    except Exception:
        pass

    ax_anim = fig.add_axes([0.05, 0.60, 0.60, 0.34])
    ax_p = fig.add_axes([0.07, 0.30, 0.25, 0.22])
    ax_k = fig.add_axes([0.40, 0.30, 0.25, 0.22])
    ax_txt = fig.add_axes([0.67, 0.28, 0.32, 0.66])

    def novo_slider(y, rotulo, vmin, vmax, ini, passo, fmt):
        ax = fig.add_axes([0.22, y, 0.40, 0.025])
        return Slider(ax, rotulo, vmin, vmax, valinit=ini, valstep=passo, valfmt=fmt)

    s_m1 = novo_slider(0.20, "Massa m1 (kg)", 0.5, 10.0, 2.0, 0.5, "%.1f")
    s_m2 = novo_slider(0.16, "Massa m2 (kg)", 0.5, 10.0, 3.0, 0.5, "%.1f")
    s_v1 = novo_slider(0.12, "Velocidade v1 (m/s)", -5.0, 15.0, 5.0, 0.5, "%.1f")
    s_v2 = novo_slider(0.08, "Velocidade v2 (m/s)", -5.0, 15.0, 0.0, 0.5, "%.1f")
    s_dt = novo_slider(0.04, "Duração Δt (ms)", 1, 500, 10, 1, "%d")
    b_pausa = Button(fig.add_axes([0.74, 0.14, 0.10, 0.06]), "Pausar")
    b_reinicia = Button(fig.add_axes([0.86, 0.14, 0.10, 0.06]), "Reiniciar")

    estado = {"cen": None, "art": None, "t": 0.0, "pausado": False}

    def reiniciar(_=None):
        """Recalcula tudo com os valores atuais dos controles e volta a t = 0."""
        estado["cen"] = preparar_cenario(s_m1.val, s_m2.val, s_v1.val, s_v2.val, s_dt.val)
        estado["t"] = 0.0
        estado["pausado"] = False
        b_pausa.label.set_text("Pausar")
        estado["art"] = montar_cena(ax_anim, estado["cen"])
        desenhar_barras(ax_p, ax_k, estado["cen"])
        ax_txt.clear()
        ax_txt.axis("off")
        ax_txt.text(0.5, 0.65, texto_painel(estado["cen"]), va="center", ha="center",
                    family="monospace", fontsize=9.5, transform=ax_txt.transAxes,
                    bbox=dict(fc="#f6f6f6", ec="#bbbbbb", boxstyle="round,pad=1"))
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