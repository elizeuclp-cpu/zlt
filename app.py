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
    "Cálculo das matrizes de indutância, reatância, "
    "resistência e impedância série da linha."
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

        linha_formatada = []

        for valor in linha:

            linha_formatada.append(
                f"{valor.real:.6f} {valor.imag:+.6f}j"
            )

        dados.append(linha_formatada)

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

    fig, ax = plt.subplots(
        figsize=(8, 5)
    )

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

    # Linha representando o solo

    ax.axhline(
        y=0,
        color="saddlebrown",
        linewidth=2,
        label="Solo"
    )

    ax.set_xlabel(
        "Coordenada horizontal X (m)"
    )

    ax.set_ylabel(
        "Altura equivalente Y (m)"
    )

    ax.set_title(
        "Geometria equivalente dos condutores"
    )

    ax.grid(
        True,
        alpha=0.25
    )

    ax.legend()

    fig.tight_layout()

    return fig


# ============================================================
# INTERFACE
# ============================================================

col1, col2 = st.columns(
    [1, 1],
    gap="large"
)


# ============================================================
# COLUNA 1
# ============================================================

with col1:

    # --------------------------------------------------------
    # CONFIGURAÇÕES GERAIS
    # --------------------------------------------------------

    st.subheader(
        "⚙️ 1. CONFIGURAÇÕES GERAIS"
    )

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

    # --------------------------------------------------------
    # CABO DAS FASES
    # --------------------------------------------------------

    st.subheader(
        "🔌 2. CABO DAS FASES"
    )

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

    # --------------------------------------------------------
    # RESULTADOS PRELIMINARES
    # --------------------------------------------------------

    cf_interface = cabos_fase[
        cabo_fase_nome
    ]

    resistencia_fase_interface = (
        cf_interface["R"] / n_sub
    )

    if n_sub == 1:

        gmr_fase_interface = (
            cf_interface["GMR"]
        )

    else:

        gmr_fase_interface = np.sqrt(
            cf_interface["GMR"] *
            dist_sub
        )

    metric1, metric2 = st.columns(2)

    with metric1:

        st.metric(
            "R equivalente",
            f"{resistencia_fase_interface:.4f} Ω/km"
        )

    with metric2:

        st.metric(
            "GMR equivalente",
            f"{gmr_fase_interface:.6f} m"
        )


# ============================================================
# COLUNA 2
# ============================================================

with col2:

    # --------------------------------------------------------
    # COORDENADAS
    # --------------------------------------------------------

    st.subheader(
        "📐 3. COORDENADAS DAS FASES"
    )

    st.caption(
        "Informe as coordenadas X e Y em metros. "
        "Y corresponde à altura do condutor."
    )

    # FASE A

    ca1, ca2 = st.columns(2)

    with ca1:

        xa = st.number_input(
            "XA (m)",
            value=-2.0,
            step=0.1
        )

    with ca2:

        ya = st.number_input(
            "YA (m)",
            value=20.0,
            step=0.1
        )

    # FASE B

    cb1, cb2 = st.columns(2)

    with cb1:

        xb = st.number_input(
            "XB (m)",
            value=0.0,
            step=0.1
        )

    with cb2:

        yb = st.number_input(
            "YB (m)",
            value=18.0,
            step=0.1
        )

    # FASE C

    cc1, cc2 = st.columns(2)

    with cc1:

        xc = st.number_input(
            "XC (m)",
            value=2.0,
            step=0.1
        )

    with cc2:

        yc = st.number_input(
            "YC (m)",
            value=20.0,
            step=0.1
        )

    st.markdown("---")

    # --------------------------------------------------------
    # CABO PARA-RAIO
    # --------------------------------------------------------

    st.subheader(
        "🛡️ 4. CABO PARA-RAIO"
    )

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

        cpr1, cpr2 = st.columns(2)

        with cpr1:

            xp = st.number_input(
                "XP (m)",
                value=0.0,
                step=0.1
            )

        with cpr2:

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
# EXECUTAR CÁLCULO
# ============================================================

if calcular:

    try:

        # ----------------------------------------------------
        # DADOS CABO FASE
        # ----------------------------------------------------

        cf = cabos_fase[
            cabo_fase_nome
        ]

        GMR_base = cf["GMR"]

        # ----------------------------------------------------
        # RESISTÊNCIA EQUIVALENTE
        #
        # Para cabos em paralelo:
        #
        # 1 subconductor: R
        # 2 subconductores: R / 2
        # ----------------------------------------------------

        Rf = cf["R"] / n_sub

        # ----------------------------------------------------
        # GMR EQUIVALENTE
        # ----------------------------------------------------

        if n_sub == 1:

            GMR_f = GMR_base

        else:

            GMR_f = np.sqrt(
                GMR_base *
                dist_sub
            )

        # ----------------------------------------------------
        # COORDENADAS
        # ----------------------------------------------------

        coords = {}

        coords["A"] = [
            xa,
            altura_equivalente(
                ya,
                flecha_fase,
                delta_altura
            )
        ]

        coords["B"] = [
            xb,
            altura_equivalente(
                yb,
                flecha_fase,
                delta_altura
            )
        ]

        coords["C"] = [
            xc,
            altura_equivalente(
                yc,
                flecha_fase,
                delta_altura
            )
        ]

        # ----------------------------------------------------
        # CABO PARA-RAIO
        # ----------------------------------------------------

        if tem_pr:

            cp = cabos_pr[
                cabo_pr_nome
            ]

            GMR_P = cp["GMR"]

            Rp = cp["R"]

            coords["P"] = [
                xp,
                altura_equivalente(
                    yp,
                    flecha_pr,
                    delta_altura
                )
            ]

        else:

            GMR_P = None

            Rp = None

        # ----------------------------------------------------
        # LISTA DE CONDUTORES
        # ----------------------------------------------------

        condutores = [
            "A",
            "B",
            "C"
        ]

        if tem_pr:
            condutores.append("P")

        n = len(
            condutores
        )

        # ----------------------------------------------------
        # VALIDAÇÃO DAS ALTURAS
        # ----------------------------------------------------

        for nome in condutores:

            altura = coords[nome][1]

            if altura <= 0:

                raise ValueError(
                    f"A altura equivalente do "
                    f"condutor {nome} deve ser "
                    f"maior que zero."
                )

        # ----------------------------------------------------
        # VALIDAÇÃO DAS DISTÂNCIAS
        # ----------------------------------------------------

        for i in range(n):

            for j in range(
                i + 1,
                n
            ):

                ci = condutores[i]

                cj = condutores[j]

                dij = distancia(
                    coords[ci],
                    coords[cj]
                )

                if dij <= 0:

                    raise ValueError(
                        f"Os condutores {ci} "
                        f"e {cj} ocupam a "
                        f"mesma posição."
                    )

        # ====================================================
        # MATRIZ DE INDUTÂNCIA
        # ====================================================

        L = np.zeros(
            (n, n)
        )

        for i, ci in enumerate(
            condutores
        ):

            for j, cj in enumerate(
                condutores
            ):

                pi = coords[ci]

                pj = coords[cj]

                # --------------------------------------------
                # ELEMENTOS DA DIAGONAL
                # --------------------------------------------

                if i == j:

                    if ci == "P":

                        GMR = GMR_P

                    else:

                        GMR = GMR_f

                    L[i, j] = (
                        K *
                        np.log(
                            (2 * pi[1]) /
                            GMR
                        )
                    )

                # --------------------------------------------
                # ELEMENTOS FORA DA DIAGONAL
                # --------------------------------------------

                else:

                    D_imagem = distancia_imagem(
                        pi,
                        pj
                    )

                    D_real = distancia(
                        pi,
                        pj
                    )

                    L[i, j] = (
                        K *
                        np.log(
                            D_imagem /
                            D_real
                        )
                    )

        # H/m -> H/km

        L = L * 1000


        # ====================================================
        # MATRIZ DE REATÂNCIA
        # ====================================================

        X = (
            2 *
            np.pi *
            frequencia *
            L
        )


        # ====================================================
        # MATRIZ DE RESISTÊNCIA
        # ====================================================

        R = np.zeros_like(
            L
        )

        # Fases A, B e C

        for i in range(3):

            R[i, i] = Rf

        # Cabo para-raio

        if tem_pr:

            R[3, 3] = Rp


        # ====================================================
        # MATRIZ DE IMPEDÂNCIA
        # ====================================================

        Z = (
            R +
            1j * X
        )


        # ====================================================
        # REDUÇÃO DE KRON
        # ====================================================

        if tem_pr:

            Z_ff = Z[
                0:3,
                0:3
            ]

            Z_fp = Z[
                0:3,
                3
            ].reshape(
                3,
                1
            )

            Z_pf = Z[
                3,
                0:3
            ].reshape(
                1,
                3
            )

            Z_pp = Z[
                3,
                3
            ]

            if abs(Z_pp) == 0:

                raise ValueError(
                    "A impedância própria do "
                    "cabo para-raio não pode "
                    "ser nula."
                )

            Z_red = (
                Z_ff -
                (Z_fp @ Z_pf) /
                Z_pp
            )

        else:

            Z_red = Z


        # ====================================================
        # IMPEDÂNCIAS POR FASE
        # ====================================================

        ZA = (
            Z_red[0, 0] -
            0.5 *
            (
                Z_red[0, 1] +
                Z_red[0, 2]
            )
        )

        ZB = (
            Z_red[1, 1] -
            0.5 *
            (
                Z_red[1, 0] +
                Z_red[1, 2]
            )
        )

        ZC = (
            Z_red[2, 2] -
            0.5 *
            (
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
        # PARÂMETROS ADOTADOS
        # ====================================================

        st.markdown("---")

        st.subheader(
            "📋 PARÂMETROS ADOTADOS"
        )

        parametros = {
            "Frequência":
                f"{frequencia:.2f} Hz",

            "Cabo fase":
                cabo_fase_nome,

            "Subcondutores por fase":
                n_sub,

            "Espaçamento do feixe":
                (
                    f"{dist_sub:.3f} m"
                    if n_sub == 2
                    else "N/A"
                ),

            "R do cabo individual":
                f"{cf['R']:.6f} Ω/km",

            "R equivalente da fase":
                f"{Rf:.6f} Ω/km",

            "GMR do cabo individual":
                f"{GMR_base:.6f} m",

            "GMR equivalente da fase":
                f"{GMR_f:.6f} m",

            "Cabo para-raio":
                (
                    cabo_pr_nome
                    if tem_pr
                    else "Não considerado"
                ),

            "Ajuste ΔH":
                f"{delta_altura:.2f} m"
        }

        df_parametros = pd.DataFrame(
            list(
                parametros.items()
            ),
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

        st.subheader(
            "🎯 RESULTADO PRINCIPAL"
        )

        res1, res2, res3 = st.columns(3)

        with res1:

            st.metric(
                "R médio",
                f"{Z_med.real:.6f} Ω/km"
            )

        with res2:

            st.metric(
                "X médio",
                f"{Z_med.imag:.6f} Ω/km"
            )

        with res3:

            st.metric(
                "|Z| médio",
                f"{abs(Z_med):.6f} Ω/km"
            )

        angulo_med = np.angle(
            Z_med,
            deg=True
        )

        st.info(
            f"Z médio = "
            f"{Z_med.real:.6f} "
            f"{Z_med.imag:+.6f}j Ω/km"
            f" | "
            f"|Z| = {abs(Z_med):.6f} Ω/km"
            f" | "
            f"Ângulo = {angulo_med:.3f}°"
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
                {
                    "R (Ω/km)": "{:.6f}",
                    "X (Ω/km)": "{:.6f}",
                    "|Z| (Ω/km)": "{:.6f}",
                    "Ângulo (°)": "{:.3f}"
                }
            ),
            hide_index=True,
            use_container_width=True
        )


        # ====================================================
        # MATRIZES
        # ====================================================

        st.markdown("---")

        st.subheader(
            "🧮 MATRIZES"
        )

        abas = st.tabs(
            [
                "Indutância",
                "Reatância",
                "Resistência",
                "Impedância",
                "Matriz reduzida"
            ]
        )


        # ====================================================
        # ABA 1 - INDUTÂNCIA
        # ====================================================

        with abasst.caption(
                "Matriz de indutância L em H/km"
            )

            df_L = dataframe_real(
                L,
                condutores
            )

            st.dataframe(
                df_L.style.format(
                    "{:.9f}"
                ),
                use_container_width=True
            )


        # ====================================================
        # ABA 2 - REATÂNCIA
        # ====================================================

        with abasst.caption(
                "Matriz de reatância "
                "indutiva X em Ω/km"
            )

            df_X = dataframe_real(
                X,
                condutores
            )

            st.dataframe(
                df_X.style.format(
                    "{:.6f}"
                ),
                use_container_width=True
            )


        # ====================================================
        # ABA 3 - RESISTÊNCIA
        # ====================================================

        with abasst.caption(
                "Matriz de resistência "
                "R em Ω/km"
            )

            df_R = dataframe_real(
                R,
                condutores
            )

            st.dataframe(
                df_R.style.format(
                    "{:.6f}"
                ),
                use_container_width=True
            )


        # ====================================================
        # ABA 4 - IMPEDÂNCIA
        # ====================================================

        with abasst.caption(
                "Matriz complexa "
                "Z = R + jX em Ω/km"
            )

            df_Z = dataframe_complexo(
                Z,
                condutores
            )

            st.dataframe(
                df_Z,
                use_container_width=True
            )


        # ====================================================
        # ABA 5 - MATRIZ REDUZIDA
        # ====================================================

        with abasif tem_pr:

                st.caption(
                    "Matriz 3 × 3 das fases "
                    "após a redução de Kron"
                )

            else:

                st.caption(
                    "Sem cabo para-raio, "
                    "a matriz reduzida coincide "
                    "com a matriz das fases."
                )

            df_Z_red = dataframe_complexo(
                Z_red,
                [
                    "A",
                    "B",
                    "C"
                ]
            )

            st.dataframe(
                df_Z_red,
                use_container_width=True
            )


        # ====================================================
        # GEOMETRIA
        # ====================================================

        st.markdown("---")

        st.subheader(
            "📈 GEOMETRIA DA LINHA"
        )

        figura = plotar_geometria(
            coords
        )

        st.pyplot(
            figura,
            use_container_width=True
        )

        plt.close(
            figura
        )


        # ====================================================
        # INFORMAÇÕES ADICIONAIS
        # ====================================================

        with st.expander(
            "ℹ️ INFORMAÇÕES ADICIONAIS",
            expanded=False
        ):

            st.markdown(
                "### Resistência equivalente"
            )

            st.write(
                "Para subcondutores idênticos "
                "em paralelo, a resistência "
                "equivalente da fase é:"
            )

            st.latex(
                r"R_{eq} = \frac{R}{n}"
            )

            st.write(
                f"Neste caso: R individual = "
                f"{cf['R']:.6f} Ω/km"
            )

            st.write(
                f"Número de subcondutores = "
                f"{n_sub}"
            )

            st.write(
                f"R equivalente = "
                f"{Rf:.6f} Ω/km"
            )

            st.markdown(
                "### GMR equivalente"
            )

            if n_sub == 1:

                st.latex(
                    r"GMR_{eq} = GMR"
                )

            else:

                st.latex(
                    r"GMR_{eq} = "
                    r"\sqrt{GMR \cdot d}"
                )

                st.write(
                    f"Espaçamento do feixe = "
                    f"{dist_sub:.3f} m"
                )

            st.write(
                f"GMR equivalente utilizado = "
                f"{GMR_f:.6f} m"
            )

            if tem_pr:

                st.markdown(
                    "### Redução de Kron"
                )

                st.write(
                    "Como existe cabo para-raio, "
                    "a influência elétrica dele "
                    "é incorporada à matriz das "
                    "fases pela redução de Kron."
                )

                st.latex(
                    r"Z_{red} = "
                    r"Z_{ff} - "
                    r"Z_{fp}"
                    r"Z_{pp}^{-1}"
                    r"Z_{pf}"
                )

            st.warning(
                "O valor denominado Z médio "
                "segue a mesma formulação do "
                "código-base fornecido. "
                "Ele não deve ser interpretado "
                "automaticamente como a "
                "impedância de sequência "
                "positiva Z₁."
            )


    # ========================================================
    # ERROS
    # ========================================================

    except Exception as erro:

        st.error(
            f"❌ Erro no cálculo: {erro}"
        )

        st.exception(
            erro
        )
