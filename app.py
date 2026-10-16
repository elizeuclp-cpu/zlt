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


def criar_dataframe_real(matriz, nomes):
    return pd.DataFrame(
        matriz,
        index=nomes,
        columns=nomes
    )


def criar_dataframe_complexo(matriz, nomes):

    dados = []

    for linha in matriz:

        linha_formatada = []

        for valor in linha:

            texto = (
                f"{valor.real:.6f} "
                f"{valor.imag:+.6f}j"
            )

            linha_formatada.append(texto)

        dados.append(linha_formatada)

    return pd.DataFrame(
        dados,
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
            color=cores.get(nome, "black"),
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

    plt.tight_layout()

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


    # ========================================================
    # CABO FASE
    # ========================================================

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
        format_func=lambda x:
        "1 condutor"
        if x == 1
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


    # ========================================================
    # VALORES EQUIVALENTES
    # ========================================================

    cabo_selecionado = cabos_fase[
        cabo_fase_nome
    ]


    R_individual = cabo_selecionado["R"]


    R_equivalente = (
        R_individual / n_sub
    )


    if n_sub == 1:

        GMR_equivalente = (
            cabo_selecionado["GMR"]
        )

    else:

        GMR_equivalente = np.sqrt(
            cabo_selecionado["GMR"]
            * dist_sub
        )


    coluna_r, coluna_gmr = st.columns(2)


    with coluna_r:

        st.metric(
            "R equivalente",
            f"{R_equivalente:.4f} Ω/km"
        )


    with coluna_gmr:

        st.metric(
            "GMR equivalente",
            f"{GMR_equivalente:.6f} m"
        )


# ============================================================
# COLUNA 2
# ============================================================

with col2:

    st.subheader(
        "📐 3. COORDENADAS DAS FASES"
    )


    st.caption(
        "Informe as coordenadas X e Y em metros."
    )


    # ========================================================
    # FASE A
    # ========================================================

    a1, a2 = st.columns(2)


    with a1:

        xa = st.number_input(
            "XA (m)",
            value=-2.0,
            step=0.1
        )


    with a2:

        ya = st.number_input(
            "YA (m)",
            value=20.0,
            step=0.1
        )


    # ========================================================
    # FASE B
    # ========================================================

    b1, b2 = st.columns(2)


    with b1:

        xb = st.number_input(
            "XB (m)",
            value=0.0,
            step=0.1
        )


    with b2:

        yb = st.number_input(
            "YB (m)",
            value=18.0,
            step=0.1
        )


    # ========================================================
    # FASE C
    # ========================================================

    c1, c2 = st.columns(2)


    with c1:

        xc = st.number_input(
            "XC (m)",
            value=2.0,
            step=0.1
        )


    with c2:

        yc = st.number_input(
            "YC (m)",
            value=20.0,
            step=0.1
        )


    st.markdown("---")


    # ========================================================
    # PARA-RAIO
    # ========================================================

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


        p1, p2 = st.columns(2)


        with p1:

            xp = st.number_input(
                "XP (m)",
                value=0.0,
                step=0.1
            )


        with p2:

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
# BOTÃO
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

        # ====================================================
        # CABO FASE
        # ====================================================

        cf = cabos_fase[
            cabo_fase_nome
        ]


        GMR_base = cf["GMR"]


        # IMPORTANTE:
        # Resistência do feixe
        Rf = (
            cf["R"] / n_sub
        )


        # ====================================================
        # GMR DO FEIXE
        # ====================================================

        if n_sub == 1:

            GMR_f = GMR_base

        else:

            GMR_f = np.sqrt(
                GMR_base *
                dist_sub
            )


        # ====================================================
        # COORDENADAS
        # ====================================================

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


        # ====================================================
        # PARA-RAIO
        # ====================================================

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


        # ====================================================
        # CONDUTORES
        # ====================================================

        condutores = [
            "A",
            "B",
            "C"
        ]


        if tem_pr:

            condutores.append(
                "P"
            )


        n = len(condutores)


        # ====================================================
        # VALIDAÇÃO
        # ====================================================

        for nome in condutores:

            if coords[nome][1] <= 0:

                raise ValueError(
                    f"A altura equivalente do "
                    f"condutor {nome} deve ser "
                    f"maior que zero."
                )


        for i in range(n):

            for j in range(
                i + 1,
                n
            ):

                ci = condutores[i]

                cj = condutores[j]


                D = distancia(
                    coords[ci],
                    coords[cj]
                )


                if D <= 0:

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


                else:

                    D_real = distancia(
                        pi,
                        pj
                    )


                    D_imagem = distancia_imagem(
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


        # H/m para H/km

        L *= 1000


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


        for i in range(3):

            R[i, i] = Rf


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
                    "A impedância do "
                    "para-raio não pode "
                    "ser zero."
                )


            Z_red = (
                Z_ff -
                (Z_fp @ Z_pf) /
                Z_pp
            )


        else:

            Z_red = Z


        # ====================================================
        # IMPEDÂNCIAS
        # ====================================================

        ZA = (
            Z_red[0, 0]
            - 0.5 *
            (
                Z_red[0, 1]
                + Z_red[0, 2]
            )
        )


        ZB = (
            Z_red[1, 1]
            - 0.5 *
            (
                Z_red[1, 0]
                + Z_red[1, 2]
            )
        )


        ZC = (
            Z_red[2, 2]
            - 0.5 *
            (
                Z_red[2, 0]
                + Z_red[2, 1]
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

            "GMR individual":
                f"{GMR_base:.6f} m",

            "GMR equivalente":
                f"{GMR_f:.6f} m",

            "Cabo para-raio":
                (
                    cabo_pr_nome
                    if tem_pr
                    else "Não considerado"
                ),

            "Ajuste de altura":
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


        st.subheader(
            "🎯 RESULTADO PRINCIPAL"
        )


        resultado1, resultado2, resultado3 = st.columns(3)


        with resultado1:

            st.metric(
                "R médio",
                f"{Z_med.real:.6f} Ω/km"
            )


        with resultado2:

            st.metric(
                "X médio",
                f"{Z_med.imag:.6f} Ω/km"
            )


        with resultado3:

            st.metric(
                "|Z| médio",
                f"{abs(Z_med):.6f} Ω/km"
            )


        angulo = np.angle(
            Z_med,
            deg=True
        )


        st.info(
            f"Z médio = "
            f"{Z_med.real:.6f} "
            f"{Z_med.imag:+.6f}j Ω/km"
            f" | "
            f"Ângulo = {angulo:.3f}°"
        )


        # ====================================================
        # RESULTADOS POR FASE
        # ====================================================

        st.markdown("---")


        st.subheader(
            "📊 IMPEDÂNCIA CALCULADA POR FASE"
        )


        resultados = [
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


        df_resultados = pd.DataFrame(
            resultados
        )


        st.dataframe(
            df_resultados,
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
        # INDUTÂNCIA
        # ====================================================

        with abasst.caption(
                "Matriz de indutância L (H/km)"
            )

            df_L = criar_dataframe_real(
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
        # REATÂNCIA
        # ====================================================

        with abasst.caption(
                "Matriz de reatância X (Ω/km)"
            )

            df_X = criar_dataframe_real(
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
        # RESISTÊNCIA
        # ====================================================

        with abasst.caption(
                "Matriz de resistência R (Ω/km)"
            )

            df_R = criar_dataframe_real(
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
        # IMPEDÂNCIA
        # ====================================================

        with abasst.caption(
                "Matriz de impedância Z (Ω/km)"
            )

            df_Z = criar_dataframe_complexo(
                Z,
                condutores
            )

            st.dataframe(
                df_Z,
                use_container_width=True
            )


        # ====================================================
        # MATRIZ REDUZIDA
        # ====================================================

        with abasif tem_pr:

                st.caption(
                    "Matriz das fases após "
                    "a redução de Kron"
                )

            else:

                st.caption(
                    "Matriz das fases"
                )


            df_Z_red = criar_dataframe_complexo(
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

        st.markdown("---")


        with st.expander(
            "ℹ️ INFORMAÇÕES ADICIONAIS",
            expanded=False
        ):

            st.markdown(
                "#### Resistência equivalente"
            )


            st.latex(
                r"R_{eq} = \frac{R}{n}"
            )


            st.write(
                f"R individual = "
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
                "#### GMR equivalente"
            )


            if n_sub == 1:

                st.latex(
                    r"GMR_{eq}=GMR"
                )


            else:

                st.latex(
                    r"GMR_{eq}="
                    r"\sqrt{GMR \cdot d}"
                )


            st.write(
                f"GMR equivalente = "
                f"{GMR_f:.6f} m"
            )


            if tem_pr:

                st.markdown(
                    "#### Redução de Kron"
                )


                st.latex(
                    r"Z_{red}="
                    r"Z_{ff}-"
                    r"Z_{fp}"
                    r"Z_{pp}^{-1}"
                    r"Z_{pf}"
                )


            st.warning(
                "O Z médio apresentado segue "
                "a formulação do código original "
                "e não deve ser interpretado "
                "automaticamente como Z₁."
            )


    except Exception as erro:

        st.error(
            f"❌ Erro no cálculo: {erro}"
        )

        st.exception(
            erro
        )
