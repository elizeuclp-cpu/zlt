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


def plotar_geometria(coords, nomes_c1=("A", "B", "C"),
                     nomes_c2=("A2", "B2", "C2"),
                     nomes_pr=("P1", "P2")):

    fig, ax = plt.subplots(figsize=(8, 5))

    cores_fase = {
        "A": "red",
        "B": "blue",
        "C": "black",
        "A2": "red",
        "B2": "blue",
        "C2": "black",
    }

    marcadores = {
        "A": "o", "B": "o", "C": "o",
        "A2": "s", "B2": "s", "C2": "s",
        "P": "^", "P1": "^", "P2": "v",
    }

    for nome, ponto in coords.items():

        x = ponto[0]
        y = ponto[1]

        if nome in cores_fase:
            cor = cores_fase[nome]
        elif nome in ("P", "P1", "P2"):
            cor = "gray"
        else:
            cor = "black"

        marcador = marcadores.get(nome, "o")

        ax.scatter(
            x,
            y,
            s=140,
            color=cor,
            marker=marcador,
            zorder=3,
            edgecolors="black",
            linewidths=0.8,
        )

        ax.annotate(
            nome,
            (x, y),
            xytext=(7, 7),
            textcoords="offset points",
            fontweight="bold",
            fontsize=9,
        )

    ax.axhline(
        y=0,
        color="saddlebrown",
        linewidth=2,
        label="Solo",
    )

    ax.set_xlabel("Coordenada horizontal X (m)")
    ax.set_ylabel("Altura equivalente Y (m)")
    ax.set_title("Geometria equivalente dos condutores")
    ax.grid(True, alpha=0.25)
    ax.legend()

    fig.tight_layout()
    return fig


# ============================================================
# INTERFACE
# ============================================================

col1, col2 = st.columns([1, 1], gap="large")


# ============================================================
# COLUNA 1
# ============================================================

with col1:

    st.subheader("⚙️ 1. CONFIGURAÇÕES GERAIS")

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
    # CABO DAS FASES (C1)
    # --------------------------------------------------------

    st.subheader("🔌 2. CABO DAS FASES (C1)")

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
        "Flecha das fases C1 (m)",
        min_value=0.0,
        value=0.0,
        step=0.1,
    )

    cabo_interface = CABOS_FASE[cabo_fase_nome]
    r_interface = cabo_interface["R"] / n_sub

    if n_sub == 1:
        gmr_interface = cabo_interface["GMR"]
    else:
        gmr_interface = np.sqrt(
            cabo_interface["GMR"] * dist_sub
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
# COLUNA 2 — C1 + C2 + ACOPLAMENTO
# ============================================================

with col2:

    # --------------------------------------------------------
    # COORDENADAS C1
    # --------------------------------------------------------

    st.subheader("📐 3. COORDENADAS DAS FASES (C1)")

    a1, a2 = st.columns(2)
    with a1:
        xa = st.number_input("XA1 (m)", value=0.0, step=0.1)
    with a2:
        ya = st.number_input("YA1 (m)", value=28.0, step=0.1)

    b1, b2 = st.columns(2)
    with b1:
        xb = st.number_input("XB1 (m)", value=0.0, step=0.1)
    with b2:
        yb = st.number_input("YB1 (m)", value=26.0, step=0.1)

    c1, c2 = st.columns(2)
    with c1:
        xc = st.number_input("XC1 (m)", value=0.0, step=0.1)
    with c2:
        yc = st.number_input("YC1 (m)", value=24.0, step=0.1)

    # --------------------------------------------------------
    # PARA-RAIO C1
    # --------------------------------------------------------

    tem_pr = st.checkbox("C1 tem cabo para-raio")

    if tem_pr:
        cabo_pr_nome = st.selectbox(
            "Cabo para-raio C1",
            list(CABOS_PR.keys()),
        )
        flecha_pr = st.number_input(
            "Flecha do para-raio C1 (m)",
            min_value=0.0,
            value=0.0,
            step=0.1,
        )
        p1c, p2c = st.columns(2)
        with p1c:
            xp = st.number_input("XP1 (m)", value=0.0, step=0.1)
        with p2c:
            yp = st.number_input("YP1 (m)", value=30.0, step=0.1)
    else:
        cabo_pr_nome = None
        flecha_pr = 0.0
        xp = 0.0
        yp = 0.0

    st.markdown("---")

    # --------------------------------------------------------
    # CIRCUITO 2
    # --------------------------------------------------------

    st.subheader("🔄 4. SEGUNDO CIRCUITO (C2)")

    tem_c2 = st.checkbox(
        "Considerar influência do segundo circuito (C2)"
    )

    if tem_c2:

        st.caption(
            "Informe a geometria do C2. As posições "
            "são independentes das do C1."
        )

        a2_1, a2_2 = st.columns(2)
        with a2_1:
            xa2 = st.number_input("XA2 (m)", value=4.0, step=0.1)
        with a2_2:
            ya2 = st.number_input("YA2 (m)", value=28.0, step=0.1)

        b2_1, b2_2 = st.columns(2)
        with b2_1:
            xb2 = st.number_input("XB2 (m)", value=4.0, step=0.1)
        with b2_2:
            yb2 = st.number_input("YB2 (m)", value=26.0, step=0.1)

        c2_1, c2_2 = st.columns(2)
        with c2_1:
            xc2 = st.number_input("XC2 (m)", value=4.0, step=0.1)
        with c2_2:
            yc2 = st.number_input("YC2 (m)", value=24.0, step=0.1)

        # ----------------------------------------------------
        # CABO DAS FASES DO C2
        # ----------------------------------------------------

        st.markdown("**Cabo das fases do C2**")

        cabo_fase2_nome = st.selectbox(
            "Cabo fase C2",
            list(CABOS_FASE.keys()),
            key="cabo_fase2",
        )

        n_sub2 = st.selectbox(
            "Subcondutores por fase C2",
            [1, 2],
            format_func=lambda valor: (
                "1 condutor"
                if valor == 1
                else "2 subcondutores"
            ),
            key="n_sub2",
        )

        dist_sub2 = st.number_input(
            "Espacamento do feixe C2 (m)",
            min_value=0.001,
            value=0.305,
            step=0.005,
            disabled=(n_sub2 == 1),
            key="dist_sub2",
        )

        flecha_fase2 = st.number_input(
            "Flecha das fases C2 (m)",
            min_value=0.0,
            value=0.0,
            step=0.1,
            key="flecha_fase2",
        )

        # ----------------------------------------------------
        # PARA-RAIO C2
        # ----------------------------------------------------

        tem_pr2 = st.checkbox(
            "C2 tem cabo para-raio",
            key="tem_pr2",
        )

        if tem_pr2:
            cabo_pr2_nome = st.selectbox(
                "Cabo para-raio C2",
                list(CABOS_PR.keys()),
                key="cabo_pr2",
            )
            flecha_pr2 = st.number_input(
                "Flecha do para-raio C2 (m)",
                min_value=0.0,
                value=0.0,
                step=0.1,
                key="flecha_pr2",
            )
            pp1, pp2 = st.columns(2)
            with pp1:
                xp2 = st.number_input("XP2 (m)", value=4.0, step=0.1, key="xp2")
            with pp2:
                yp2 = st.number_input("YP2 (m)", value=30.0, step=0.1, key="yp2")
        else:
            cabo_pr2_nome = None
            flecha_pr2 = 0.0
            xp2 = 0.0
            yp2 = 0.0

        # ----------------------------------------------------
        # RAZÃO k = I2/I1
        # ----------------------------------------------------

        st.markdown("---")
        st.subheader("🔗 5. ACOPLAMENTO ENTRE CIRCUITOS")

        k_relacao = st.number_input(
            "Relação k = I2 / I1",
            min_value=0.0,
            max_value=100.0,
            value=1.0,
            step=0.1,
            help=(
                "k = 0 → C2 em vazio (mas fisicamente presente). "
                "k > 0 → corrente do C2 em fase com o C1."
            ),
        )

    else:
        xa2 = ya2 = xb2 = yb2 = xc2 = yc2 = 0.0
        cabo_fase2_nome = None
        n_sub2 = 1
        dist_sub2 = 0.305
        flecha_fase2 = 0.0
        tem_pr2 = False
        cabo_pr2_nome = None
        flecha_pr2 = 0.0
        xp2 = yp2 = 0.0
        k_relacao = 0.0


# ============================================================
# VALIDAÇÃO ANTECIPADA DE Y
# ============================================================

erros_validacao = []

if ya <= 0:
    erros_validacao.append(f"YA1 = {ya} m (deve ser > 0)")
if yb <= 0:
    erros_validacao.append(f"YB1 = {yb} m (deve ser > 0)")
if yc <= 0:
    erros_validacao.append(f"YC1 = {yc} m (deve ser > 0)")
if tem_pr and yp <= 0:
    erros_validacao.append(f"YP1 = {yp} m (deve ser > 0)")

if tem_c2:
    if ya2 <= 0:
        erros_validacao.append(f"YA2 = {ya2} m (deve ser > 0)")
    if yb2 <= 0:
        erros_validacao.append(f"YB2 = {yb2} m (deve ser > 0)")
    if yc2 <= 0:
        erros_validacao.append(f"YC2 = {yc2} m (deve ser > 0)")
    if tem_pr2 and yp2 <= 0:
        erros_validacao.append(f"YP2 = {yp2} m (deve ser > 0)")


def checar_equivalente(nome, y_digitado, flecha):
    y_eq = altura_equivalente(y_digitado, flecha, delta_altura)
    if y_eq <= 0:
        erros_validacao.append(
            f"Altura equivalente de {nome} = {y_eq:.2f} m "
            f"(flecha = {flecha} m e ΔH = {delta_altura} m). "
            f"Reduza a flecha ou o ΔH."
        )


if ya > 0:
    checar_equivalente("A1", ya, flecha_fase)
if yb > 0:
    checar_equivalente("B1", yb, flecha_fase)
if yc > 0:
    checar_equivalente("C1", yc, flecha_fase)
if tem_pr and yp > 0:
    checar_equivalente("P1", yp, flecha_pr)

if tem_c2:
    if ya2 > 0:
        checar_equivalente("A2", ya2, flecha_fase2)
    if yb2 > 0:
        checar_equivalente("B2", yb2, flecha_fase2)
    if yc2 > 0:
        checar_equivalente("C2", yc2, flecha_fase2)
    if tem_pr2 and yp2 > 0:
        checar_equivalente("P2", yp2, flecha_pr2)

if erros_validacao:
    st.error(
        "❌ Corrija os seguintes pontos antes de continuar:\n\n- "
        + "\n- ".join(erros_validacao)
    )


# ============================================================
# SESSION STATE — FLAG DE GEOMETRIA TESTADA
# ============================================================

if "geometria_testada" not in st.session_state:
    st.session_state["geometria_testada"] = False

_hash_atual = hash((
    xa, ya, xb, yb, xc, yc,
    xp, yp, flecha_pr if tem_pr else 0,
    xa2 if tem_c2 else 0, ya2 if tem_c2 else 0,
    xb2 if tem_c2 else 0, yb2 if tem_c2 else 0,
    xc2 if tem_c2 else 0, yc2 if tem_c2 else 0,
    xp2 if (tem_c2 and tem_pr2) else 0,
    yp2 if (tem_c2 and tem_pr2) else 0,
    flecha_fase, delta_altura,
    flecha_fase2 if tem_c2 else 0,
    flecha_pr2 if (tem_c2 and tem_pr2) else 0,
    tem_pr, tem_c2, tem_pr2,
))

if st.session_state.get("hash_geo") != _hash_atual:
    st.session_state["geometria_testada"] = False
    st.session_state["hash_geo"] = _hash_atual


# ============================================================
# BOTÕES: TESTAR GEOMETRIA  +  CALCULAR
# ============================================================

st.markdown("---")

col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    testar_geometria = st.button(
        "🧭 Testar geometria",
        use_container_width=True,
        disabled=bool(erros_validacao),
    )

if testar_geometria and not erros_validacao:
    st.session_state["geometria_testada"] = True

if erros_validacao:
    st.session_state["geometria_testada"] = False

with col_btn2:
    calcular = st.button(
        "🔍 Calcular parâmetros elétricos",
        type="primary",
        use_container_width=True,
        disabled=(
            bool(erros_validacao)
            or not st.session_state["geometria_testada"]
        ),
        help=(
            "Teste a geometria primeiro para liberar o cálculo."
            if not st.session_state["geometria_testada"]
            else None
        ),
    )


# ============================================================
# BOTÃO "TESTAR GEOMETRIA" — desenha antes do cálculo
# ============================================================

if st.session_state["geometria_testada"] and not erros_validacao:

    coords_geo = {
        "A": [xa, altura_equivalente(ya, flecha_fase, delta_altura)],
        "B": [xb, altura_equivalente(yb, flecha_fase, delta_altura)],
        "C": [xc, altura_equivalente(yc, flecha_fase, delta_altura)],
    }

    if tem_pr:
        coords_geo["P1"] = [xp, altura_equivalente(yp, flecha_pr, delta_altura)]

    if tem_c2:
        coords_geo["A2"] = [xa2, altura_equivalente(ya2, flecha_fase2, delta_altura)]
        coords_geo["B2"] = [xb2, altura_equivalente(yb2, flecha_fase2, delta_altura)]
        coords_geo["C2"] = [xc2, altura_equivalente(yc2, flecha_fase2, delta_altura)]

        if tem_pr2:
            coords_geo["P2"] = [xp2, altura_equivalente(yp2, flecha_pr2, delta_altura)]

    st.subheader("🧭 PRÉ-VISUALIZAÇÃO DA GEOMETRIA")

    fig_geo = plotar_geometria(coords_geo)
    st.pyplot(fig_geo, use_container_width=True)
    plt.close(fig_geo)

    st.info(
        "Se a geometria estiver correta, clique em "
        "**🔍 Calcular parâmetros elétricos** para prosseguir."
    )


# ============================================================
# PROCESSAMENTO PRINCIPAL
# ============================================================

if calcular and not erros_validacao:

    try:

        cf = CABOS_FASE[cabo_fase_nome]
        gmr_base = cf["GMR"]
        r_individual = cf["R"]
        rf = r_individual / n_sub

        if n_sub == 1:
            gmr_f = gmr_base
        else:
            gmr_f = np.sqrt(gmr_base * dist_sub)

        coords = {
            "A1": [xa, altura_equivalente(ya, flecha_fase, delta_altura)],
            "B1": [xb, altura_equivalente(yb, flecha_fase, delta_altura)],
            "C1": [xc, altura_equivalente(yc, flecha_fase, delta_altura)],
        }

        if tem_pr:
            cp = CABOS_PR[cabo_pr_nome]
            gmr_p = cp["GMR"]
            rp = cp["R"]
            coords["P1"] = [xp, altura_equivalente(yp, flecha_pr, delta_altura)]
        else:
            gmr_p = None
            rp = None

        gmr_f2 = None
        rf2 = None
        gmr_p2 = None
        rp2 = None

        if tem_c2:
            cf2 = CABOS_FASE[cabo_fase2_nome]
            gmr_base2 = cf2["GMR"]
            r_individual2 = cf2["R"]
            rf2 = r_individual2 / n_sub2

            if n_sub2 == 1:
                gmr_f2 = gmr_base2
            else:
                gmr_f2 = np.sqrt(gmr_base2 * dist_sub2)

            coords["A2"] = [xa2, altura_equivalente(ya2, flecha_fase2, delta_altura)]
            coords["B2"] = [xb2, altura_equivalente(yb2, flecha_fase2, delta_altura)]
            coords["C2"] = [xc2, altura_equivalente(yc2, flecha_fase2, delta_altura)]

            if tem_pr2:
                cp2 = CABOS_PR[cabo_pr2_nome]
                gmr_p2 = cp2["GMR"]
                rp2 = cp2["R"]
                coords["P2"] = [xp2, altura_equivalente(yp2, flecha_pr2, delta_altura)]

        condutores = ["A1", "B1", "C1"]
        if tem_c2:
            condutores += ["A2", "B2", "C2"]
        if tem_pr:
            condutores += ["P1"]
        if tem_c2 and tem_pr2:
            condutores += ["P2"]

        n = len(condutores)
        idx = {nome: i for i, nome in enumerate(condutores)}

        for i in range(n):
            for j in range(i + 1, n):
                ci = condutores[i]
                cj = condutores[j]
                d = distancia(coords[ci], coords[cj])
                if d <= 0:
                    raise ValueError(
                        f"Os condutores {ci} e {cj} ocupam a mesma posição."
                    )

        l_mat = np.zeros((n, n), dtype=float)

        gmr_map = {}
        for nome in ["A1", "B1", "C1"]:
            gmr_map[nome] = gmr_f
        if tem_c2:
            for nome in ["A2", "B2", "C2"]:
                gmr_map[nome] = gmr_f2
        if tem_pr:
            gmr_map["P1"] = gmr_p
        if tem_c2 and tem_pr2:
            gmr_map["P2"] = gmr_p2

        for i, ci in enumerate(condutores):
            for j, cj in enumerate(condutores):
                pi = coords[ci]
                pj = coords[cj]

                if i == j:
                    gmr = gmr_map[ci]
                    l_mat[i, j] = K * np.log((2 * pi[1]) / gmr)
                else:
                    d_real = distancia(pi, pj)
                    d_img = distancia_imagem(pi, pj)
                    l_mat[i, j] = K * np.log(d_img / d_real)

        l_mat = l_mat * 1000

        x_mat = 2 * np.pi * frequencia * l_mat

        r_mat = np.zeros_like(l_mat)
        for nome in ["A1", "B1", "C1"]:
            r_mat[idx[nome], idx[nome]] = rf
        if tem_c2:
            for nome in ["A2", "B2", "C2"]:
                r_mat[idx[nome], idx[nome]] = rf2
        if tem_pr:
            r_mat[idx["P1"], idx["P1"]] = rp
        if tem_c2 and tem_pr2:
            r_mat[idx["P2"], idx["P2"]] = rp2

        z_mat = r_mat + 1j * x_mat

        idx_pr = []
        if tem_pr:
            idx_pr.append(idx["P1"])
        if tem_c2 and tem_pr2:
            idx_pr.append(idx["P2"])

        idx_fases = [i for i in range(n) if i not in idx_pr]

        if len(idx_pr) > 0:
            z_ff = z_mat[np.ix_(idx_fases, idx_fases)]
            z_fp = z_mat[np.ix_(idx_fases, idx_pr)]
            z_pf = z_mat[np.ix_(idx_pr, idx_fases)]
            z_pp = z_mat[np.ix_(idx_pr, idx_pr)]

            z_red = z_ff - z_fp @ np.linalg.inv(z_pp) @ z_pf
        else:
            z_red = z_mat[np.ix_(idx_fases, idx_fases)].copy()

        # C1 isolado
        if tem_pr:
            cond_c1_iso = ["A1", "B1", "C1", "P1"]
            n_iso = len(cond_c1_iso)

            l_iso = np.zeros((n_iso, n_iso), dtype=float)
            gmr_iso = {"A1": gmr_f, "B1": gmr_f, "C1": gmr_f, "P1": gmr_p}

            for i, ci in enumerate(cond_c1_iso):
                for j, cj in enumerate(cond_c1_iso):
                    pi = coords[ci]
                    pj = coords[cj]
                    if i == j:
                        l_iso[i, j] = K * np.log((2 * pi[1]) / gmr_iso[ci])
                    else:
                        l_iso[i, j] = K * np.log(
                            distancia_imagem(pi, pj) / distancia(pi, pj)
                        )
            l_iso *= 1000
            x_iso = 2 * np.pi * frequencia * l_iso
            r_iso = np.zeros_like(l_iso)
            r_iso[0, 0] = rf
            r_iso[1, 1] = rf
            r_iso[2, 2] = rf
            r_iso[3, 3] = rp
            z_iso = r_iso + 1j * x_iso
            z_c1_iso = (
                z_iso[0:3, 0:3]
                - (z_iso[0:3, 3:4] @ z_iso[3:4, 0:3]) / z_iso[3, 3]
            )
        else:
            cond_c1_iso = ["A1", "B1", "C1"]
            l_iso = np.zeros((3, 3), dtype=float)
            gmr_iso = {"A1": gmr_f, "B1": gmr_f, "C1": gmr_f}

            for i, ci in enumerate(cond_c1_iso):
                for j, cj in enumerate(cond_c1_iso):
                    pi = coords[ci]
                    pj = coords[cj]
                    if i == j:
                        l_iso[i, j] = K * np.log((2 * pi[1]) / gmr_iso[ci])
                    else:
                        l_iso[i, j] = K * np.log(
                            distancia_imagem(pi, pj) / distancia(pi, pj)
                        )
            l_iso *= 1000
            x_iso = 2 * np.pi * frequencia * l_iso
            r_iso = np.zeros((3, 3), dtype=float)
            r_iso[0, 0] = rf
            r_iso[1, 1] = rf
            r_iso[2, 2] = rf
            z_c1_iso = r_iso + 1j * x_iso

        if tem_c2:
            z_f1f1 = z_red[0:3, 0:3]
            z_f1f2 = z_red[0:3, 3:6]
            z_f2f2 = z_red[3:6, 3:6]
            z_vista_1 = z_f1f1 + k_relacao * z_f1f2
        else:
            z_f1f1 = z_red[0:3, 0:3]
            z_f1f2 = None
            z_f2f2 = None
            z_vista_1 = z_f1f1

        def impedancias_por_fase(z3):
            za_ = z3[0, 0] - 0.5 * (z3[0, 1] + z3[0, 2])
            zb_ = z3[1, 1] - 0.5 * (z3[1, 0] + z3[1, 2])
            zc_ = z3[2, 2] - 0.5 * (z3[2, 0] + z3[2, 1])
            zmed_ = (za_ + zb_ + zc_) / 3
            return za_, zb_, zc_, zmed_

        za_iso, zb_iso, zc_iso, zmed_iso = impedancias_por_fase(z_c1_iso)
        za_v, zb_v, zc_v, zmed_v = impedancias_por_fase(z_vista_1)

        st.markdown("---")
        st.subheader("📋 PARÂMETROS ADOTADOS")

        texto_espacamento = f"{dist_sub:.3f} m" if n_sub == 2 else "N/A"
        texto_pr = cabo_pr_nome if tem_pr else "Não considerado"

        parametros = {
            "Frequência": f"{frequencia:.2f} Hz",
            "Cabo fase C1": cabo_fase_nome,
            "Subcondutores por fase C1": n_sub,
            "Espaçamento do feixe C1": texto_espacamento,
            "R do cabo individual C1": f"{r_individual:.6f} ohm/km",
            "R equivalente da fase C1": f"{rf:.6f} ohm/km",
            "GMR individual C1": f"{gmr_base:.6f} m",
            "GMR equivalente C1": f"{gmr_f:.6f} m",
            "Cabo para-raio C1": texto_pr,
            "Ajuste de altura ΔH": f"{delta_altura:.2f} m",
        }

        if tem_c2:
            texto_pr2 = cabo_pr2_nome if tem_pr2 else "Não considerado"
            parametros["C2 considerado"] = "Sim"
            parametros["Cabo fase C2"] = cabo_fase2_nome
            parametros["Subcondutores por fase C2"] = n_sub2
            parametros["GMR equivalente C2"] = f"{gmr_f2:.6f} m"
            parametros["Cabo para-raio C2"] = texto_pr2
            parametros["Razão k = I2/I1"] = f"{k_relacao:.3f}"

        df_parametros = pd.DataFrame(
            parametros.items(),
            columns=["Parâmetro", "Valor"],
        )

        st.dataframe(df_parametros, hide_index=True, use_container_width=True)

        st.markdown("---")
        st.subheader("🎯 RESULTADO PRINCIPAL")

        if tem_c2:

            col_a, col_b = st.columns(2)

            with col_a:
                st.markdown("**C1 sem influência do C2**")
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.metric("R médio", f"{zmed_iso.real:.6f} Ω/km")
                with m2:
                    st.metric("X médio", f"{zmed_iso.imag:.6f} Ω/km")
                with m3:
                    st.metric("|Z| médio", f"{abs(zmed_iso):.6f} Ω/km")

            with col_b:
                st.markdown(f"**C1 influenciado pelo C2 (k = {k_relacao:.2f})**")
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.metric("R médio", f"{zmed_v.real:.6f} Ω/km")
                with m2:
                    st.metric("X médio", f"{zmed_v.imag:.6f} Ω/km")
                with m3:
                    st.metric("|Z| médio", f"{abs(zmed_v):.6f} Ω/km")

            st.info(
                f"**C1 isolado:** Z = {zmed_iso.real:.6f} "
                f"{zmed_iso.imag:+.6f}j Ω/km "
                f"(ângulo {np.angle(zmed_iso, deg=True):.2f}°)\n\n"
                f"**C1 com C2:** Z = {zmed_v.real:.6f} "
                f"{zmed_v.imag:+.6f}j Ω/km "
                f"(ângulo {np.angle(zmed_v, deg=True):.2f}°)"
            )

        else:

            res1, res2, res3 = st.columns(3)
            with res1:
                st.metric("R médio", f"{zmed_v.real:.6f} Ω/km")
            with res2:
                st.metric("X médio", f"{zmed_v.imag:.6f} Ω/km")
            with res3:
                st.metric("|Z| médio", f"{abs(zmed_v):.6f} Ω/km")

            st.info(
                f"Z médio = {zmed_v.real:.6f} "
                f"{zmed_v.imag:+.6f}j Ω/km | "
                f"Ângulo = {np.angle(zmed_v, deg=True):.3f}°"
            )

        st.markdown("---")
        st.subheader("📊 IMPEDÂNCIA CALCULADA POR FASE")

        def montar_tabela_fases(za_, zb_, zc_, zmed_, rotulo):
            return pd.DataFrame([
                {"Seção": rotulo, "Fase": "A1",
                 "R (Ω/km)": za_.real, "X (Ω/km)": za_.imag,
                 "|Z| (Ω/km)": abs(za_), "Ângulo (°)": np.angle(za_, deg=True)},
                {"Seção": rotulo, "Fase": "B1",
                 "R (Ω/km)": zb_.real, "X (Ω/km)": zb_.imag,
                 "|Z| (Ω/km)": abs(zb_), "Ângulo (°)": np.angle(zb_, deg=True)},
                {"Seção": rotulo, "Fase": "C1",
                 "R (Ω/km)": zc_.real, "X (Ω/km)": zc_.imag,
                 "|Z| (Ω/km)": abs(zc_), "Ângulo (°)": np.angle(zc_, deg=True)},
                {"Seção": rotulo, "Fase": "Média",
                 "R (Ω/km)": zmed_.real, "X (Ω/km)": zmed_.imag,
                 "|Z| (Ω/km)": abs(zmed_), "Ângulo (°)": np.angle(zmed_, deg=True)},
            ])

        if tem_c2:
            df_iso = montar_tabela_fases(
                za_iso, zb_iso, zc_iso, zmed_iso, "C1 isolado"
            )
            df_v = montar_tabela_fases(
                za_v, zb_v, zc_v, zmed_v, "C1 com C2"
            )
            df_todas = pd.concat([df_iso, df_v], ignore_index=True)
            st.dataframe(
                df_todas.style.format(precision=6),
                hide_index=True,
                use_container_width=True,
            )
        else:
            df_todas = montar_tabela_fases(
                za_v, zb_v, zc_v, zmed_v, "C1 isolado"
            )
            st.dataframe(
                df_todas.style.format(precision=6),
                hide_index=True,
                use_container_width=True,
            )

        st.markdown("---")
        st.subheader("🧮 MATRIZES")

        (
            tab_indutancia,
            tab_reatancia,
            tab_resistencia,
            tab_impedancia,
            tab_reduzida,
        ) = st.tabs([
            "Indutância",
            "Reatância",
            "Resistência",
            "Impedância",
            "Matriz reduzida (Z vista 1)",
        ])

        with tab_indutancia:
            st.caption(
                f"Matriz de indutância L em H/km "
                f"({n}×{n}, todos os condutores)"
            )
            st.dataframe(
                df_real(l_mat, condutores).style.format("{:.9f}"),
                use_container_width=True,
            )

        with tab_reatancia:
            st.caption(
                f"Matriz de reatância X em Ω/km "
                f"({n}×{n}, todos os condutores)"
            )
            st.dataframe(
                df_real(x_mat, condutores).style.format("{:.6f}"),
                use_container_width=True,
            )

        with tab_resistencia:
            st.caption(
                f"Matriz de resistência R em Ω/km "
                f"({n}×{n}, todos os condutores)"
            )
            st.dataframe(
                df_real(r_mat, condutores).style.format("{:.6f}"),
                use_container_width=True,
            )

        with tab_impedancia:
            st.caption(
                f"Matriz de impedância Z = R + jX em Ω/km "
                f"({n}×{n}, todos os condutores)"
            )
            st.dataframe(
                df_complexo(z_mat, condutores),
                use_container_width=True,
            )

        with tab_reduzida:
            if tem_c2:
                st.caption(
                    f"Z vista 1(k) = Z'f1f1 + k·Z'f1f2 "
                    f"com k = {k_relacao:.3f} (Ω/km)"
                )
            else:
                st.caption(
                    "Impedância do C1 após eliminação de para-raios "
                    "(Ω/km)"
                )
            st.dataframe(
                df_complexo(z_vista_1, ["A1", "B1", "C1"]),
                use_container_width=True,
            )

        st.markdown("---")
        st.subheader("📈 GEOMETRIA DA LINHA")

        figura = plotar_geometria(coords)
        st.pyplot(figura, use_container_width=True)
        plt.close(figura)

        with st.expander("ℹ️ INFORMAÇÕES ADICIONAIS", expanded=False):

            st.write(
                "A resistência equivalente da fase é dividida pelo "
                "número de subcondutores em paralelo."
            )
            st.latex(r"R_{eq} = \frac{R}{n}")
            st.write(f"R individual C1 = {r_individual:.6f} Ω/km")
            st.write(f"Número de subcondutores C1 = {n_sub}")
            st.write(f"R equivalente C1 = {rf:.6f} Ω/km")

            if n_sub == 1:
                st.latex(r"GMR_{eq} = GMR")
            else:
                st.latex(r"GMR_{eq} = \sqrt{GMR \cdot d}")

            st.write(f"GMR equivalente C1 = {gmr_f:.6f} m")

            if len(idx_pr) > 0:
                st.latex(
                    r"Z_{red} = Z_{ff} - Z_{fp}\, Z_{pp}^{-1}\, Z_{pf}"
                )

            if tem_c2:
                st.markdown("---")
                st.markdown("**Acoplamento C1 ↔ C2**")
                st.latex(
                    r"Z_{vista,1}(k) = Z'_{f1f1} + k \cdot Z'_{f1f2}"
                )
                st.write(
                    "Z'f1f1 é o bloco 3×3 do C1 após eliminação "
                    "dos para-raios. Z'f1f2 é o bloco 3×3 de "
                    "acoplamento C1↔C2 após a mesma eliminação."
                )
                st.warning(
                    "Mesmo com k = 0, o resultado NÃO é necessariamente "
                    "igual ao C1 isolado quando o C2 tem para-raio: "
                    "o P2 aterrado afeta o C1 via acoplamento, mesmo "
                    "sem corrente no C2."
                )

            st.warning(
                "O Z médio apresentado segue a formulação original "
                "e não deve ser interpretado automaticamente como "
                "impedância de sequência positiva Z1."
            )

        if tem_c2:
            with st.expander("🔍 DETALHES DO ACOPLAMENTO C1 ↔ C2", expanded=False):

                st.markdown("**Z'f1f1 — bloco do C1 após Kron (Ω/km)**")
                st.dataframe(
                    df_complexo(z_f1f1, ["A1", "B1", "C1"]),
                    use_container_width=True,
                )

                st.markdown("**Z'f1f2 — acoplamento C1↔C2 após Kron (Ω/km)**")
                st.dataframe(
                    df_complexo(z_f1f2, ["A1", "B1", "C1"]).rename(
                        columns={0: "A2", 1: "B2", 2: "C2"}
                    ),
                    use_container_width=True,
                )

                st.markdown(
                    f"**k · Z'f1f2 — contribuição do C2 "
                    f"(k = {k_relacao:.3f}) (Ω/km)**"
                )
                st.dataframe(
                    df_complexo(k_relacao * z_f1f2, ["A1", "B1", "C1"]).rename(
                        columns={0: "A2", 1: "B2", 2: "C2"}
                    ),
                    use_container_width=True,
                )

                st.markdown("**Verificação:**")
                st.latex(
                    r"Z_{vista,1}(k) = Z'_{f1f1} + k \cdot Z'_{f1f2}"
                )

    except Exception as erro:
        st.error(f"Erro no cálculo: {erro}")
        st.exception(erro)
