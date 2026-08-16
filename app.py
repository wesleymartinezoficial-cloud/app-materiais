import io
import math
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# ------------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Sistema de Controle Tecnológico - ABNT",
    layout="wide",
    page_icon="🏗️",
)

# ------------------------------------------------------------------------------
# PAINEL LATERAL: DADOS DA OBRA E ENGENHARIA
# ------------------------------------------------------------------------------
st.sidebar.image(
    "https://img.icons8.com/color/96/worker-with-roadblock.png", width=60
)
st.sidebar.title("Informações do Laudo")

obra = st.sidebar.text_input("Obra / Empreendimento", value="Residencial Unifamiliar")
cliente = st.sidebar.text_input("Cliente / Contratante", value="Construtora X")
responsavel = st.sidebar.text_input(
    "Engenheiro Responsável / CREA", value="Eng. Silvério Medeiros"
)
data_ensaio = st.sidebar.date_input("Data da Coleta/Ensaio")

st.sidebar.markdown("---")
st.sidebar.caption("Normas Aplicadas: NBR 17054 | 16916 | 16917 | 16972 | 5739")

# ------------------------------------------------------------------------------
# CABEÇALHO PRINCIPAL
# ------------------------------------------------------------------------------
st.title("🏗️ Sistema Integrado de Controle Tecnológico")
st.caption(
    f"**Obra:** {obra} | **Responsável:** {responsavel} | **Data:** {data_ensaio.strftime('%d/%m/%Y')}"
)

# Organização por Abas
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "📊 Granulometria",
        "🏖️ Agregado Miúdo",
        "🪨 Agregado Graúdo",
        "⚖️ Massa Unitária",
        "💥 Compressão (CPs)",
    ]
)

# ------------------------------------------------------------------------------
# ABA 1: GRANULOMETRIA (NBR 17054)
# ------------------------------------------------------------------------------
with tab1:
    st.subheader("Análise Granulométrica de Agregados (NBR 17054)")

    LIMITES_MASSA = {
        "Areia (Agregado Miúdo)": {
            "massa_min": 300.0,
            "aplicacao": "Argamassas e concreto.",
        },
        "Brita 0 (Pedrisco)": {
            "massa_min": 1000.0,
            "aplicacao": "Pré-fabricados e lajes.",
        },
        "Brita 1": {
            "massa_min": 5000.0,
            "aplicacao": "Concreto armado estrutural.",
        },
        "Brita 2": {
            "massa_min": 10000.0,
            "aplicacao": "Pisos e fundações.",
        },
        "Brita 3": {
            "massa_min": 15000.0,
            "aplicacao": "Concreto massa e drenagem.",
        },
    }

    c1, c2 = st.columns(2)
    with c1:
        tipo = st.selectbox("Tipo de Agregado", list(LIMITES_MASSA.keys()))
    with c2:
        m_min = LIMITES_MASSA[tipo]["massa_min"]
        massa_inicial = st.number_input(
            "Massa Inicial Seca (g)", value=m_min, step=100.0
        )

    st.info(
        f"💡 **Requisito NBR:** Massa mínima recomendada = **{m_min}g** | **Aplicação:** {LIMITES_MASSA[tipo]['aplicacao']}"
    )

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

    df_base = pd.DataFrame(
        {
            "Abertura (mm)": [p["abertura"] for p in PENEIRAS],
            "ASTM": [p["astm"] for p in PENEIRAS],
            "Série": [
                "Normal" if p["serie_normal"] else "Intermediária"
                for p in PENEIRAS
            ],
            "Massa Retida (g)": [0.0] * len(PENEIRAS),
        }
    )

    col_tab, col_fundo = st.columns([3, 1])
    with col_tab:
        df_editado = st.data_editor(
            df_base, use_container_width=True, hide_index=True
        )
    with col_fundo:
        massa_fundo = st.number_input("Fundo Receptor (g)", value=0.0)
        btn_calc_1 = st.button("📊 Processar Granulometria", use_container_width=True)

    if btn_calc_1:
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
            m1, m2, m3 = st.columns(3)
            m1.metric("Massa Recuperada", f"{massa_rec:.1f} g")
            m2.metric(
                "Erro de Perda",
                f"{erro:.2f}%",
                delta="✓ Dentro do limite"
                if erro <= 1.0
                else "❌ Fora do limite (>1%)",
                delta_color="normal" if erro <= 1.0 else "inverse",
            )
            m3.metric(
                "Módulo de Finura (MF)",
                f"{mf:.2f}",
                f"DMC: {dmc if dmc else 'N/I'} mm",
            )

            fig, ax = plt.subplots(figsize=(8, 3))
            ax.plot(
                df_res["Abertura (mm)"],
                df_res["Passante (%)"],
                marker="o",
                color="#005580",
                linewidth=2,
            )
            ax.set_xscale("log")
            ax.invert_xaxis()
            ax.set_title(f"Curva Granulométrica - {tipo}")
            ax.set_xlabel("Abertura das Peneiras (mm) - Escala Logarítmica")
            ax.set_ylabel("Passante Acumulado (%)")
            ax.grid(True, which="both", linestyle="--", alpha=0.5)

            st.pyplot(fig)

            with st.expander("📄 Ver Tabela Completa de Resultados"):
                st.dataframe(df_res, use_container_width=True)

# ------------------------------------------------------------------------------
# ABA 2: MASSA ESPECÍFICA - AGREGADO MIÚDO (NBR 16916)
# ------------------------------------------------------------------------------
with tab2:
    st.subheader(
        "Massa Específica e Absorção de Água - Agregado Miúdo (NBR 16916)"
    )

    c1, c2 = st.columns(2)
    with c1:
        m_seco_m = st.number_input(
            "Massa da amostra seca em estufa (g)", value=490.0, key="m_seco_m"
        )
        m_sss_m = st.number_input(
            "Massa da amostra SSS (g)", value=500.0, key="m_sss_m"
        )
    with c2:
        m_pic_agua = st.number_input(
            "Massa do picnômetro + água (g)", value=1300.0
        )
        m_pic_amostra_agua = st.number_input(
            "Massa do picnômetro + amostra SSS + água (g)", value=1610.0
        )

    if st.button("🧪 Calcular Agregado Miúdo", use_container_width=True):
        den = m_pic_agua + m_sss_m - m_pic_amostra_agua
        if den <= 0 or m_seco_m <= 0:
            st.error("Erro nos dados digitados. Verifique as massas informadas.")
        else:
            gamma_seca = m_seco_m / den
            gamma_sss = m_sss_m / den
            absorcao = ((m_sss_m - m_seco_m) / m_seco_m) * 100

            st.success("Resultados Apurados:")
            r1, r2, r3 = st.columns(3)
            r1.metric("Massa Específica Seca", f"{gamma_seca:.3f} g/cm³")
            r2.metric("Massa Específica SSS", f"{gamma_sss:.3f} g/cm³")
            r3.metric("Absorção de Água", f"{absorcao:.2f}%")

# ------------------------------------------------------------------------------
# ABA 3: MASSA ESPECÍFICA - AGREGADO GRAÚDO (NBR 16917)
# ------------------------------------------------------------------------------
with tab3:
    st.subheader(
        "Massa Específica e Absorção de Água - Agregado Graúdo (NBR 16917)"
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        m_seco_g = st.number_input(
            "Massa da amostra seca em estufa (g)", value=3000.0, key="m_seco_g"
        )
    with c2:
        m_sss_g = st.number_input(
            "Massa SSS no ar (g)", value=3040.0, key="m_sss_g"
        )
    with c3:
        m_submersa = st.number_input(
            "Massa aparente submersa (g)", value=1900.0
        )

    if st.button("🧪 Calcular Agregado Graúdo", use_container_width=True):
        den = m_sss_g - m_submersa
        if den <= 0 or m_seco_g <= 0:
            st.error("A massa submersa deve ser menor que a massa SSS.")
        else:
            gamma_seca = m_seco_g / den
            gamma_sss = m_sss_g / den
            absorcao = ((m_sss_g - m_seco_g) / m_seco_g) * 100

            st.success("Resultados Apurados:")
            r1, r2, r3 = st.columns(3)
            r1.metric("Massa Específica Seca", f"{gamma_seca:.3f} g/cm³")
            r2.metric("Massa Específica SSS", f"{gamma_sss:.3f} g/cm³")
            r3.metric("Absorção de Água", f"{absorcao:.2f}%")

# ------------------------------------------------------------------------------
# ABA 4: MASSA UNITÁRIA (NBR 16972)
# ------------------------------------------------------------------------------
with tab4:
    st.subheader("Massa Unitária e Volume de Vazios - Estado Solto (NBR 16972)")

    c1, c2 = st.columns(2)
    with c1:
        v_rec = st.number_input("Volume do recipiente (litros)", value=15.0)
        m_rec = st.number_input("Massa do recipiente vazio (g)", value=4000.0)
    with c2:
        m_rec_amostra = st.number_input(
            "Massa recipiente + agregado solto (g)", value=25000.0
        )
        gamma_esp = st.number_input(
            "Massa específica real do agregado (g/cm³)", value=2.65
        )

    if st.button("⚖️ Calcular Massa Unitária", use_container_width=True):
        if v_rec <= 0 or gamma_esp <= 0 or m_rec_amostra <= m_rec:
            st.error("Verifique os valores informados para volume e massas.")
        else:
            m_amostra = m_rec_amostra - m_rec
            massa_unitaria = (m_amostra / 1000.0) / v_rec
            vazios = (1.0 - (massa_unitaria / gamma_esp)) * 100

            st.success("Resultados Apurados:")
            r1, r2 = st.columns(2)
            r1.metric(
                "Massa Unitária Solta (γ_u)",
                f"{massa_unitaria:.3f} kg/dm³",
                f"{massa_unitaria * 1000:.1f} kg/m³",
            )
            r2.metric("Índice de Vazios Solto", f"{vazios:.2f}%")

# ------------------------------------------------------------------------------
# ABA 5: RESISTÊNCIA À COMPRESSÃO EM LOTE (NBR 5739)
# ------------------------------------------------------------------------------
with tab5:
    st.subheader("Resistência à Compressão de Corpos de Prova (NBR 5739)")

    c1, c2, c3 = st.columns(3)
    with c1:
        d = st.number_input("Diâmetro nominal do CP (cm)", value=10.0)
    with c2:
        h = st.number_input("Altura do CP (cm)", value=20.0)
    with c3:
        idade = st.text_input("Idade de Rompimento (dias)", value="28")

    st.write("**Entrada de Cargas de Ruptura do Lote:**")
    df_cps = pd.DataFrame(
        {"Identificação": ["CP-01", "CP-02"], "Carga Ruptura (kN)": [245.0, 255.0]}
    )
    df_cps_edit = st.data_editor(
        df_cps, num_rows="dynamic", use_container_width=True, hide_index=True
    )

    if st.button("💥 Calcular Lote de Rompimento", use_container_width=True):
        if d <= 0:
            st.error("O diâmetro deve ser maior que zero.")
        else:
            area_cm2 = (math.pi * (d**2)) / 4.0
            fcs = []
            for _, row in df_cps_edit.iterrows():
                f_n = row["Carga Ruptura (kN)"] * 1000.0
                fc = (f_n / area_cm2) / 10.0
                fcs.append(round(fc, 2))

            df_resultado = df_cps_edit.copy()
            df_resultado["Tensão fc (MPa)"] = fcs
            fc_medio = sum(fcs) / len(fcs) if len(fcs) > 0 else 0

            st.success(f"Lote Processado para {idade} dias:")
            st.dataframe(df_resultado, use_container_width=True)

            r1, r2 = st.columns(2)
            r1.metric("Resistência Média (fc,m)", f"{fc_medio:.2f} MPa")
            r2.metric("Área da Seção Transversal", f"{area_cm2:.2f} cm²")

# ------------------------------------------------------------------------------
# RODAPÉ DE EXPLICABILIDADE DA NORMA
# ------------------------------------------------------------------------------
st.markdown("---")
with st.expander("📚 Memória de Cálculo e Referência das Normas"):
    st.markdown("""
    * **NBR 17054:** Erro de perda acumulada máximo aceitável = $1,0\%$.
    * **NBR 16916 / 16917:** Absorção $(\%) = \\frac{M_{sss} - M_{seca}}{M_{seca}} \\times 100$.
    * **NBR 16972:** Volume de vazios $(\%) = \\left(1 - \\frac{\\gamma_u}{\\gamma_{real}}\\right) \\times 100$.
    * **NBR 5739:** Tensão $f_c (MPa) = \\frac{F (N)}{A (mm^2)}$.
    """)
