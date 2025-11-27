import streamlit as st
import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, accuracy_score

# Configuração da página
st.set_page_config(
    page_title="FarmTech Solutions - ML Dashboard",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #2E7D32;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .success-box {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border-left: 5px solid #17a2b8;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Cabeçalho
st.markdown('<p class="main-header">🌾 FarmTech Solutions</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Sistema Inteligente de Previsão e Manejo Agrícola</p>', unsafe_allow_html=True)
st.markdown("---")

# Carregar dados e modelos
@st.cache_data
def carregar_dados():
    return pd.read_csv('dados_sensor.csv')

@st.cache_resource
def carregar_modelos():
    with open('modelo_umidade.pkl', 'rb') as f:
        modelo_u = pickle.load(f)
    with open('modelo_irrigacao.pkl', 'rb') as f:
        modelo_i = pickle.load(f)
    return modelo_u, modelo_i

try:
    df = carregar_dados()
    modelo_umidade, modelo_irrigacao = carregar_modelos()
except FileNotFoundError:
    st.error("⚠️ Erro: Execute 'python treinar_modelo.py' primeiro!")
    st.stop()

# Sidebar
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/628/628283.png", width=120)
st.sidebar.title("🎛️ Painel de Controle")
st.sidebar.markdown("---")

opcao = st.sidebar.radio(
    "Navegação:",
    ["🏠 Visão Geral", "🔮 Previsões", "📊 Análise de Dados", 
     "🎯 Métricas dos Modelos", "💡 Recomendações"]
)

st.sidebar.markdown("---")
st.sidebar.info("""
**🌾 FarmTech Solutions**  
Sistema de IA para Agricultura de Precisão

**Modelos:**
- Regressão Linear (Umidade)
- Classificação (Irrigação)
""")

# ============== SEÇÃO 1: VISÃO GERAL ==============
if opcao == "🏠 Visão Geral":
    st.header("🏠 Visão Geral do Sistema")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Registros", f"{len(df)}")
    with col2:
        st.metric("💧 Umidade Média", f"{df['Umidade(%)'].mean():.1f}%")
    with col3:
        st.metric("⚗️ pH Médio", f"{df['pH'].mean():.2f}")
    with col4:
        irrigacoes = df['Irrigando'].sum()
        st.metric("🚿 Irrigações", f"{irrigacoes}")
    
    st.markdown("---")
    
    # Gráficos lado a lado
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Evolução da Umidade do Solo")
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(df.index, df['Umidade(%)'], marker='o', linewidth=2, 
                color='#2196F3', markersize=6)
        ax.axhline(y=df['Umidade(%)'].mean(), color='red', linestyle='--', 
                   label=f'Média: {df["Umidade(%)"].mean():.1f}%')
        ax.fill_between(df.index, df['Umidade(%)'], alpha=0.3, color='#2196F3')
        ax.set_xlabel('Índice de Leitura', fontsize=11)
        ax.set_ylabel('Umidade (%)', fontsize=11)
        ax.legend()
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
    
    with col2:
        st.subheader("⚗️ Distribuição do pH do Solo")
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.hist(df['pH'], bins=15, color='#4CAF50', edgecolor='black', alpha=0.7)
        ax.axvline(df['pH'].mean(), color='red', linestyle='--', linewidth=2,
                   label=f'Média: {df["pH"].mean():.2f}')
        ax.set_xlabel('pH', fontsize=11)
        ax.set_ylabel('Frequência', fontsize=11)
        ax.legend()
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
    
    st.markdown("---")
    
    # Nutrientes
    st.subheader("🧪 Status dos Nutrientes (NPK)")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        n_percent = (df['Nitrogenio'].sum() / len(df)) * 100
        st.metric("🟦 Nitrogênio (N)", f"{n_percent:.1f}%", 
                  delta="Aplicado" if n_percent > 0 else "Não aplicado")
    with col2:
        p_percent = (df['Fosforo'].sum() / len(df)) * 100
        st.metric("🟧 Fósforo (P)", f"{p_percent:.1f}%",
                  delta="Aplicado" if p_percent > 0 else "Não aplicado")
    with col3:
        k_percent = (df['Potassio'].sum() / len(df)) * 100
        st.metric("🟨 Potássio (K)", f"{k_percent:.1f}%",
                  delta="Aplicado" if k_percent > 0 else "Não aplicado")

# ============== SEÇÃO 2: PREVISÕES ==============
elif opcao == "🔮 Previsões":
    st.header("🔮 Realizar Previsões")
    
    st.markdown("""
    Use os controles abaixo para simular diferentes cenários e obter previsões:
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎛️ Parâmetros de Entrada")
        
        ph = st.slider("⚗️ pH do Solo", 
                      min_value=0.0, max_value=14.0, value=6.5, step=0.1)
        
        nitrogenio = st.selectbox("🟦 Nitrogênio (N)", [0, 1], 
                                  format_func=lambda x: "Não Aplicado" if x == 0 else "Aplicado")
        
        fosforo = st.selectbox("🟧 Fósforo (P)", [0, 1],
                               format_func=lambda x: "Não Aplicado" if x == 0 else "Aplicado")
        
        potassio = st.selectbox("🟨 Potássio (K)", [0, 1],
                                format_func=lambda x: "Não Aplicado" if x == 0 else "Aplicado")
    
    with col2:
        st.subheader("📊 Resultados das Previsões")
        
        if st.button("🚀 CALCULAR PREVISÕES", type="primary", use_container_width=True):
            # Previsão de Umidade
            entrada_umidade = np.array([[ph, nitrogenio, fosforo, potassio]])
            umidade_prevista = modelo_umidade.predict(entrada_umidade)[0]
            
            st.markdown("### 💧 Umidade do Solo Prevista")
            st.metric("Umidade", f"{umidade_prevista:.2f}%", 
                     delta=f"{umidade_prevista - df['Umidade(%)'].mean():.2f}% vs média")
            
            # Previsão de Irrigação
            entrada_irrigacao = np.array([[umidade_prevista, ph, nitrogenio, fosforo, potassio]])
            irrigacao_prevista = modelo_irrigacao.predict(entrada_irrigacao)[0]
            prob_irrigacao = modelo_irrigacao.predict_proba(entrada_irrigacao)[0]
            
            st.markdown("### 🚿 Necessidade de Irrigação")
            
            if irrigacao_prevista == 1:
                st.error(f"**⚠️ IRRIGAÇÃO NECESSÁRIA** ({prob_irrigacao[1]*100:.1f}% de confiança)")
            else:
                st.success(f"**✅ IRRIGAÇÃO NÃO NECESSÁRIA** ({prob_irrigacao[0]*100:.1f}% de confiança)")
            
            # Barra de progresso
            st.progress(prob_irrigacao[1])
    
    st.markdown("---")
    
    # Simulador rápido
    st.subheader("⚡ Simulador Rápido")
    st.markdown("Veja como diferentes níveis de umidade afetam a necessidade de irrigação:")
    
    umidades_teste = np.linspace(15, 90, 20)
    resultados = []
    
    for u in umidades_teste:
        entrada = np.array([[u, 6.5, 0, 0, 0]])
        pred = modelo_irrigacao.predict(entrada)[0]
        resultados.append(pred)
    
    fig, ax = plt.subplots(figsize=(12, 5))
    cores = ['#4CAF50' if r == 0 else '#F44336' for r in resultados]
    ax.bar(umidades_teste, [1]*len(umidades_teste), color=cores, width=3, edgecolor='black')
    ax.set_xlabel('Umidade do Solo (%)', fontsize=12)
    ax.set_ylabel('Decisão', fontsize=12)
    ax.set_title('Limiar de Decisão para Irrigação', fontsize=14, fontweight='bold')
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['Não Irrigar', 'Irrigar'])
    ax.grid(True, alpha=0.3, axis='x')
    st.pyplot(fig)

# ============== SEÇÃO 3: ANÁLISE DE DADOS ==============
elif opcao == "📊 Análise de Dados":
    st.header("📊 Análise Exploratória dos Dados")
    
    # Estatísticas
    st.subheader("📈 Estatísticas Descritivas")
    st.dataframe(df.describe(), use_container_width=True)
    
    st.markdown("---")
    
    # Matriz de Correlação
    st.subheader("🔗 Matriz de Correlação")
    
    fig, ax = plt.subplots(figsize=(10, 8))
    correlacao = df[['Umidade(%)', 'pH', 'Nitrogenio', 'Fosforo', 'Potassio', 'Irrigando']].corr()
    sns.heatmap(correlacao, annot=True, cmap='RdYlGn', center=0, 
                square=True, linewidths=2, fmt='.2f', ax=ax,
                cbar_kws={'label': 'Coeficiente de Correlação'})
    ax.set_title('Correlação entre Variáveis Agrícolas', fontsize=14, fontweight='bold')
    st.pyplot(fig)
    
    st.markdown("---")
    
    # Scatter plots
    st.subheader("📉 Relações entre Variáveis")
    
    var_x = st.selectbox("Selecione variável X:", ['pH', 'Nitrogenio', 'Fosforo', 'Potassio'])
    var_y = st.selectbox("Selecione variável Y:", ['Umidade(%)', 'Irrigando'])
    
    fig, ax = plt.subplots(figsize=(10, 6))
    scatter = ax.scatter(df[var_x], df[var_y], c=df['Irrigando'], 
                        cmap='RdYlGn', s=100, edgecolors='black', alpha=0.7)
    ax.set_xlabel(var_x, fontsize=12)
    ax.set_ylabel(var_y, fontsize=12)
    ax.set_title(f'Relação: {var_x} vs {var_y}', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Irrigando', fontsize=10)
    st.pyplot(fig)

# ============== SEÇÃO 4: MÉTRICAS ==============
elif opcao == "🎯 Métricas dos Modelos":
    st.header("🎯 Desempenho dos Modelos de Machine Learning")
    
    # MODELO 1: Regressão (Umidade)
    st.subheader("📊 Modelo 1: Regressão Linear - Previsão de Umidade")
    
    X_umidade = df[['pH', 'Nitrogenio', 'Fosforo', 'Potassio']]
    y_umidade = df['Umidade(%)']
    y_pred_umidade = modelo_umidade.predict(X_umidade)
    
    mae = mean_absolute_error(y_umidade, y_pred_umidade)
    mse = mean_squared_error(y_umidade, y_pred_umidade)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_umidade, y_pred_umidade)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("MAE", f"{mae:.3f}%", help="Erro Médio Absoluto")
    with col2:
        st.metric("MSE", f"{mse:.3f}", help="Erro Quadrático Médio")
    with col3:
        st.metric("RMSE", f"{rmse:.3f}%", help="Raiz do MSE")
    with col4:
        st.metric("R²", f"{r2:.3f}", help="Coeficiente de Determinação")
    
    # Interpretação
    if r2 > 0.7:
        st.success(f"✅ Modelo com **excelente** desempenho! Explica {r2*100:.1f}% da variação.")
    elif r2 > 0.5:
        st.info(f"ℹ️ Modelo com **bom** desempenho. Explica {r2*100:.1f}% da variação.")
    else:
        st.warning(f"⚠️ Modelo com desempenho **moderado**. Explica {r2*100:.1f}% da variação.")
    
    # Gráfico Real vs Previsto
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(y_umidade, y_pred_umidade, alpha=0.7, edgecolors='k', s=100)
    ax.plot([y_umidade.min(), y_umidade.max()], 
            [y_umidade.min(), y_umidade.max()], 
            'r--', lw=2, label='Previsão Perfeita')
    ax.set_xlabel('Umidade Real (%)', fontsize=12)
    ax.set_ylabel('Umidade Prevista (%)', fontsize=12)
    ax.set_title('Real vs Previsto - Modelo de Umidade', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
    
    st.markdown("---")
    
    # MODELO 2: Classificação (Irrigação)
    st.subheader("🎯 Modelo 2: Classificação - Previsão de Irrigação")
    
    X_irrig = df[['Umidade(%)', 'pH', 'Nitrogenio', 'Fosforo', 'Potassio']]
    y_irrig = df['Irrigando']
    y_pred_irrig = modelo_irrigacao.predict(X_irrig)
    
    acuracia = accuracy_score(y_irrig, y_pred_irrig)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🎯 Acurácia", f"{acuracia*100:.1f}%")
    with col2:
        st.metric("✅ Acertos", f"{sum(y_irrig == y_pred_irrig)}/{len(y_irrig)}")
    with col3:
        st.metric("❌ Erros", f"{sum(y_irrig != y_pred_irrig)}/{len(y_irrig)}")
    
    if acuracia > 0.9:
        st.success(f"✅ Modelo com **excelente** precisão! ({acuracia*100:.1f}%)")
    elif acuracia > 0.7:
        st.info(f"ℹ️ Modelo com **boa** precisão. ({acuracia*100:.1f}%)")
    else:
        st.warning(f"⚠️ Modelo com precisão **moderada**. ({acuracia*100:.1f}%)")
    
    # Importância das variáveis
    st.markdown("---")
    st.subheader("⚖️ Importância das Variáveis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Modelo de Umidade:**")
        features_u = ['pH', 'Nitrogênio', 'Fósforo', 'Potássio']
        coefs_u = modelo_umidade.coef_
        
        fig, ax = plt.subplots(figsize=(8, 5))
        cores = ['#4CAF50' if x > 0 else '#F44336' for x in coefs_u]
        ax.barh(features_u, coefs_u, color=cores, edgecolor='black')
        ax.set_xlabel('Coeficiente', fontsize=11)
        ax.set_title('Impacto na Umidade', fontsize=12, fontweight='bold')
        ax.axvline(x=0, color='black', linestyle='--', linewidth=1)
        ax.grid(True, alpha=0.3, axis='x')
        st.pyplot(fig)
    
    with col2:
        st.markdown("**Modelo de Irrigação:**")
        features_i = ['Umidade', 'pH', 'Nitrogênio', 'Fósforo', 'Potássio']
        coefs_i = modelo_irrigacao.coef_[0]
        
        fig, ax = plt.subplots(figsize=(8, 5))
        cores = ['#4CAF50' if x > 0 else '#F44336' for x in coefs_i]
        ax.barh(features_i, coefs_i, color=cores, edgecolor='black')
        ax.set_xlabel('Coeficiente', fontsize=11)
        ax.set_title('Impacto na Irrigação', fontsize=12, fontweight='bold')
        ax.axvline(x=0, color='black', linestyle='--', linewidth=1)
        ax.grid(True, alpha=0.3, axis='x')
        st.pyplot(fig)

# ============== SEÇÃO 5: RECOMENDAÇÕES ==============
elif opcao == "💡 Recomendações":
    st.header("💡 Recomendações Inteligentes de Manejo")
    
    # Análise atual
    umidade_atual = df['Umidade(%)'].iloc[-1]
    ph_atual = df['pH'].iloc[-1]
    
    st.subheader("📊 Status Atual do Solo")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💧 Umidade Atual", f"{umidade_atual:.1f}%")
    with col2:
        st.metric("⚗️ pH Atual", f"{ph_atual:.2f}")
    with col3:
        irrigando = df['Irrigando'].iloc[-1]
        st.metric("🚿 Irrigação", "Ativa" if irrigando == 1 else "Inativa")
    
    st.markdown("---")
    
    # Recomendações baseadas em umidade
    st.subheader("💧 Análise de Umidade")
    
    if umidade_atual < 30:
        st.markdown('<div class="warning-box">⚠️ <strong>ALERTA: Umidade Baixa</strong><br>Risco de estresse hídrico nas plantas</div>', unsafe_allow_html=True)
        st.markdown("""
        **Ações Recomendadas:**
        - 🚿 Iniciar irrigação imediatamente
        - 📊 Monitorar evolução a cada 2 horas
        - 🔍 Verificar sistema de irrigação
        """)
    elif umidade_atual > 70:
        st.markdown('<div class="info-box">ℹ️ <strong>INFORMAÇÃO: Umidade Alta</strong><br>Solo bem hidratado</div>', unsafe_allow_html=True)
        st.markdown("""
        **Ações Recomendadas:**
        - ✅ Manter monitoramento regular
        - ⚠️ Evitar irrigação excessiva
        - 🌱 Condições ideais para desenvolvimento
        """)
    else:
        st.markdown('<div class="success-box">✅ <strong>ÓTIMO: Umidade Ideal</strong><br>Solo em condições adequadas</div>', unsafe_allow_html=True)
        st.markdown("""
        **Ações Recomendadas:**
        - ✓ Manter níveis atuais
        - 📊 Monitoramento diário
        """)
    
    st.markdown("---")
    
    # Recomendações baseadas em pH
    st.subheader("⚗️ Análise de pH")
    
    if ph_atual < 5.5:
        st.warning("⚠️ **pH ÁCIDO** - Pode afetar absorção de nutrientes")
        st.markdown("""
        **Correção Recomendada:**
        - 🧪 Aplicar calcário para elevar pH
        - 📊 Realizar nova análise em 30 dias
        - 🌱 Monitorar desenvolvimento das plantas
        """)
    elif ph_atual > 7.5:
        st.warning("⚠️ **pH ALCALINO** - Pode limitar disponibilidade de nutrientes")
        st.markdown("""
        **Correção Recomendada:**
        - 🧪 Aplicar enxofre elementar
        - 📊 Realizar nova análise em 30 dias
        - 🌱 Atenção a deficiências nutricionais
        """)
    else:
        st.success("✅ **pH ADEQUADO** - Faixa ideal para maioria das culturas (5.5-7.5)")
        st.markdown("Manter monitoramento regular do pH do solo.")
    
    st.markdown("---")
    
    # Recomendações de NPK
    st.subheader("🧪 Análise de Nutrientes (NPK)")
    
    n_aplicado = df['Nitrogenio'].iloc[-1]
    p_aplicado = df['Fosforo'].iloc[-1]
    k_aplicado = df['Potassio'].iloc[-1]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if n_aplicado == 0:
            st.info("🟦 **Nitrogênio:** Não aplicado recentemente")
            st.caption("Considerar adubação nitrogenada")
        else:
            st.success("🟦 **Nitrogênio:** Aplicado")
            st.caption("Monitorar resposta da cultura")
    
    with col2:
        if p_aplicado == 0:
            st.info("🟧 **Fósforo:** Não aplicado recentemente")
            st.caption("Avaliar necessidade de adubação fosfatada")
        else:
            st.success("🟧 **Fósforo:** Aplicado")
            st.caption("Favorecer desenvolvimento radicular")
    
    with col3:
        if k_aplicado == 0:
            st.info("🟨 **Potássio:** Não aplicado recentemente")
            st.caption("Considerar adubação potássica")
        else:
            st.success("🟨 **Potássio:** Aplicado")
            st.caption("Importante para qualidade dos frutos")
    
    st.markdown("---")
    
    # Plano de ação geral
    st.subheader("📋 Plano de Ação Semanal")
    
    st.markdown("""
    **Segunda-feira:**
    - 📊 Coletar dados de todos os sensores
    - 💧 Verificar sistema de irrigação
    
    **Quarta-feira:**
    - 🧪 Realizar análise de pH
    - 🌱 Inspeção visual das culturas
    
    **Sexta-feira:**
    - 📈 Revisar dados da semana
    - 🎯 Ajustar parâmetros conforme necessário
    - 📋 Planejar ações para próxima semana
    """)

# Rodapé
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1.5rem; background-color: #f8f9fa; border-radius: 10px;'>
    <h3 style='color: #2E7D32; margin-bottom: 0.5rem;'>🌾 FarmTech Solutions</h3>
    <p style='margin: 0.5rem 0;'><strong>Fase 4:</strong> Previsão Inteligente na Agricultura</p>
    <p style='margin: 0; font-size: 0.9rem; color: #999;'>Inteligência Artificial aplicada ao Agronegócio</p>
</div>
""", unsafe_allow_html=True)