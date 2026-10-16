import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Calculadora de Impedância de Linhas Aéreas",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("⚡ Calculadora de Impedância de Linhas Aéreas")

st.caption(
    "Cálculo das matrizes de indutância, reatância, resistência "
    "e impedância série da linha."
)

st.markdown("---")

# ============================================================
# CONSTANTES
# ============================================================

mu0 = 4 * np.pi * 1e-7
K = mu0 / (2 * np.pi)

# ============================================================
# DADOS DOS CABOS
# ============================================================

cabos_fase = {
    "Linnet (336,4 MCM)": {
        "GMR": 0.00742,
        "diam": 0.01831,
        "R": 0.203
    },
    "Grosbeak (636 MCM)": {
        "GMR": 0.01021,
        "diam": 0.02515,
        "R": 0.108
    },
    "Raven (1/0 AWG)": {
        "GMR": 0.00388,
        "diam": 0.01011,
        "R": 0.709
    },
    "Penguin (4/0 AWG)": {
        "GMR": 0.00550,
        "diam": 0.01431,
        "R": 0.380
    },
    "Cairo (465,4 MCM)": {
        "GMR": 0.00753,
        "diam": 0.01990,
        "R": 0.170
    },
    "Flint (740,8 MCM)": {
        "GMR": 0.00966,
        "diam": 0.02513,
        "R": 0.108
    }
}

cabos_pr = {
    '5/16"': {
        "GMR": 0.0025,
        "diam": 0.00794,
        "R": 4.76 * (1 + 0.004 * (75 - 20))
    },
    '3/8"': {
        "GMR": 0.0030,
        "diam": 0.00952,
        "R": 3.44 * (1 + 0.004 * (75 - 20))
    }
}

# ============================================================
# FUNÇÕES
# ============================================================

def altura_equivalente(y, flecha, delta_h):
    return y - (2 / 3) * flecha + delta_h


def distancia(p1, p2):
    return np.sqrt(
        (p1[0] - p2[0]) ** 2 +
        (p1[1] - p2[1]) ** 2
    )


def distancia_imagem(p1, p2):
    return np.sqrt(
        (p1[0] - p2[0]) ** 2 +
        (p1[1] + p2[1]) ** 2
    )


def dataframe_complexo(matriz, nomes):
    dados = []

    for linha in matriz:
        dados.append([
            f"{valor.real:.6f} {valor.imag:+.6f}j"
            for valor in linha
        ])

    return pd.DataFrame(
        dados,
        index=nomes,
        columns=nomes
    )


def dataframe_real(matriz, nomes):
    return pd.DataFrame(
        matriz,
        index=nomes,
        columns=nomes
    )


def plotar_geometria(coords):
    fig, ax = plt.subplots(figsize=(8, 5))

    cores = {
        "A": "red",
        "B": "blue",
        "C": "green",
        "P": "gray"
    }

    for nome, ponto in coords.items():
        x = ponto[0]
        y = ponto[1]

        ax.scatter(
            x,
            y,
            s=120,
            color=cores[nome],
            zorder=3
        )

        ax.annotate(
            nome,
            (x, y),
            xytext=(7, 7),
            textcoords="offset points",
            fontweight="bold"
        )

    ax.axhline(
        y=0,
        color="saddlebrown",
        linewidth=2,
        label="Solo"
    )

    ax.set_xlabel("Coordenada horizontal X (m)")
    ax.set_ylabel("Altura equivalente Y (m)")
    ax.set_title("Geometria equivalente dos condutores")
    ax.grid(True, alpha=0.25)
    ax.legend()

    fig.tight_layout()

    return fig


# ============================================================
# INTERFACE EM DUAS COLUNAS
# ============================================================

col1, col2 = st.columns(
    [1, 1],
    gap="large"
)

# ============================================================
# COLUNA 1
# ============================================================

with col1:

    st.subheader("⚙️ 1. CONFIGURAÇÕES GERAIS")

    frequencia = st.number_input(
        "Frequência (Hz)",
        min_value=1.0,
        value=60.0,
        step=1.0
    )

    delta_altura = st.slider(
        "Ajuste de altura ΔH (m)",
        min_value=-20.0,
        max_value=20.0,
        value=0.0,
        step=0.5
    )

    st.markdown("---")

    st.subheader("🔌 2. CABO DAS FASES")

    cabo_fase_nome = st.selectbox(
        "Cabo fase",
        list(cabos_fase.keys())
    )

    n_sub = st.selectbox(
        "Subcondutores por fase",
        [1, 2],
        format_func=lambda valor:
            "1 condutor"
            if valor == 1
            else "2 subcondutores"
    )

    dist_sub = st.number_input(
        "Espaçamento do feixe (m)",
        min_value=0.001,
        value=0.305,
        step=0.005,
        disabled=(n_sub == 1)
    )

    flecha_fase = st.number_input(
        "Flecha das fases (m)",
        min_value=0.0,
        value=0.0,
        step=0.1
    )

    # Dados equivalentes apresentados antes do cálculo

    cf_interface = cabos_fase[cabo_fase_nome]

    resistencia_fase_interface = (
        cf_interface["R"] / n_sub
    )

    if n_sub == 1:
        gmr_fase_interface = cf_interface["GMR"]
    else:
        gmr_fase_interface = np.sqrt(
            cf_interface["GMR"] * dist_sub
        )

    met1, met2 = st.columns(2)

    with met1:
        st.metric(
            "R equivalente",
            f"{resistencia_fase_interface:.4f} Ω/km"
        )

    with met2:
        st.metric(
            "GMR equivalente",
            f"{gmr_fase_interface:.6f} m"
        )


# ============================================================
# COLUNA 2
# ============================================================

with col2:

    st.subheader("📐 3. COORDENADAS DAS FASES")

    st.caption(
        "Informe X e Y em metros. "
        "Y corresponde à altura no ponto de fixação."
    )

    col_a1, col_a2 = st.columns(2)

    with col_a1:
        xa = st.number_input(
            "XA (m)",
            value=-2.0,
            step=0.1
        )

    with col_a2:
        ya = st.number_input(
            "YA (m)",
            value=20.0,
            step=0.1
        )

    col_b1, col_b2 = st.columns(2)

    with col_b1:
        xb = st.number_input(
            "XB (m)",
            value=0.0,
            step=0.1
        )

    with col_b2:
        yb = st.number_input(
            "YB (m)",
            value=18.0,
            step=0.1
        )

    col_c1, col_c2 = st.columns(2)

    with col_c1:
        xc = st.number_input(
            "XC (m)",
            value=2.0,
            step=0.1
        )

    with col_c2:
        yc = st.number_input(
            "YC (m)",
            value=20.0,
            step=0.1
        )

    st.markdown("---")

    st.subheader("🛡️ 4. CABO PARA-RAIO")

    tem_pr = st.checkbox(
        "Existe cabo para-raio"
    )

    if tem_pr:

        cabo_pr_nome = st.selectbox(
            "Cabo para-raio",
            list(cabos_pr.keys())
        )

        flecha_pr = st.number_input(
            "Flecha do para-raio (m)",
            min_value=0.0,
            value=0.0,
            step=0.1
        )

        col_pr1, col_pr2 = st.columns(2)

        with col_pr1:
            xp = st.number_input(
                "XP (m)",
                value=0.0,
                step=0.1
            )

        with col_pr2:
            yp = st.number_input(
                "YP (m)",
                value=23.0,
                step=0.1
            )

    else:

        cabo_pr_nome = None
        flecha_pr = 0.0
        xp = 0.0
        yp = 0.0


# ============================================================
# BOTÃO DE CÁLCULO
# ============================================================

st.markdown("---")

calcular = st.button(
    "🔍 Calcular parâmetros elétricos",
    type="primary",
    use_container_width=True
)


# ============================================================
# CÁLCULO
# ============================================================

if calcular:

    try:

        # ----------------------------------------------------
        # DADOS DO CABO FASE
        # ----------------------------------------------------

        cf = cabos_fase[cabo_fase_nome]

        gmr_base = cf["GMR"]

        # Resistência equivalente dos cabos em paralelo
        rf = cf["R"] / n_sub

        # GMR equivalente
        if n_sub == 1:
            gmr_f = gmr_base
        else:
            gmr_f = np.sqrt(
                gmr_base * dist_sub
            )

        # ----------------------------------------------------
        # COORDENADAS EQUIVALENTES
        # ----------------------------------------------------

        coords = {
            "A": [
                xa,
                altura_equivalente(
                    ya,
                    flecha_fase,
                    delta_altura
                )
            ],
            "B": [
                xb,
                altura_equivalente(
                    yb,
                    flecha_fase,
                    delta_altura
                )
            ],
            "C": [
                xc,
                altura_equivalente(
                    yc,
                    flecha_fase,
                    delta_altura
                )
            ]
        }

        # ----------------------------------------------------
        # CABO PARA-RAIO
        # ----------------------------------------------------

        if tem_pr:

            cp = cabos_pr[cabo_pr_nome]

            gmr_p = cp["GMR"]
            rp = cp["R"]

            coords["P"] = [
                xp,
                altura_equivalente(
                    yp,
                    flecha_pr,
                    delta_altura
                )
            ]

        else:

            gmr_p = None
            rp = None

        condutores = list(coords.keys())

        n = len(condutores)

        # ----------------------------------------------------
        # VALIDAÇÃO DAS ALTURAS
        # ----------------------------------------------------

        for nome, ponto in coords.items():

            if ponto[1] <= 0:

                raise ValueError(
                    f"A altura equivalente do condutor "
                    f"{nome} deve ser maior que zero."
                )

        # ----------------------------------------------------
        # VALIDAÇÃO DAS POSIÇÕES
        # ----------------------------------------------------

        for i in range(n):

            for j in range(i + 1, n):

                distancia_condutores = distancia(
                    coords[condutores[i]],
                    coords[condutores[j]]
                )

                if distancia_condutores <= 0:

                    raise ValueError(
                        f"Os condutores {condutores[i]} e "
                        f"{condutores[j]} ocupam a mesma posição."
                    )

        # ----------------------------------------------------
        # MATRIZ DE INDUTÂNCIA
        # ----------------------------------------------------

        L = np.zeros(
            (n, n),
            dtype=float
        )

        for i, ci in enumerate(condutores):

            for j, cj in enumerate(condutores):

                pi = coords[ci]
                pj = coords[cj]

                if i == j:

                    if ci == "P":
                        gmr_condutor = gmr_p
                    else:
                        gmr_condutor = gmr_f

                    L[i, j] = K * np.log(
                        (2 * pi[1]) / gmr_condutor
                    )

                else:

                    d_imagem = distancia_imagem(
                        pi,
                        pj
                    )

                    d_real = distancia(
                        pi,
                        pj
                    )

                    L[i, j] = K * np.log(
                        d_imagem / d_real
                    )

        # Conversão de H/m para H/km

        L = L * 1000

        # ----------------------------------------------------
        # MATRIZ DE REATÂNCIA
        # ----------------------------------------------------

        X = (
            2 *
            np.pi *
            frequencia *
            L
        )

        # ----------------------------------------------------
        # MATRIZ DE RESISTÊNCIA
        # ----------------------------------------------------

        R = np.zeros_like(L)

        for i in range(3):
            R[i, i] = rf

        if tem_pr:
            R[3, 3] = rp

        # ----------------------------------------------------
        # MATRIZ DE IMPEDÂNCIA
        # ----------------------------------------------------

        Z = R + 1j * X

        # ----------------------------------------------------
        # REDUÇÃO DE KRON
        # ----------------------------------------------------

        if tem_pr:

            Z_ff = Z[0:3, 0:3]

            Z_fp = Z[0:3, 3].reshape(
                3,
                1
            )

            Z_pf = Z[3, 0:3].reshape(
                1,
                3
            )

            Z_pp = Z[3, 3]

            if abs(Z_pp) == 0:

                raise ValueError(
                    "A impedância própria do cabo "
                    "para-raio não pode ser nula."
                )

            Z_red = (
                Z_ff -
                (Z_fp @ Z_pf) / Z_pp
            )

        else:

            Z_red = Z

        # ----------------------------------------------------
        # IMPEDÂNCIAS POR FASE
        # ----------------------------------------------------

        ZA = (
            Z_red[0, 0] -
            0.5 * (
                Z_red[0, 1] +
                Z_red[0, 2]
            )
        )

        ZB = (
            Z_red[1, 1] -
            0.5 * (
                Z_red[1, 0] +
                Z_red[1, 2]
            )
        )

        ZC = (
            Z_red[2, 2] -
            0.5 * (
                Z_red[2, 0] +
                Z_red[2, 1]
            )
        )

        Z_med = (
            ZA +
            ZB +
            ZC
        ) / 3

        # ====================================================
        # RESULTADOS
        # ====================================================

        st.markdown("---")

        st.subheader("📋 PARÂMETROS ADOTADOS")

        parametros = {
            "Frequência":
                f"{frequencia:.2f} Hz",

            "Cabo fase":
                cabo_fase_nome,

            "Subcondutores por fase":
                n_sub,

            "Espaçamento do feixe":
                f"{dist_sub:.3f} m"
                if n_sub == 2
                else "N/A",

            "R do cabo individual":
                f"{cf['R']:.6f} Ω/km",

            "R equivalente da fase":
                f"{rf:.6f} Ω/km",

            "GMR do cabo individual":
                f"{gmr_base:.6f} m",

            "GMR equivalente da fase":
                f"{gmr_f:.6f} m",

            "Cabo para-raio":
                cabo_pr_nome
                if tem_pr
                else "Não considerado",

            "Ajuste ΔH":
                f"{delta_altura:.2f} m"
        }

        df_parametros = pd.DataFrame(
            list(parametros.items()),
            columns=[
                "Parâmetro",
                "Valor"
            ]
        )

        st.dataframe(
            df_parametros,
            hide_index=True,
            use_container_width=True
        )

        # ====================================================
        # RESULTADO PRINCIPAL
        # ====================================================

        st.markdown("---")

        st.subheader("🎯 RESULTADO PRINCIPAL")

        col_result1, col_result2, col_result3 = st.columns(3)

        with col_result1:

            st.metric(
                "R médio",
                f"{Z_med.real:.6f} Ω/km"
            )

        with col_result2:

            st.metric(
                "X médio",
                f"{Z_med.imag:.6f} Ω/km"
            )

        with col_result3:

            st.metric(
                "|Z| médio",
                f"{abs(Z_med):.6f} Ω/km"
            )

        st.info(
            f"Z médio = "
            f"{Z_med.real:.6f} "
            f"{Z_med.imag:+.6f}j Ω/km"
            f" | Ângulo = "
            f"{np.angle(Z_med, deg=True):.3f}°"
        )

        # ====================================================
        # IMPEDÂNCIA POR FASE
        # ====================================================

        st.markdown("---")

        st.subheader(
            "📊 IMPEDÂNCIA CALCULADA POR FASE"
        )

        dados_fases = [
            {
                "Fase": "A",
                "R (Ω/km)": ZA.real,
                "X (Ω/km)": ZA.imag,
                "|Z| (Ω/km)": abs(ZA),
                "Ângulo (°)": np.angle(
                    ZA,
                    deg=True
                )
            },
            {
                "Fase": "B",
                "R (Ω/km)": ZB.real,
                "X (Ω/km)": ZB.imag,
                "|Z| (Ω/km)": abs(ZB),
                "Ângulo (°)": np.angle(
                    ZB,
                    deg=True
                )
            },
            {
                "Fase": "C",
                "R (Ω/km)": ZC.real,
                "X (Ω/km)": ZC.imag,
                "|Z| (Ω/km)": abs(ZC),
                "Ângulo (°)": np.angle(
                    ZC,
                    deg=True
                )
            },
            {
                "Fase": "Média",
                "R (Ω/km)": Z_med.real,
                "X (Ω/km)": Z_med.imag,
                "|Z| (Ω/km)": abs(Z_med),
                "Ângulo (°)": np.angle(
                    Z_med,
                    deg=True
                )
            }
        ]

        df_fases = pd.DataFrame(
            dados_fases
        )

        st.dataframe(
            df_fases.style.format(
                precision=6
            ),
            hide_index=True,
            use_container_width=True
        )

        # ====================================================
        # MATRIZES
        # ====================================================

        st.markdown("---")

        st.subheader("🧮 MATRIZES")

        abas = st.tabs([
            "Indutância",
            "Reatância",
            "Resistência",
            "Impedância",
            "Matriz reduzida"
        ])

        # ----------------------------------------------------
        # MATRIZ DE INDUTÂNCIA
        # ----------------------------------------------------

        with abasst.caption(
                "Matriz de indutância L em H/km"
            )

            df_L = dataframe_real(
                L,
                condutores
            )

            st.dataframe(
                df_L.style.format(
                    precision=9
                ),
                use_container_width=True
            )

        # ----------------------------------------------------
        # MATRIZ DE REATÂNCIA
        # ----------------------------------------------------

        with abasst.caption(
                "Matriz de reatância indutiva X em Ω/km"
            )

            df_X = dataframe_real(
                X,
                condutores
            )

            st.dataframe(
                df_X.style.format(
                    precision=6
                ),
                use_container_width=True
            )

        # ----------------------------------------------------
        # MATRIZ DE RESISTÊNCIA
        # ----------------------------------------------------

        with abasst.caption(
                "Matriz de resistência R em Ω/km"
            )

            df_R = dataframe_real(
                R,
                condutores
            )

            st.dataframe(
                df_R.style.format(
                    precision=6
                ),
                use_container_width=True
            )

        # ----------------------------------------------------
        # MATRIZ DE IMPEDÂNCIA
        # ----------------------------------------------------

        with abasst.caption(
                "Matriz complexa Z = R + jX em Ω/km"
            )

            df_Z = dataframe_complexo(
                Z,
                condutores
            )

            st.dataframe(
                df_Z,
                use_container_width=True
            )

        # ----------------------------------------------------
        # MATRIZ REDUZIDA
        # ----------------------------------------------------

        with abasif tem_pr:

                st.caption(
                    "Matriz 3 × 3 das fases "
                    "após a redução de Kron"
                )

            else:

                st.caption(
                    "Sem cabo para-raio, a matriz "
                    "reduzida coincide com a matriz "
                    "das fases."
                )

            df_Z_red = dataframe_complexo(
                Z_red,
                ["A", "B", "C"]
            )

            st.dataframe(
                df_Z_red,
                use_container_width=True
            )

        # ====================================================
        # GEOMETRIA
        # ====================================================

        st.markdown("---")

        st.subheader("📈 GEOMETRIA DA LINHA")

        figura = plotar_geometria(
            coords
        )

        st.pyplot(
            figura,
            use_container_width=True
        )

        plt.close(figura)

        # ====================================================
        # INFORMAÇÕES ADICIONAIS
        # ====================================================

        with st.expander(
            "ℹ️ INFORMAÇÕES ADICIONAIS",
            expanded=False
        ):

            st.write(
                "A resistência equivalente da fase "
                "é dividida pelo número de "
                "subcondutores em paralelo."
            )

            st.write(
                "Para dois subcondutores, o GMR "
                "equivalente é calculado por:"
            )

            st.latex(
                r"GMR_{eq} = \sqrt{GMR \cdot d}"
            )

            st.write(
                "Quando existe cabo para-raio, "
                "a influência dele é incorporada "
                "à matriz trifásica por meio da "
                "redução de Kron."
            )

            st.warning(
                "O valor apresentado como Z médio "
                "segue a formulação do código-base. "
                "Ele não deve ser considerado "
                "automaticamente como a impedância "
                "de sequência positiva Z₁."
            )

    except Exception as erro:

        st.error(
            f"❌ Erro no cálculo: {erro}"
        )

        st.exception(erro)
