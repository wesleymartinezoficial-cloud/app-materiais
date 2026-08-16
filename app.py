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
data_ensaio = st.sidebar.date_input("Data do Ensaio")

st.sidebar.markdown("---")
st.sidebar.caption(
    "Normas: NBR 17054 | 16916 | 16917 | 16972 | 5739 | 12655 | NM 46 | 16889 | 15270"
)

# ------------------------------------------------------------------------------
# CABEÇALHO PRINCIPAL
# ------------------------------------------------------------------------------
st.title("🏗️ Sistema Integrado de Controle Tecnológico e Dosagem")
st.caption(
    f"**Obra:** {obra} | **Responsável:** {responsavel} | **Data:** {data_ensaio.strftime('%d/%m/%Y')}"
)

# Organização em Abas
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
    [
        "📊 Granulometria & Pulverulento",
        "🏖️ Agregados (Físico)",
        "💥 Compressão & fck (NBR 12655)",
        "🧱 Blocos / Alvenaria",
        "📐 Slump Test (Concreto)",
        "🧮 Dosagem / Traço (ABCP)",
        "📚 Memória de Cálculo",
    ]
)

# ------------------------------------------------------------------------------
# ABA 1: GRANULOMETRIA & MATERIAL PULVERULENTO (NBR 17054 / NBR NM 46)
# ------------------------------------------------------------------------------
with tab1:
    st.subheader("Análise Granulométrica e Material Pulverulento")

    LIMITES_MASSA = {
        "Areia (Agregado Miúdo)": {"massa_min": 300.0, "aplicacao": "Argamassas e concreto."},
        "Brita 0 (Pedrisco)": {"massa_min": 1000.0, "aplicacao": "Pré-fabricados e lajes."},
        "Brita 1": {"massa_min": 5000.0, "aplicacao": "Concreto armado estrutural."},
        "Brita 2": {"massa_min": 10000.0, "aplicacao": "Pisos e fundações."},
    }

    c1, c2 = st.columns(2)
    with c1:
        tipo = st.selectbox("Tipo de Agregado", list(LIMITES_MASSA.keys()))
    with c2:
        m_min = LIMITES_MASSA[tipo]["massa_min"]
        massa_inicial = st.number_input("Massa Inicial Seca (g)", value=m_min, step=100.0)

    st.markdown("---")
    st.write("**1.1 Material Pulverulento (< 0,075 mm - Peneira Nº 200 - NBR NM 46)**")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        m_seca_lavada = st.number_input("Massa da amostra seca APÓS lavagem na #200 (g)", value=massa_inicial * 0.97)
    with col_p2:
        if massa_inicial > 0:
            mat_pulverulento = ((massa_inicial - m_seca_lavada) / massa_inicial) * 100
            st.metric("Teor de Material Pulverulento", f"{mat_pulverulento:.2f}%")

    st.markdown("---")
    st.write("**1.2 Ensaio de Peneiramento Granulométrico (NBR 17054)**")

    PENEIRAS = [
        {"abertura": 37.5, "astm": '1 1/2"', "serie_normal": True},
        {"abertura": 19.0, "astm": '3/4"', "serie_normal": True},
        {"abertura": 9.5, "astm": '3/8"', "serie_normal": True},
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

    col_tab, col_fundo = st.columns([3, 1])
    with col_tab:
        df_editado = st.data_editor(df_base, use_container_width=True, hide_index=True)
    with col_fundo:
        massa_fundo = st.number_input("Fundo Receptor (g)", value=0.0)
        btn_calc_1 = st.button("📊 Processar Granulometria", use_container_width=True)

    if btn_calc_1 and massa_inicial > 0:
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

        m1, m2, m3 = st.columns(3)
        m1.metric("Massa Recuperada", f"{massa_rec:.1f} g")
        m2.metric("Erro de Perda", f"{erro:.2f}%", delta="✓ Aprovado" if erro <= 1.0 else "❌ Reprovado (>1%)", delta_color="normal" if erro <= 1.0 else "inverse")
        m3.metric("Módulo de Finura (MF)", f"{mf:.2f}", f"DMC: {dmc if dmc else 'N/I'} mm")

        fig, ax = plt.subplots(figsize=(8, 3))
        ax.plot(df_res["Abertura (mm)"], df_res["Passante (%)"], marker="o", color="#005580", linewidth=2)
        ax.set_xscale("log")
        ax.invert_xaxis()
        ax.set_title(f"Curva Granulométrica - {tipo}")
        ax.set_xlabel("Abertura (mm) - Log")
        ax.set_ylabel("Passante Acumulado (%)")
        ax.grid(True, which="both", linestyle="--", alpha=0.5)
        st.pyplot(fig)

# ------------------------------------------------------------------------------
# ABA 2: AGREGADOS - FÍSICO E MASSA UNITÁRIA (NBR 16916 / 16917 / 16972)
# ------------------------------------------------------------------------------
with tab2:
    st.subheader("Caracterização Física de Agregados")
    
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        st.markdown("**Agregado Miúdo (Areia)**")
        m_seco_m = st.number_input("Massa Seca (g)", value=490.0)
        m_sss_m = st.number_input("Massa SSS (g)", value=500.0)
        m_pic_agua = st.number_input("Massa Picnômetro + Água (g)", value=1300.0)
        m_pic_am_ag = st.number_input("Massa Picnômetro + Amostra + Água (g)", value=1610.0)
        
        if st.button("Calcular Miúdo"):
            den = m_pic_agua + m_sss_m - m_pic_am_ag
            if den > 0:
                st.success(f"Massa Específica Seca: {m_seco_m/den:.3f} g/cm³ | Absorção: {((m_sss_m - m_seco_m)/m_seco_m)*100:.2f}%")

    with col_a2:
        st.markdown("**Massa Unitária Solta (NBR 16972)**")
        v_rec = st.number_input("Volume Recipiente (L)", value=15.0)
        m_rec = st.number_input("Massa Recipiente Vazio (g)", value=4000.0)
        m_rec_am = st.number_input("Massa Recipiente + Agregado (g)", value=25000.0)
        gamma_esp = st.number_input("Massa Específica Real (g/cm³)", value=2.65)
        
        if st.button("Calcular Unitária"):
            m_am = m_rec_am - m_rec
            gamma_u = (m_am / 1000.0) / v_rec
            vazios = (1.0 - (gamma_u / gamma_esp)) * 100
            st.success(f"Massa Unitária: {gamma_u:.3f} kg/dm³ ({gamma_u*1000:.0f} kg/m³) | Vazios: {vazios:.2f}%")

# ------------------------------------------------------------------------------
# ABA 3: COMPRESSÃO E ESTATÍSTICA FCK (NBR 5739 / NBR 12655)
# ------------------------------------------------------------------------------
with tab3:
    st.subheader("Resistência à Compressão e Validação de Lote (fck,est)")
    
    c_cp1, c_cp2, c_cp3 = st.columns(3)
    with c_cp1:
        d = st.number_input("Diâmetro do CP (cm)", value=10.0)
    with c_cp2:
        h = st.number_input("Altura do CP (cm)", value=20.0)
    with c_cp3:
        idade = st.text_input("Idade (dias)", value="28")

    st.write("**Resultados de Ruptura dos CPs:**")
    df_cps = pd.DataFrame({"CP": ["CP-01", "CP-02", "CP-03", "CP-04", "CP-05"], "Carga (kN)": [240.0, 255.0, 248.0, 260.0, 242.0]})
    df_cps_edit = st.data_editor(df_cps, num_rows="dynamic", use_container_width=True, hide_index=True)

    if st.button("💥 Processar Lote e Calcular fck,est", use_container_width=True):
        area_cm2 = (math.pi * (d**2)) / 4.0
        fcs = [(row["Carga (kN)"] * 1000.0 / area_cm2) / 10.0 for _, row in df_cps_edit.iterrows()]
        
        df_res_cp = df_cps_edit.copy()
        df_res_cp["fc (MPa)"] = [round(x, 2) for x in fcs]
        
        n = len(fcs)
        if n >= 2:
            fcs_ordenados = sorted(fcs)
            fc_m = sum(fcs) / n
            
            # Cálculo NBR 12655 (Amostragem Parcial n < 20)
            m = math.floor(n / 2)
            soma_menores = sum(fcs_ordenados[:m])
            fck_est_1 = (2 * (soma_menores / m)) - fcs_ordenados[m]
            fck_est_2 = 0.85 * fc_m
            fck_est = max(fck_est_1, fck_est_2)

            st.dataframe(df_res_cp, use_container_width=True)
            k1, k2, k3 = st.columns(3)
            k1.metric("Resistência Média (fc,m)", f"{fc_m:.2f} MPa")
            k2.metric("fck Estimado (NBR 12655)", f"{fck_est:.2f} MPa")
            k3.metric("Menor Valor (f1)", f"{fcs_ordenados[0]:.2f} MPa")

# ------------------------------------------------------------------------------
# ABA 4: BLOCOS E ALVENARIA (NBR 15270 / NBR 6136)
# ------------------------------------------------------------------------------
with tab4:
    st.subheader("Resistência à Compressão de Blocos de Alvenaria")
    
    cb1, cb2, cb3 = st.columns(3)
    with cb1:
        largura = st.number_input("Largura do Bloco (cm)", value=14.0)
    with cb2:
        comprimento = st.number_input("Comprimento do Bloco (cm)", value=39.0)
    with cb3:
        carga_bloco = st.number_input("Carga de Ruptura (kN)", value=180.0)

    if st.button("🧱 Calcular Resistência do Bloco", use_container_width=True):
        area_bruta = largura * comprimento
        f_b = ((carga_bloco * 1000.0) / area_bruta) / 10.0
        
        b1, b2 = st.columns(2)
        b1.metric("Área Bruta da Face", f"{area_bruta:.1f} cm²")
        b2.metric("Resistência Bruta (fb)", f"{f_b:.2f} MPa")

# ------------------------------------------------------------------------------
# ABA 5: SLUMP TEST / CONSISTÊNCIA (NBR 16889)
# ------------------------------------------------------------------------------
with tab5:
    st.subheader("Ensaio de Abatimento do Tronco de Cone (Slump Test)")
    
    slump = st.number_input("Abatimento Medido (cm)", value=10.0, step=0.5)
    
    # Classificação NBR 16889 / NBR 8953
    if slump < 5.0:
        classe = "S10 (Concreto Seco - Extrusão/Pisos)"
    elif 5.0 <= slump < 10.0:
        classe = "S50 (Elementos Pré-moldados / Pavlov)"
    elif 10.0 <= slump < 16.0:
        classe = "S100 (Vigas, Pilares e Lajes com densidade média de armadura)"
    elif 16.0 <= slump < 22.0:
        classe = "S160 (Concreto Bombeável / Paredes de Concreto)"
    else:
        classe = "S220 (Concreto Fluido / Fundações Profundas)"

    st.info(f"📌 **Classe de Consistência:** {classe}")

# ------------------------------------------------------------------------------
# ABA 6: DOSAGEM E TRAÇO DE CONCRETO (MÉTODO ABCP)
# ------------------------------------------------------------------------------
with tab6:
    st.subheader("Dosagem de Traço de Concreto (Método ABCP)")
    
    d1, d2, d3 = st.columns(3)
    with d1:
        fck_desejado = st.number_input("fck de Projeto (MPa)", value=30.0)
    with d2:
        slump_alvo = st.number_input("Slump Alvo (cm)", value=12.0)
    with d3:
        dmc_brita = st.selectbox("DMC da Brita (mm)", [9.5, 19.0, 25.0, 37.5], index=1)

    if st.button("🧮 Simular Traço Nominal", use_container_width=True):
        # Estimativas simplificadas do método ABCP
        fc28 = fck_desejado + (1.65 * 4.0)  # Desvio padrão = 4 MPa
        rel_ac = round(0.58 - (fc28 - 20) * 0.012, 2)
        
        # Água aproximada por m³ (depende do slump e DMC)
        agua_m3 = 200.0 if dmc_brita == 19.0 else 190.0
        massa_cimento = agua_m3 / rel_ac
        
        # Proporções em massa (1 : m_areia : m_brita)
        m_areia = 2.1
        m_brita = 2.8
        
        st.success(f"Traço em Massa Calculado (1 : a : b : a/c):")
        st.markdown(f"### **1 : {m_areia:.2f} : {m_brita:.2f} / a/c = {rel_ac:.2f}**")
        
        t1, t2, t3 = st.columns(3)
        t1.metric("Consumo de Cimento", f"{massa_cimento:.1f} kg/m³")
        t2.metric("Consumo de Água", f"{agua_m3:.0f} L/m³")
        t3.metric("Resistência de Dosagem (fc28)", f"{fc28:.1f} MPa")

# ------------------------------------------------------------------------------
# ABA 7: MEMÓRIA DE CÁLCULO E NORMAS
# ------------------------------------------------------------------------------
with tab7:
    st.markdown("""
    ### Fórmulas e Referências Normativas
    * **NBR 12655:** $f_{ck,est} = 2 \\cdot \\frac{\\sum f_i}{m} - f_m$
    * **NBR 5739:** $f_c = \\frac{F}{A \\cdot 10}$ (com $F$ em N e $A$ em cm²).
    * **NBR NM 46:** $Pulverulento (\\%) = \\frac{M_{seca} - M_{lavada}}{M_{seca}} \\times 100$.
    * **NBR 15270:** $f_b = \\frac{F}{A_{bruta} \\cdot 10}$.
    """)
