import math
import io
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Controle Tecnológico de Materiais",
    layout="wide",
    page_icon="🏗️",
)

st.title("🏗️ Controle Tecnológico de Materiais (ABNT / NBR)")

# Menu Lateral
ensaio = st.sidebar.selectbox(
    "Selecione o Ensaio de Laboratório:",
    [
        "1. Granulometria de Agregados (NBR 17054)",
        "2. Massa Específica e Absorção - Agregado Miúdo (NBR 16916)",
        "3. Massa Específica e Absorção - Agregado Graúdo (NBR 16917)",
        "4. Massa Unitária e Volume de Vazios (NBR 16972)",
        "5. Resistência à Compressão do Concreto em Lote (NBR 5739)",
    ],
)

# ------------------------------------------------------------------------------
# 1. GRANULOMETRIA (NBR 17054)
# ------------------------------------------------------------------------------
if ensaio == "1. Granulometria de Agregados (NBR 17054)":
    st.header("Análise Granulométrica de Agregados")

    LIMITES_MASSA = {
        "Areia (Agregado Miúdo)": {"massa_min": 300.0, "aplicacao": "Preenchimento de vazios e argamassas."},
        "Brita 0 (Pedrisco)": {"massa_min": 1000.0, "aplicacao": "Lajes treliçadas e pré-fabricados."},
        "Brita 1": {"massa_min": 5000.0, "aplicacao": "Estruturas de concreto armado geral."},
        "Brita 2": {"massa_min": 10000.0, "aplicacao": "Pisos industriais e fundações."},
        "Brita 3": {"massa_min": 15000.0, "aplicacao": "Concreto massa e obras de drenagem."},
    }

    col1, col2 = st.columns(2)
    with col1:
        tipo = st.selectbox("Tipo de Agregado", list(LIMITES_MASSA.keys()))
    with col2:
        m_min = LIMITES_MASSA[tipo]["massa_min"]
        massa_inicial = st.number_input("Massa Inicial Seca M_T (g)", value=m_min, step=100.0)

    st.info(f"📌 **Massa Mínima Recomendada:** {m_min}g | **Aplicação:** {LIMITES_MASSA[tipo]['aplicacao']}")

    PENEIRAS = [
        {"abertura": 37.5, "astm": '1 1/2"', "serie_normal": True},
        {"abertura": 31.5, "astm": '1 1/4"', "serie_normal": False},
        {"abertura": 19.0, "astm": '3/4"', "serie_normal": True},
        {"abertura": 12.5, "astm": '1/2"', "serie_normal": False},
        {"abertura": 9.5, "astm": '3/8"', "serie_normal": True},
        {"abertura": 6.3, "astm": '1/4"', "serie_normal": False},
        {"abertura": 4.75, "astm": "Nº 4", "serie_normal": True},
        {"abertura": 2.36, "astm": "Nº 8", "serie_normal": True},
        {"abertura": 1.18, "astm": "Nº 16", "serie_normal": False},
        {"abertura": 0.60, "astm": "Nº 30", "serie_normal": True},
        {"abertura": 0.30, "astm": "Nº 50", "serie_normal": True},
        {"abertura": 0.15, "astm": "Nº 100", "serie_normal": True},
    ]

    df_base = pd.DataFrame({
        "Abertura (mm)": [p["abertura"] for p in PENEIRAS],
        "ASTM": [p["astm"] for p in PENEIRAS],
        "Série": ["Normal" if p["serie_normal"] else "Intermediária" for p in PENEIRAS],
        "Massa Retida (g)": [0.0] * len(PENEIRAS),
    })

    df_editado = st.data_editor(df_base, use_container_width=True)
    massa_fundo = st.number_input("Fundo Receptor (g)", value=0.0)

    if st.button("📊 Calcular Granulometria"):
        if massa_inicial <= 0:
            st.error("A massa inicial deve ser maior que zero.")
        else:
            massa_rec = df_editado["Massa Retida (g)"].sum() + massa_fundo
            erro = (abs(massa_inicial - massa_rec) / massa_inicial) * 100

            acumulado, soma_pa_norm, dmc = 0.0, 0.0, None
            retida_simples, retida_acumulada, passante = [], [], []

            for idx, row in df_editado.iterrows():
                pr = (row["Massa Retida (g)"] / massa_inicial) * 100
                acumulado += pr
                pp = 100.0 - acumulado

                retida_simples.append(round(pr, 2))
                retida_acumulada.append(round(acumulado, 2))
                passante.append(round(pp, 2))

                if row["Série"] == "Normal":
                    soma_pa_norm += acumulado
                if acumulado <= 5.0:
                    dmc = row["Abertura (mm)"]

            mf = soma_pa_norm / 100.0
            df_res = df_editado.copy()
            df_res["Retida Simples (%)"] = retida_simples
            df_res["Retida Acum. (%)"] = retida_acumulada
            df_res["Passante (%)"] = passante

            st.markdown("---")
            c1, c2, c3 = st.columns(3)
            c1.metric("Massa Recuperada", f"{massa_rec:.1f} g")
            c2.metric("Erro de Perda", f"{erro:.2f}%", delta="✓ Aprovado" if erro <= 1.0 else "❌ Reprovado (>1%)", delta_color="normal" if erro <= 1.0 else "inverse")
            c3.metric("Módulo de Finura (MF)", f"{mf:.2f}", f"DMC: {dmc if dmc else 'N/I'} mm")

            if erro > 1.0:
                st.error("⚠️ Ensaio Reprovado: O erro de perda acumulada superou 1.0% do valor inicial conforme a NBR 17054.")

            fig, ax = plt.subplots(figsize=(8, 3.5))
            ax.plot(df_res["Abertura (mm)"], df_res["Passante (%)"], marker="o", color="#1f77b4", linewidth=2)
            ax.set_xscale("log")
            ax.invert_xaxis()
            ax.set_title(f"Curva Granulométrica - {tipo}")
            ax.set_xlabel("Abertura das Peneiras (mm) - Escala Logarítmica")
            ax.set_ylabel("Passante Acumulado (%)")
            ax.grid(True, which="both", linestyle="--", alpha=0.5)

            st.pyplot(fig)
            st.dataframe(df_res, use_container_width=True)

            # Exportação Excel
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_res.to_excel(writer, index=False, sheet_name='Granulometria')
            st.download_button("📥 Baixar Relatório em Excel", data=buffer.getvalue(), file_name="relatorio_granulometria.xlsx", mime="application/vnd.ms-excel")

# ------------------------------------------------------------------------------
# 2. MASSA ESPECÍFICA - AGREGADO MIÚDO (NBR 16916)
# ------------------------------------------------------------------------------
elif ensaio == "2. Massa Específica e Absorção - Agregado Miúdo (NBR 16916)":
    st.header("Massa Específica e Absorção - Agregado Miúdo (Areia)")

    c1, c2 = st.columns(2)
    with c1:
        m_seco = st.number_input("Massa seca em estufa (g)", value=490.0)
        m_sss = st.number_input("Massa SSS (g)", value=500.0)
    with c2:
        m_pic_agua = st.number_input("Massa picnômetro + água (g)", value=1300.0)
        m_pic_amostra_agua = st.number_input("Massa picnômetro + amostra SSS + água (g)", value=1610.0)

    if st.button("🧪 Calcular Agregado Miúdo"):
        den = m_pic_agua + m_sss - m_pic_amostra_agua
        if den <= 0 or m_seco <= 0:
            st.error("Erro nos dados digitados. Verifique as massas informadas.")
        else:
            gamma_seca = m_seco / den
            gamma_sss = m_sss / den
            absorcao = ((m_sss - m_seco) / m_seco) * 100

            st.success("Resultados do Ensaio:")
            res1, res2, res3 = st.columns(3)
            res1.metric("Massa Específica Seca", f"{gamma_seca:.3f} g/cm³")
            res2.metric("Massa Específica SSS", f"{gamma_sss:.3f} g/cm³")
            res3.metric("Absorção de Água", f"{absorcao:.2f}%")

# ------------------------------------------------------------------------------
# 3. MASSA ESPECÍFICA - AGREGADO GRAÚDO (NBR 16917)
# ------------------------------------------------------------------------------
elif ensaio == "3. Massa Específica e Absorção - Agregado Graúdo (NBR 16917)":
    st.header("Massa Específica e Absorção - Agregado Graúdo (Brita)")

    c1, c2, c3 = st.columns(3)
    with c1:
        m_seco = st.number_input("Massa seca em estufa (g)", value=3000.0)
    with c2:
        m_sss = st.number_input("Massa SSS no ar (g)", value=3040.0)
    with c3:
        m_submersa = st.number_input("Massa aparente submersa (g)", value=1900.0)

    if st.button("🧪 Calcular Agregado Graúdo"):
        den = m_sss - m_submersa
        if den <= 0 or m_seco <= 0:
            st.error("A massa submersa deve ser menor que a massa SSS.")
        else:
            gamma_seca = m_seco / den
            gamma_sss = m_sss / den
            absorcao = ((m_sss - m_seco) / m_seco) * 100

            st.success("Resultados do Ensaio:")
            res1, res2, res3 = st.columns(3)
            res1.metric("Massa Específica Seca", f"{gamma_seca:.3f} g/cm³")
            res2.metric("Massa Específica SSS", f"{gamma_sss:.3f} g/cm³")
            res3.metric("Absorção de Água", f"{absorcao:.2f}%")

# ------------------------------------------------------------------------------
# 4. MASSA UNITÁRIA (NBR 16972)
# ------------------------------------------------------------------------------
elif ensaio == "4. Massa Unitária e Volume de Vazios (NBR 16972)":
    st.header("Massa Unitária e Volume de Vazios (Estado Solto)")

    c1, c2 = st.columns(2)
    with c1:
        v_rec = st.number_input("Volume do recipiente (litros)", value=15.0)
        m_rec = st.number_input("Massa do recipiente vazio (g)", value=4000.0)
    with c2:
        m_rec_amostra = st.number_input("Massa recipiente + agregado solto (g)", value=25000.0)
        gamma_esp = st.number_input("Massa específica real (g/cm³)", value=2.65)

    if st.button("⚖️ Calcular Massa Unitária"):
        if v_rec <= 0 or gamma_esp <= 0 or m_rec_amostra <= m_rec:
            st.error("Verifique os valores informados para volume e massas.")
        else:
            m_amostra = m_rec_amostra - m_rec
            massa_unitaria = (m_amostra / 1000.0) / v_rec
            vazios = (1.0 - (massa_unitaria / gamma_esp)) * 100

            st.success("Resultados do Ensaio:")
            res1, res2 = st.columns(2)
            res1.metric("Massa Unitária Solta (γ_u)", f"{massa_unitaria:.3f} kg/dm³", f"{massa_unitaria * 1000:.1f} kg/m³")
            res2.metric("Índice de Vazios Solto", f"{vazios:.2f}%")

# ------------------------------------------------------------------------------
# 5. RESISTÊNCIA À COMPRESSÃO EM LOTE (NBR 5739)
# ------------------------------------------------------------------------------
else:
    st.header("Resistência à Compressão de Corpos de Prova (NBR 5739)")

    c1, c2 = st.columns(2)
    with c1:
        d = st.number_input("Diâmetro nominal do CP (cm)", value=10.0)
        idade = st.text_input("Idade de Rompimento (dias)", value="28")
    with c2:
        h = st.number_input("Altura do CP (cm)", value=20.0)

    st.subheader("Cargas de Ruptura dos CPs do Lote")
    df_cps = pd.DataFrame({
        "Identificação CP": ["CP-01", "CP-02"],
        "Carga Ruptura (kN)": [245.0, 255.0]
    })
    df_cps_edit = st.data_editor(df_cps, num_rows="dynamic", use_container_width=True)

    if st.button("💥 Calcular Lote de Compressão"):
        if d <= 0:
            st.error("O diâmetro deve ser maior que zero.")
        else:
            area_cm2 = (math.pi * (d ** 2)) / 4.0
            fcs = []
            for _, row in df_cps_edit.iterrows():
                f_n = row["Carga Ruptura (kN)"] * 1000.0
                fc = (f_n / area_cm2) / 10.0
                fcs.append(round(fc, 2))

            df_resultado = df_cps_edit.copy()
            df_resultado["Tensão fc (MPa)"] = fcs
            fc_medio = sum(fcs) / len(fcs) if len(fcs) > 0 else 0

            st.success("Resultados do Lote:")
            st.dataframe(df_resultado, use_container_width=True)
            
            c1, c2 = st.columns(2)
            c1.metric("Resistência Média (fc,m)", f"{fc_medio:.2f} MPa")
            c2.metric("Área da Seção Transversal", f"{area_cm2:.2f} cm²")
