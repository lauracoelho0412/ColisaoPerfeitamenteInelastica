"""Funções físicas para a colisão perfeitamente inelástica (opção B).

Todas as velocidades são algébricas: positivas para a direita.
Unidades: kg, m/s, s, N, J e kg·m/s.
"""


def momento_total(m1, m2, v1, v2):
    """Momento linear total p = m1 v1 + m2 v2."""
    return m1 * v1 + m2 * v2


def cinetica(m1, m2, v1, v2):
    """Energia cinética total K."""
    return 0.5 * m1 * v1**2 + 0.5 * m2 * v2**2


def colisao_perfeitamente_inelastica(m1, m2, v1, v2):
    """Velocidade comum V após os blocos ficarem unidos."""
    return (m1 * v1 + m2 * v2) / (m1 + m2)


def instante_contato(folga, v1, v2):
    """Instante tc do choque (fórmula fechada).

    folga = distância entre os centros menos a soma das meias-larguras.
    Exige v1 > v2.
    """
    return folga / (v1 - v2)


def calcular_resultados(m1, m2, v1, v2, delta_t_ms):
    """Velocidade final, p, K, ΔK, impulsos e força média."""
    V = colisao_perfeitamente_inelastica(m1, m2, v1, v2)
    p_antes = momento_total(m1, m2, v1, v2)
    p_depois = momento_total(m1, m2, V, V)
    k_antes = cinetica(m1, m2, v1, v2)
    k_depois = cinetica(m1, m2, V, V)
    delta_k = k_depois - k_antes

    mu = m1 * m2 / (m1 + m2)                    # massa reduzida
    delta_k_formula = -0.5 * mu * (v1 - v2) ** 2

    j1 = m1 * (V - v1)                          # J1 = Δp1
    j2 = m2 * (V - v2)                          # J2 = Δp2 = -J1
    delta_t = delta_t_ms / 1000.0
    f_med = abs(j1) / delta_t
    fracao = abs(delta_k) / k_antes if k_antes > 0 else 0.0

    return dict(V=V, p_antes=p_antes, p_depois=p_depois,
                k_antes=k_antes, k_depois=k_depois, delta_k=delta_k,
                delta_k_formula=delta_k_formula, fracao=fracao,
                j1=j1, j2=j2, f_med=f_med)