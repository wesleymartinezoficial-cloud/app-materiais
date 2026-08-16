import math
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Controle Tecnológico - Materiais",
    layout="wide",
    page_icon="🏗️",
)

st.title("🏗️ Controle Tecnológico de Materiais (ABNT)")

# Menu Lateral
ensaio = st.sidebar.selectbox(
    "Selecione o Ensaio de Laboratório:",
    ["1. Granulometria (NBR 17054)", "2. Compressão do Concreto (NBR 5739)"],
)

# ------------------------------------------------------------------------------
# ENSAIO 1: GRANULOMETRIA
# ------------------------------------------------------------------------------
if ensaio == "1. Granulometria (NBR 17054)":
    st.header("Análise Granulométrica de Agregados")

    col1, col2 = st.columns(2)
    with col1:
        tipo = st.selectbox(
            "Tipo de Agregado",
            [
                "Areia (Agregado Miúdo)",
                "Brita 0 (Pedrisco)",
                "Brita 1",
                "Brita 2",
                "Brita 3",
            ],
        )
    with col2:
        massa_inicial = st.number_input(
            "Massa Inicial Seca (g)", value=5000.0, step=100.0
        )

    st.subheader("Massas Retidas nas Peneiras (g)")

    peneiras_padrao = [
        37.5,
        31.5,
        19.0,
        12.5,
        9.5,
        6.3,
        4.75,
        2.36,
        1.18,
        0.60,
        0.30,
        0.15,
    ]
    df_base = pd.DataFrame(
        {"Abertura (mm)": peneiras_padrao, "Massa Retida (g)": [0.0] * 12}
    )

    df_editado = st.data_editor(df_base, use_container_width=True)
    massa_fundo = st.number_input("Massa Retida no Fundo (g)", value=0.0)

    if st.button("📊 Calcular e Gerar Curva"):
        dados = df_editado.copy()
        massa_recuperada = dados["Massa Retida (g)"].sum() + massa_fundo
        erro = (abs(massa_inicial - massa_recuperada) / massa_inicial) * 100

        dados["Retida (%)"] = (dados["Massa Retida (g)"] / massa_inicial) * 100
        dados["Acumulada (%)"] = dados["Retida (%)"].cumsum()
        dados["Passante (%)"] = 100.0 - dados["Acumulada (%)"]

        st.markdown("---")
        c1, c2 = st.columns(2)
        c1.metric("Massa Recuperada", f"{massa_recuperada:.1f} g")
        c2.metric(
            "Erro de Perda",
            f"{erro:.2f}%",
            delta="Aprovado" if erro <= 1.0 else "Reprovado (>1%)",
        )

        # Gráfico Logarítmico
        fig, ax = plt.subplots(figsize=(8, 3.5))
        ax.plot(
            dados["Abertura (mm)"],
            dados["Passante (%)"],
            marker="o",
            color="#1f77b4",
            linewidth=2,
        )
        ax.set_xscale("log")
        ax.invert_xaxis()
        ax.set_title(f"Curva Granulométrica - {tipo}")
        ax.set_xlabel("Abertura (mm) - Log")
        ax.set_ylabel("Passante Acumulado (%)")
        ax.grid(True, which="both", linestyle="--", alpha=0.5)

        st.pyplot(fig)
        st.dataframe(dados, use_container_width=True)

# ------------------------------------------------------------------------------
# ENSAIO 2: COMPRESSÃO DO CONCRETO
# ------------------------------------------------------------------------------
else:
    st.header("Ensaio de Resistência à Compressão (CPs Cilíndricos)")

    col1, col2, col3 = st.columns(3)
    with col1:
        d = st.number_input("Diâmetro do CP (cm)", value=10.0)
    with col2:
        carga = st.number_input("Carga Ruptura (kN)", value=250.0)
    with col3:
        idade = st.number_input("Idade (dias)", value=28)

    if st.button("💥 Calcular Resistência (fc)"):
        area = (math.pi * (d**2)) / 4.0
        fc_mpa = ((carga * 1000.0) / area) / 10.0

        st.success("Ensaio Calculado!")
        st.metric(
            label="Resistência à Compressão (fc)", value=f"{fc_mpa:.2f} MPa"
        )
        st.info(f"Área da seção transversal: {area:.2f} cm²")