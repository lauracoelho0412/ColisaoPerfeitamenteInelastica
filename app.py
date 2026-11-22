"""ADO-3 — Colisão perfeitamente inelástica (versão Streamlit).

Execução local:   streamlit run app.py
"""
import threading
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import streamlit as st
from matplotlib.figure import Figure

from fisica import momento_total, cinetica
from animacao import (preparar_cenario, desenhar_cena, desenhar_barras,
                      BG, CARD, BORDA, TXT, MUTED, COR1, COR2, ACENTO)

VERDE = "#27AE60"

st.set_page_config(page_title="ADO-3 — Colisão inelástica",
                   page_icon="💥", layout="wide")

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "text.color": TXT,
    "axes.labelcolor": MUTED,
})


# ---------------------------------------------------------------- sidebar
def sidebar_controles():
    st.sidebar.header("Controles")
    m1 = st.sidebar.slider("Massa m1 (kg)", 0.5, 10.0, 2.0, 0.5)
    m2 = st.sidebar.slider("Massa m2 (kg)", 0.5, 10.0, 3.0, 0.5)
    v1 = st.sidebar.slider("Velocidade v1 (m/s)", -5.0, 15.0, 5.0, 0.5)
    v2 = st.sidebar.slider("Velocidade v2 (m/s)", -5.0, 15.0, 0.0, 0.5)
    dt = st.sidebar.slider("Duração Δt (ms)", 1, 500, 10, 1)

    st.sidebar.divider()

    if "pausado" not in st.session_state:
        st.session_state.pausado = False

    rotulo = "▶ Continuar" if st.session_state.pausado else "⏸ Pausar"
    if st.sidebar.button(rotulo, use_container_width=True):
        st.session_state.pausado = not st.session_state.pausado
        st.rerun()

    reiniciar = st.sidebar.button("↺ Reiniciar", use_container_width=True)
    return m1, m2, v1, v2, dt, st.session_state.pausado, reiniciar


# --------------------------------------------------------------- painel
def painel_resultados(c):
    m1, m2, v1, v2 = c["m1"], c["m2"], c["v1"], c["v2"]
    if not c["colide"]:
        p = momento_total(m1, m2, v1, v2)
        k = cinetica(m1, m2, v1, v2)
        st.error("**SEM COLISÃO (v1 ≤ v2)** — ajuste as velocidades.")
        st.markdown("**Estado inicial:**")
        st.code(f"p = {p:+.3f} kg·m/s\nK = {k:.3f} J", language="text")
        return

    r = c["res"]
    st.markdown("#### 🟦 Velocidades (m/s)")
    st.code(f"bloco 1: antes {v1:+7.3f} | depois {r['V']:+7.3f}\n"
            f"bloco 2: antes {v2:+7.3f} | depois {r['V']:+7.3f}", language="text")

    st.markdown("#### 🟧 Momento linear (kg·m/s)")
    st.code(f"p_antes  = {r['p_antes']:+9.3f}\n"
            f"p_depois = {r['p_depois']:+9.3f}", language="text")

    st.markdown("#### 🟩 Energia cinética (J)")
    st.code(f"K_antes  = {r['k_antes']:9.3f}\n"
            f"K_depois = {r['k_depois']:9.3f}\n"
            f"ΔK       = {r['delta_k']:+9.3f}\n"
            f"-½μ(v1-v2)² = {r['delta_k_formula']:+.3f}\n"
            f"dissipada: {100 * r['fracao']:.1f} % de K_antes", language="text")

    st.markdown("#### 🟥 Impulso e força média")
    st.code(f"J1 = {r['j1']:+9.3f} N·s\n"
            f"J2 = {r['j2']:+9.3f} N·s\n"
            f"Δt = {c['dt_ms']:.0f} ms\n"
            f"F_med = {r['f_med']:.3f} N", language="text")

    st.caption(f"Instante do choque: tc = {c['tc']:.3f} s")


# --------------------------------------------------------------- animação
def _desenhar_painel_r4(c):
    """Figura de barras (R4) reutilizável."""
    fig = Figure(figsize=(8.5, 3.4), facecolor=BG)
    desenhar_barras(fig, c)
    return fig


# ------------------------------------------------------------------ main
def main():
    st.title("💥 Colisão Frontal Perfeitamente Inelástica")
    st.caption("ADO-3 — Física: Práticas Extensivas (opção B)")

    m1, m2, v1, v2, dt, pausado, reiniciar = sidebar_controles()

    if "t" not in st.session_state or reiniciar:
        st.session_state.t = 0.0
        st.session_state.pausado = False

    c = preparar_cenario(m1, m2, v1, v2, dt)

    # duas colunas: esquerda (animação + barras) | direita (resultados)
    col_esq, col_dir = st.columns([2.2, 1])

    with col_esq:
        st.subheader("Cena da animação")
        quadro = st.empty()

        # botões próximos da animação
        col_a, col_b = st.columns(2)
        with col_a:
            rotulo = "▶ Continuar" if pausado else "⏸ Pausar"
            if st.button(rotulo, use_container_width=True):
                st.session_state.pausado = not st.session_state.pausado
                st.rerun()
        with col_b:
            if st.button("↺ Reiniciar", use_container_width=True):
                st.session_state.t = 0.0
                st.session_state.pausado = False
                st.rerun()

        # ---- Momento e energia (R4) logo abaixo, mesma largura ----
        st.subheader("Momento e energia: antes × depois")
        barras_ph = st.empty()

    with col_dir:
        st.subheader("Resultados")
        painel_ph = st.empty()

    # ---- renderização inicial ----
    fig_anim = Figure(figsize=(8.5, 3.4), facecolor=BG)
    ax_anim = fig_anim.add_subplot(111)

    def renderizar(t):
        desenhar_cena(ax_anim, c, t)
        quadro.pyplot(fig_anim, clear_figure=False)
        with barras_ph.container():
            st.pyplot(_desenhar_painel_r4(c), clear_figure=False)
        with painel_ph.container():
            painel_resultados(c)

    renderizar(st.session_state.t)

    # ---- loop de animação na thread principal ----
    if not pausado and c["colide"]:
        DURACAO_CICLO = 7.0
        ESCALA = c["t_final"] / DURACAO_CICLO
        INTERVALO = 0.06
        t = st.session_state.t
        while not st.session_state.pausado:
            t += ESCALA * INTERVALO
            if t > c["t_final"]:
                t = 0.0
            st.session_state.t = t
            renderizar(t)
            time.sleep(INTERVALO)


main()