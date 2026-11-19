# ADO-3 — Colisão perfeitamente inelástica
 
Simulador interativo de uma colisão frontal (unidimensional) entre dois blocos
que ficam unidos após o choque. Projeto da disciplina **Física: Práticas
Extensivas** (opção B), feito apenas com **matplotlib** e **numpy**.
 
Usa somente fórmulas fechadas: não há integração numérica nem método iterativo.
 
## Como executar
 
```bash
# (opcional) criar e ativar um ambiente virtual
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
 
pip install -r requirements.txt
python app.py
```
 
## Controles
 
| Controle | Função |
|---|---|
| Massa m1, m2 (kg) | Massas dos blocos (0,5 a 10) |
| Velocidade v1, v2 (m/s) | Velocidades iniciais, positivas para a direita (−5 a 15) |
| Duração Δt (ms) | Duração do contato, usada no cálculo da força média |
| Pausar / Continuar | Congela e retoma a animação |
| Reiniciar | Volta ao instante inicial |
 
Ao mover qualquer slider, a simulação reinicia com os novos valores.
Valores iniciais: m1 = 2,0 kg, m2 = 3,0 kg, v1 = 5,0 m/s, v2 = 0 e Δt = 10 ms.
 
## O que o programa mostra
 
- **Animação** dos blocos em MRU antes e depois do choque, com a mudança de
  velocidade no instante `tc`. O tamanho de cada bloco depende da massa.
- **Painel de resultados:** velocidades antes e depois, momento linear
  (`p_antes` e `p_depois`), energia cinética (`K_antes`, `K_depois` e `ΔK`),
  conferência de `ΔK` com −½μ(v1−v2)², fração de energia dissipada, impulsos
  `J1` e `J2` e força média `F_med`.
- **Gráficos de barras** comparando, antes e depois, o momento total e a
  energia cinética total.
- **Caso sem colisão** (`v1 ≤ v2`): exibe uma mensagem na tela, sem erro.
## Fórmulas utilizadas
 
- Momento total: `p = m1·v1 + m2·v2`
- Energia cinética: `K = ½·m1·v1² + ½·m2·v2²`
- Velocidade final (blocos unidos): `V = (m1·v1 + m2·v2) / (m1 + m2)`
- Variação de energia: `ΔK = −½·μ·(v1 − v2)²`, com `μ = m1·m2 / (m1 + m2)`
- Impulsos: `J1 = m1·(V − v1)`, `J2 = m2·(V − v2)` e `J1 = −J2`
- Força média: `F_med = |J| / Δt`
- Instante do choque: `tc = folga / (v1 − v2)`, onde `folga` é a distância entre
  os centros menos a soma das meias-larguras (exige `v1 > v2`).
## Estrutura do projeto
 
```
ADO3/
├── app.py            # interface: sliders, botões e painel de resultados
├── animacao.py       # cena, FuncAnimation e gráficos de barras
├── fisica.py         # fórmulas físicas (sem matplotlib)
├── requirements.txt  # dependências
├── .gitignore
└── README.md
```
 
## Autores
 
- Laura Coelho
- Pedro Zeferino 
- Paulo Eduardo
 