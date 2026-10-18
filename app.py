import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# CONFIGURACAO DA PAGINA
# ============================================================

st.set_page_config(
    page_title="ZLT - Calculadora de Impedância de Linhas Aéreas",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.title("⚡ ZLT - Calculadora de Impedância de Linhas Aéreas")

st.caption(
    "Calculo das matrizes de indutância, reatância, "
    "resistencia e impedância série da linha."
)

st.markdown("---")


# ============================================================
# CONSTANTES
# ============================================================

MU0 = 4 * np.pi * 1e-7
K = MU0 / (2 * np.pi)


# ============================================================
# DADOS DOS CABOS DE FASE
# ============================================================

CABOS_FASE = {
    "Linnet (336,4 MCM)": {
        "GMR": 0.00742,
        "diam": 0.01831,
        "R": 0.203,
    },
    "Grosbeak (636 MCM)": {
        "GMR": 0.01021,
        "diam": 0.02515,
        "R": 0.108,
    },
    "Raven (1/0 AWG)": {
        "GMR": 0.00388,
        "diam": 0.01011,
        "R": 0.709,
    },
    "Penguin (4/0 AWG)": {
        "GMR": 0.00550,
        "diam": 0.01431,
        "R": 0.380,
    },
    "Cairo (465,4 MCM)": {
        "GMR": 0.00753,
        "diam": 0.01990,
        "R": 0.170,
    },
    "Flint (740,8 MCM)": {
        "GMR": 0.00966,
        "diam": 0.02513,
        "R": 0.108,
    },
}


# ============================================================
# DADOS DOS CABOS PARA-RAIOS
# ============================================================

CABOS_PR = {
    '5/16"': {
        "GMR": 0.0025,
        "diam": 0.00794,
        "R": 4.76 * (1 + 0.004 * (75 - 20)),
    },
    '3/8"': {
        "GMR": 0.0030,
        "diam": 0.00952,
        "R": 3.44 * (1 + 0.004 * (75 - 20)),
    },
}


# ============================================================
# FUNÇÕES 
# ============================================================

def altura_equivalente(y, flecha, delta_h):
    return y - (2 / 3) * flecha + delta_h


def distancia(p1, p2):
    return np.hypot(
        p1[0] - p2[0],
        p1[1] - p2[1],
    )


def distancia_imagem(p1, p2):
    return np.hypot(
        p1[0] - p2[0],
        p1[1] + p2[1],
    )


def df_real(matriz, nomes):
    return pd.DataFrame(
        matriz,
        index=nomes,
        columns=nomes,
    )


def df_complexo(matriz, nomes):

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
        columns=nomes,
    )


def df_polar(matriz, nomes):

    dados = []

    for linha in matriz:

        linha_formatada = []

        for valor in linha:

            valor_c = complex(valor)

            modulo = abs(valor_c)

            angulo = np.angle(
                valor_c,
                deg=True,
            )

            texto = (
                f"{modulo:.6f} "
                f"∠ {angulo:+.3f}°"
            )

            linha_formatada.append(texto)

        dados.append(linha_formatada)

    return pd.DataFrame(
        dados,
        index=nomes,
        columns=nomes,
    )


def plotar_geometria(coords):

    fig, ax = plt.subplots(
        figsize=(8, 5)
    )

    cores = {
        "A": "red",
        "B": "blue",
        "C": "green",
        "P": "gray",
    }

    for nome, ponto in coords.items():

        x = ponto[0]
        y = ponto[1]

        ax.scatter(
            x,
            y,
            s=120,
            color=cores.get(nome, "black"),
            zorder=3,
        )

        ax.annotate(
            nome,
            (x, y),
            xytext=(7, 7),
            textcoords="offset points",
            fontweight="bold",
        )

    ax.axhline(
        y=0,
        color="saddlebrown",
        linewidth=2,
        label="Solo",
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
        alpha=0.25,
    )

    ax.legend()

    fig.tight_layout()

    return fig


# ============================================================
# INTERFACE
# ============================================================

col1, col2 = st.columns(
    [1, 1],
    gap="large",
)


# ============================================================
# COLUNA 1
# ============================================================

with col1:

    st.subheader(
        "⚙️ 1. CONFIGURAÇÕES GERAIS"
    )

    frequencia = st.number_input(
        "Frequencia (Hz)",
        min_value=1.0,
        value=60.0,
        step=1.0,
    )

    delta_altura = st.slider(
        "Ajuste de altura delta H (m)",
        min_value=-20.0,
        max_value=20.0,
        value=0.0,
        step=0.5,
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
        list(CABOS_FASE.keys()),
    )

    n_sub = st.selectbox(
        "Subcondutores por fase",
        [1, 2],
        format_func=lambda valor: (
            "1 condutor"
            if valor == 1
            else "2 subcondutores"
        ),
    )

    dist_sub = st.number_input(
        "Espacamento do feixe (m)",
        min_value=0.001,
        value=0.305,
        step=0.005,
        disabled=(n_sub == 1),
    )

    flecha_fase = st.number_input(
        "Flecha das fases (m)",
        min_value=0.0,
        value=0.0,
        step=0.1,
    )

    # --------------------------------------------------------
    # RESULTADOS PRELIMINARES
    # --------------------------------------------------------

    cabo_interface = CABOS_FASE[
        cabo_fase_nome
    ]

    r_interface = (
        cabo_interface["R"] / n_sub
    )

    if n_sub == 1:

        gmr_interface = (
            cabo_interface["GMR"]
        )

    else:

        gmr_interface = np.sqrt(
            cabo_interface["GMR"]
            * dist_sub
        )

    met1, met2 = st.columns(2)

    with met1:

        st.metric(
            "R equivalente",
            f"{r_interface:.4f} ohm/km",
        )

    with met2:

        st.metric(
            "GMR equivalente",
            f"{gmr_interface:.6f} m",
        )


# ============================================================
# COLUNA 2
# ============================================================

with col2:

    st.subheader(
        "📐 3. COORDENADAS DAS FASES"
    )

    st.caption(
        "Informe X e Y em metros. "
        "Y corresponde a altura do condutor."
    )

    # --------------------------------------------------------
    # FASE A
    # --------------------------------------------------------

    a1, a2 = st.columns(2)

    with a1:

        xa = st.number_input(
            "XA (m)",
            value=-2.0,
            step=0.1,
        )

    with a2:

        ya = st.number_input(
            "YA (m)",
            value=20.0,
            step=0.1,
        )

    # --------------------------------------------------------
    # FASE B
    # --------------------------------------------------------

    b1, b2 = st.columns(2)

    with b1:

        xb = st.number_input(
            "XB (m)",
            value=0.0,
            step=0.1,
        )

    with b2:

        yb = st.number_input(
            "YB (m)",
            value=18.0,
            step=0.1,
        )

    # --------------------------------------------------------
    # FASE C
    # --------------------------------------------------------

    c1, c2 = st.columns(2)

    with c1:

        xc = st.number_input(
            "XC (m)",
            value=2.0,
            step=0.1,
        )

    with c2:

        yc = st.number_input(
            "YC (m)",
            value=20.0,
            step=0.1,
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
            list(CABOS_PR.keys()),
        )

        flecha_pr = st.number_input(
            "Flecha do para-raio (m)",
            min_value=0.0,
            value=0.0,
            step=0.1,
        )

        p1, p2 = st.columns(2)

        with p1:

            xp = st.number_input(
                "XP (m)",
                value=0.0,
                step=0.1,
            )

        with p2:

            yp = st.number_input(
                "YP (m)",
                value=23.0,
                step=0.1,
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
    use_container_width=True,
)


# ============================================================
# PROCESSAMENTO
# ============================================================

if calcular:

    try:

        # ----------------------------------------------------
        # DADOS DO CABO FASE
        # ----------------------------------------------------

        cf = CABOS_FASE[
            cabo_fase_nome
        ]

        gmr_base = cf["GMR"]
        r_individual = cf["R"]

        # A resistência e dividida pelo número 
        # de subcondutores em paralelo.

        rf = r_individual / n_sub

        # ----------------------------------------------------
        # GMR EQUIVALENTE
        # ----------------------------------------------------

        if n_sub == 1:

            gmr_f = gmr_base

        else:

            gmr_f = np.sqrt(
                gmr_base * dist_sub
            )

        # ----------------------------------------------------
        # COORDENADAS
        # ----------------------------------------------------

        coords = {
            "A": [
                xa,
                altura_equivalente(
                    ya,
                    flecha_fase,
                    delta_altura,
                ),
            ],
            "B": [
                xb,
                altura_equivalente(
                    yb,
                    flecha_fase,
                    delta_altura,
                ),
            ],
            "C": [
                xc,
                altura_equivalente(
                    yc,
                    flecha_fase,
                    delta_altura,
                ),
            ],
        }

        # ----------------------------------------------------
        # CABO PARA-RAIO
        # ----------------------------------------------------

        if tem_pr:

            cp = CABOS_PR[
                cabo_pr_nome
            ]

            gmr_p = cp["GMR"]
            rp = cp["R"]

            coords["P"] = [
                xp,
                altura_equivalente(
                    yp,
                    flecha_pr,
                    delta_altura,
                ),
            ]

        else:

            gmr_p = None
            rp = None

        # ----------------------------------------------------
        # LISTA DE CONDUTORES
        # ----------------------------------------------------

        condutores = list(
            coords.keys()
        )

        n = len(condutores)

        # ----------------------------------------------------
        # VALIDACAO DAS ALTURAS
        # ----------------------------------------------------

        for nome, ponto in coords.items():

            if ponto[1] <= 0:

                raise ValueError(
                    f"A altura equivalente do condutor "
                    f"{nome} deve ser maior que zero."
                )

        # ----------------------------------------------------
        # VALIDAÇÃO DAS DISTÂNCIAS 
        # ----------------------------------------------------

        for i in range(n):

            for j in range(
                i + 1,
                n,
            ):

                ci = condutores[i]
                cj = condutores[j]

                d_condutores = distancia(
                    coords[ci],
                    coords[cj],
                )

                if d_condutores <= 0:

                    raise ValueError(
                        f"Os condutores {ci} e {cj} "
                        f"ocupam a mesma posicao."
                    )

        # ====================================================
        # MATRIZ DE INDUTÂNCIA 
        # ====================================================

        l_mat = np.zeros(
            (n, n),
            dtype=float,
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

                        gmr = gmr_p

                    else:

                        gmr = gmr_f

                    l_mat[i, j] = (
                        K
                        * np.log(
                            (2 * pi[1]) / gmr
                        )
                    )

                else:

                    d_real = distancia(
                        pi,
                        pj,
                    )

                    d_imagem = distancia_imagem(
                        pi,
                        pj,
                    )

                    l_mat[i, j] = (
                        K
                        * np.log(
                            d_imagem / d_real
                        )
                    )

        # H/m para H/km

        l_mat = l_mat * 1000

        # ====================================================
        # MATRIZ DE REATÂNCIA 
        # ====================================================

        x_mat = (
            2
            * np.pi
            * frequencia
            * l_mat
        )

        # ====================================================
        # MATRIZ DE RESISTÊNCIA 
        # ====================================================

        r_mat = np.zeros_like(
            l_mat
        )

        r_mat[0, 0] = rf
        r_mat[1, 1] = rf
        r_mat[2, 2] = rf

        if tem_pr:

            r_mat[3, 3] = rp

        # ====================================================
        # MATRIZ DE IMPEDÂNCIA 
        # ====================================================

        z_mat = (
            r_mat
            + 1j * x_mat
        )

        # ====================================================
        # REDUÇÃO DE KRON
        # ====================================================

        if tem_pr:

            z_ff = z_mat[
                0:3,
                0:3,
            ]

            z_fp = z_mat[
                0:3,
                3,
            ].reshape(
                3,
                1,
            )

            z_pf = z_mat[
                3,
                0:3,
            ].reshape(
                1,
                3,
            )

            z_pp = z_mat[
                3,
                3,
            ]

            if abs(z_pp) == 0:

                raise ValueError(
                    "A impedância do cabo "
                    "para-raio nao pode ser zero."
                )

            z_red = (
                z_ff
                - (z_fp @ z_pf) / z_pp
            )

        else:

            z_red = z_mat

        # ====================================================
        # IMPEDÂNCIAS POR FASE
        # ====================================================

        za = (
            z_red[0, 0]
            - 0.5
            * (
                z_red[0, 1]
                + z_red[0, 2]
            )
        )

        zb = (
            z_red[1, 1]
            - 0.5
            * (
                z_red[1, 0]
                + z_red[1, 2]
            )
        )

        zc = (
            z_red[2, 2]
            - 0.5
            * (
                z_red[2, 0]
                + z_red[2, 1]
            )
        )

        z_med = (
            za + zb + zc
        ) / 3

        # ====================================================
        # PARÂMETROS ADOTADOS
        # ====================================================

        st.markdown("---")

        st.subheader(
            "📋 PARÂMETROS ADOTADOS"
        )

        if n_sub == 2:

            texto_espacamento = (
                f"{dist_sub:.3f} m"
            )

        else:

            texto_espacamento = "N/A"

        if tem_pr:

            texto_para_raio = (
                cabo_pr_nome
            )

        else:

            texto_para_raio = (
                "Não considerado"
            )

        parametros = {
            "Frequência":
                f"{frequencia:.2f} Hz",

            "Cabo fase":
                cabo_fase_nome,

            "Subcondutores por fase":
                n_sub,

            "Espaçamento do feixe":
                texto_espacamento,

            "R do cabo individual":
                f"{r_individual:.6f} ohm/km",

            "R equivalente da fase":
                f"{rf:.6f} ohm/km",

            "GMR individual":
                f"{gmr_base:.6f} m",

            "GMR equivalente":
                f"{gmr_f:.6f} m",

            "Cabo para-raio":
                texto_para_raio,

            "Ajuste de altura":
                f"{delta_altura:.2f} m",
        }

        df_parametros = pd.DataFrame(
            parametros.items(),
            columns=[
                "Parâmetro",
                "Valor",
            ],
        )

        st.dataframe(
            df_parametros,
            hide_index=True,
            use_container_width=True,
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
                f"{z_med.real:.6f} ohm/km",
            )

        with res2:

            st.metric(
                "X médio",
                f"{z_med.imag:.6f} ohm/km",
            )

        with res3:

            st.metric(
                "Módulo de Z médio",
                f"{abs(z_med):.6f} ohm/km",
            )

        angulo_medio = np.angle(
            z_med,
            deg=True,
        )

        st.info(
            f"Z médio = "
            f"{z_med.real:.6f} "
            f"{z_med.imag:+.6f}j ohm/km"
            f" | Ângulo = "
            f"{angulo_medio:.3f} graus"
        )

        # ====================================================
        # IMPEDÂNCIA POR FASE
        # ====================================================

        st.markdown("---")

        st.subheader(
            "📊 IMPEDÂNCIA CALCULADA POR FASE"
        )

        resultados = [
            {
                "Fase": "A",
                "R (ohm/km)": za.real,
                "X (ohm/km)": za.imag,
                "Módulo Z (ohm/km)": abs(za),
                "Ângulo (graus)": np.angle(
                    za,
                    deg=True,
                ),
            },
            {
                "Fase": "B",
                "R (ohm/km)": zb.real,
                "X (ohm/km)": zb.imag,
                "Módulo Z (ohm/km)": abs(zb),
                "Ângulo (graus)": np.angle(
                    zb,
                    deg=True,
                ),
            },
            {
                "Fase": "C",
                "R (ohm/km)": zc.real,
                "X (ohm/km)": zc.imag,
                "Módulo Z (ohm/km)": abs(zc),
                "Ângulo (graus)": np.angle(
                    zc,
                    deg=True,
                ),
            },
            {
                "Fase": "Média",
                "R (ohm/km)": z_med.real,
                "X (ohm/km)": z_med.imag,
                "Módulo Z (ohm/km)": abs(z_med),
                "Ângulo (graus)": np.angle(
                    z_med,
                    deg=True,
                ),
            },
        ]

        df_resultados = pd.DataFrame(
            resultados
        )

        st.dataframe(
            df_resultados.style.format(
                precision=6
            ),
            hide_index=True,
            use_container_width=True,
        )

        # ====================================================
        # MATRIZES
        # ====================================================

        st.markdown("---")

        st.subheader(
            "🧮 MATRIZES"
        )

        tab_retangular, tab_polar = st.tabs(
            [
                "Retangular (R + jX)",
                "Polar (|Z| ∠ θ)",
            ]
        )

        # ----------------------------------------------------
        # ABA EXTERNA: RETANGULAR
        # ----------------------------------------------------

        with tab_retangular:

            (
                tab_indutancia,
                tab_reatancia,
                tab_resistencia,
                tab_impedancia,
                tab_reduzida,
            ) = st.tabs(
                [
                    "Indutância",
                    "Reatância",
                    "Resistência",
                    "Impedância",
                    "Matriz reduzida",
                ]
            )

            with tab_indutancia:

                st.caption(
                    "Matriz de indutância L em H/km"
                )

                df_l = df_real(
                    l_mat,
                    condutores,
                )

                st.dataframe(
                    df_l.style.format(
                        "{:.9f}"
                    ),
                    use_container_width=True,
                )

            with tab_reatancia:

                st.caption(
                    "Matriz de reatância X em ohm/km"
                )

                df_x = df_real(
                    x_mat,
                    condutores,
                )

                st.dataframe(
                    df_x.style.format(
                        "{:.6f}"
                    ),
                    use_container_width=True,
                )

            with tab_resistencia:

                st.caption(
                    "Matriz de resistência R em ohm/km"
                )

                df_r = df_real(
                    r_mat,
                    condutores,
                )

                st.dataframe(
                    df_r.style.format(
                        "{:.6f}"
                    ),
                    use_container_width=True,
                )

            with tab_impedancia:

                st.caption(
                    "Matriz de impedância "
                    "Z = R + jX em ohm/km"
                )

                df_z = df_complexo(
                    z_mat,
                    condutores,
                )

                st.dataframe(
                    df_z,
                    use_container_width=True,
                )

            with tab_reduzida:

                if tem_pr:

                    st.caption(
                        "Matriz das fases após "
                        "a redução de Kron"
                    )

                else:

                    st.caption(
                        "Sem para-raio, a matriz "
                        "reduzida coincide com a "
                        "matriz das fases"
                    )

                df_z_red = df_complexo(
                    z_red,
                    [
                        "A",
                        "B",
                        "C",
                    ],
                )

                st.dataframe(
                    df_z_red,
                    use_container_width=True,
                )

        # ----------------------------------------------------
        # ABA EXTERNA: POLAR
        # ----------------------------------------------------

        with tab_polar:

            (
                tab_indutancia_p,
                tab_reatancia_p,
                tab_resistencia_p,
                tab_impedancia_p,
                tab_reduzida_p,
            ) = st.tabs(
                [
                    "Indutância",
                    "Reatância",
                    "Resistência",
                    "Impedância",
                    "Matriz reduzida",
                ]
            )

            with tab_indutancia_p:

                st.caption(
                    "Matriz de indutância L em H/km "
                    "no formato polar (|L| ∠ θ)"
                )

                st.dataframe(
                    df_polar(
                        l_mat,
                        condutores,
                    ),
                    use_container_width=True,
                )

            with tab_reatancia_p:

                st.caption(
                    "Matriz de reatância X em ohm/km "
                    "no formato polar (|X| ∠ θ)"
                )

                st.dataframe(
                    df_polar(
                        x_mat,
                        condutores,
                    ),
                    use_container_width=True,
                )

            with tab_resistencia_p:

                st.caption(
                    "Matriz de resistência R em ohm/km "
                    "no formato polar (|R| ∠ θ)"
                )

                st.dataframe(
                    df_polar(
                        r_mat,
                        condutores,
                    ),
                    use_container_width=True,
                )

            with tab_impedancia_p:

                st.caption(
                    "Matriz de impedância "
                    "em ohm/km, formato polar "
                    "(|Z| em ohm/km e ângulo em graus)"
                )

                st.dataframe(
                    df_polar(
                        z_mat,
                        condutores,
                    ),
                    use_container_width=True,
                )

            with tab_reduzida_p:

                if tem_pr:

                    st.caption(
                        "Matriz das fases após "
                        "a redução de Kron, em polar"
                    )

                else:

                    st.caption(
                        "Sem para-raio, a matriz "
                        "reduzida coincide com a "
                        "matriz das fases, em polar"
                    )

                st.dataframe(
                    df_polar(
                        z_red,
                        [
                            "A",
                            "B",
                            "C",
                        ],
                    ),
                    use_container_width=True,
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
            use_container_width=True,
        )

        plt.close(
            figura
        )

        # ====================================================
        # INFORMAÇÕES ADICIONAIS
        # ====================================================

        with st.expander(
            "ℹ️ INFORMAÇÕES ADICIONAIS",
            expanded=False,
        ):

            st.write(
                "A resistencia equivalente da fase "
                "e dividida pelo número de "
                "subcondutores em paralelo."
            )

            st.latex(
                r"R_{eq} = \frac{R}{n}"
            )

            st.write(
                f"R individual = "
                f"{r_individual:.6f} ohm/km"
            )

            st.write(
                f"Número de subcondutores = "
                f"{n_sub}"
            )

            st.write(
                f"R equivalente = "
                f"{rf:.6f} ohm/km"
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
                f"GMR equivalente = "
                f"{gmr_f:.6f} m"
            )

            if tem_pr:

                st.latex(
                    r"Z_{red} = "
                    r"Z_{ff} - "
                    r"Z_{fp}"
                    r"Z_{pp}^{-1}"
                    r"Z_{pf}"
                )

            st.warning(
                "O Z médio apresentado segue a "
                "formulação do código original e "
                "nao deve ser interpretado "
                "automaticamente como impedância "
                "de sequência positiva Z1."
            )

    except Exception as erro:

        st.error(
            f"Erro no calculo: {erro}"
        )

        st.exception(
            erro
        )
