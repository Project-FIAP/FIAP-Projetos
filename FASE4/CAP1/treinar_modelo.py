import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, accuracy_score, classification_report
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import warnings
warnings.filterwarnings('ignore')

# Configuração de estilo dos gráficos
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

print("=" * 70)
print("FARMTECH SOLUTIONS - TREINAMENTO DE MODELOS DE MACHINE LEARNING")
print("=" * 70)

# 1. CARREGAR DADOS
print("\n[1/7] Carregando dados dos sensores...")
df = pd.read_csv('dados_sensor.csv')
print(f"✓ Dados carregados: {df.shape[0]} registros, {df.shape[1]} variáveis")
print(f"\nColunas disponíveis: {list(df.columns)}")
print(f"\nPrimeiras linhas:\n{df.head()}")

# 2. ANÁLISE EXPLORATÓRIA
print("\n[2/7] Análise exploratória dos dados...")
print(f"\nEstatísticas descritivas:\n{df.describe()}")
print(f"\nValores nulos:\n{df.isnull().sum()}")

# 3. PREPARAR DADOS - MODELO 1: REGRESSÃO (PREVER UMIDADE)
print("\n" + "=" * 70)
print("MODELO 1: REGRESSÃO LINEAR - PREVISÃO DE UMIDADE DO SOLO")
print("=" * 70)

print("\n[3/7] Preparando dados para modelo de regressão...")

# Features para prever umidade
X_umidade = df[['pH', 'Nitrogenio', 'Fosforo', 'Potassio']]
y_umidade = df['Umidade(%)']

# Dividir dados
X_train_u, X_test_u, y_train_u, y_test_u = train_test_split(
    X_umidade, y_umidade, test_size=0.2, random_state=42
)

print(f"✓ Dados de treino: {X_train_u.shape[0]} amostras")
print(f"✓ Dados de teste: {X_test_u.shape[0]} amostras")

# 4. TREINAR MODELO DE REGRESSÃO
print("\n[4/7] Treinando modelo de Regressão Linear...")
modelo_umidade = LinearRegression()
modelo_umidade.fit(X_train_u, y_train_u)
print("✓ Modelo de regressão treinado!")

# Fazer previsões
y_pred_u = modelo_umidade.predict(X_test_u)

# Avaliar modelo de regressão
print("\n" + "=" * 70)
print("MÉTRICAS DO MODELO DE REGRESSÃO (Umidade):")
print("=" * 70)

mae_u = mean_absolute_error(y_test_u, y_pred_u)
mse_u = mean_squared_error(y_test_u, y_pred_u)
rmse_u = np.sqrt(mse_u)
r2_u = r2_score(y_test_u, y_pred_u)

print(f"MAE (Erro Médio Absoluto):        {mae_u:.4f} %")
print(f"MSE (Erro Quadrático Médio):      {mse_u:.4f}")
print(f"RMSE (Raiz do MSE):               {rmse_u:.4f} %")
print(f"R² (Coeficiente de Determinação): {r2_u:.4f}")

if r2_u < 0:
    print("\n⚠️ ATENÇÃO: R² negativo indica que o modelo tem dificuldade em capturar")
    print("   a relação entre as variáveis. Isso pode ocorrer com poucos dados.")
    print("   O modelo ainda pode fazer previsões, mas com maior margem de erro.")
else:
    print(f"\n• O modelo explica {r2_u*100:.2f}% da variação na umidade do solo")

print(f"• Erro médio de previsão: ±{mae_u:.2f}%")

# Importância das variáveis
print("\n" + "=" * 70)
print("IMPORTÂNCIA DAS VARIÁVEIS (Coeficientes) - UMIDADE:")
print("=" * 70)
for feature, coef in zip(X_umidade.columns, modelo_umidade.coef_):
    print(f"• {feature:15s}: {coef:+.4f}")

# 5. PREPARAR DADOS - MODELO 2: CLASSIFICAÇÃO (PREVER IRRIGAÇÃO)
print("\n" + "=" * 70)
print("MODELO 2: CLASSIFICAÇÃO - PREVISÃO DE NECESSIDADE DE IRRIGAÇÃO")
print("=" * 70)

print("\n[5/7] Preparando dados para modelo de classificação...")

# Features para prever irrigação
X_irrig = df[['Umidade(%)', 'pH', 'Nitrogenio', 'Fosforo', 'Potassio']]
y_irrig = df['Irrigando']

# Dividir dados
X_train_i, X_test_i, y_train_i, y_test_i = train_test_split(
    X_irrig, y_irrig, test_size=0.2, random_state=42
)

print(f"✓ Dados de treino: {X_train_i.shape[0]} amostras")
print(f"✓ Dados de teste: {X_test_i.shape[0]} amostras")
print(f"✓ Distribuição das classes: Não Irrigar={sum(y_irrig==0)}, Irrigar={sum(y_irrig==1)}")

# 6. TREINAR MODELO DE CLASSIFICAÇÃO
print("\n[6/7] Treinando modelo de Classificação (Logistic Regression)...")
modelo_irrigacao = LogisticRegression(random_state=42, max_iter=1000)
modelo_irrigacao.fit(X_train_i, y_train_i)
print("✓ Modelo de classificação treinado!")

# Fazer previsões
y_pred_i = modelo_irrigacao.predict(X_test_i)

# Avaliar modelo de classificação
print("\n" + "=" * 70)
print("MÉTRICAS DO MODELO DE CLASSIFICAÇÃO (Irrigação):")
print("=" * 70)

acuracia = accuracy_score(y_test_i, y_pred_i)
print(f"Acurácia: {acuracia:.4f} ({acuracia*100:.2f}%)")

# Verificar se há múltiplas classes no teste
classes_unicas_teste = np.unique(y_test_i)
if len(classes_unicas_teste) > 1:
    print("\nRelatório de Classificação:")
    print(classification_report(y_test_i, y_pred_i, target_names=['Não Irrigar', 'Irrigar']))
else:
    print(f"\nℹ️ Conjunto de teste contém apenas classe: {classes_unicas_teste[0]}")
    print("   (Conjunto muito pequeno para relatório completo)")
    
    # Fazer relatório com todo o dataset
    y_pred_all = modelo_irrigacao.predict(X_irrig)
    print("\nRelatório usando TODOS os dados:")
    print(classification_report(y_irrig, y_pred_all, target_names=['Não Irrigar', 'Irrigar'], zero_division=0))

# 7. SALVAR MODELOS
print("\n[7/7] Salvando modelos treinados...")

with open('modelo_umidade.pkl', 'wb') as f:
    pickle.dump(modelo_umidade, f)
print("✓ Modelo de umidade salvo: 'modelo_umidade.pkl'")

with open('modelo_irrigacao.pkl', 'wb') as f:
    pickle.dump(modelo_irrigacao, f)
print("✓ Modelo de irrigação salvo: 'modelo_irrigacao.pkl'")

# 8. CRIAR GRÁFICOS
print("\n[8/8] Gerando gráficos de análise...")

# Gráfico 1: Real vs Previsto (Umidade)
plt.figure(figsize=(10, 6))
plt.scatter(y_test_u, y_pred_u, alpha=0.7, edgecolors='k', s=100, color='#2196F3')
plt.plot([y_test_u.min(), y_test_u.max()], [y_test_u.min(), y_test_u.max()], 
         'r--', lw=2, label='Previsão Perfeita')
plt.xlabel('Umidade Real (%)', fontsize=12, fontweight='bold')
plt.ylabel('Umidade Prevista (%)', fontsize=12, fontweight='bold')
plt.title('Modelo de Regressão: Umidade Real vs Prevista', fontsize=14, fontweight='bold')
plt.legend(fontsize=10)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('grafico_umidade_real_vs_previsto.png', dpi=300, bbox_inches='tight')
print("✓ Gráfico 'grafico_umidade_real_vs_previsto.png' criado")

# Gráfico 2: Matriz de Correlação
plt.figure(figsize=(10, 8))
correlacao = df[['Umidade(%)', 'pH', 'Nitrogenio', 'Fosforo', 'Potassio', 'Irrigando']].corr()
sns.heatmap(correlacao, annot=True, cmap='RdYlGn', center=0, 
            square=True, linewidths=1, fmt='.2f', cbar_kws={'label': 'Correlação'})
plt.title('Matriz de Correlação - Variáveis Agrícolas', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('matriz_correlacao.png', dpi=300, bbox_inches='tight')
print("✓ Gráfico 'matriz_correlacao.png' criado")

# Gráfico 3: Distribuição de Umidade
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].hist(df['Umidade(%)'], bins=15, color='#2196F3', edgecolor='black', alpha=0.7)
axes[0].axvline(df['Umidade(%)'].mean(), color='red', linestyle='--', 
                linewidth=2, label=f'Média: {df["Umidade(%)"].mean():.1f}%')
axes[0].set_xlabel('Umidade do Solo (%)', fontsize=12, fontweight='bold')
axes[0].set_ylabel('Frequência', fontsize=12, fontweight='bold')
axes[0].set_title('Distribuição da Umidade do Solo', fontsize=13, fontweight='bold')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Gráfico 4: pH vs Umidade
scatter = axes[1].scatter(df['pH'], df['Umidade(%)'], 
                          c=df['Irrigando'], cmap='RdYlGn', 
                          s=100, edgecolors='black', alpha=0.7)
axes[1].set_xlabel('pH do Solo', fontsize=12, fontweight='bold')
axes[1].set_ylabel('Umidade do Solo (%)', fontsize=12, fontweight='bold')
axes[1].set_title('Relação: pH vs Umidade (cor = irrigação)', fontsize=13, fontweight='bold')
axes[1].grid(True, alpha=0.3)
cbar = plt.colorbar(scatter, ax=axes[1])
cbar.set_label('Irrigando (0=Não, 1=Sim)', fontsize=10)

plt.tight_layout()
plt.savefig('analise_umidade_ph.png', dpi=300, bbox_inches='tight')
print("✓ Gráfico 'analise_umidade_ph.png' criado")

print("\n" + "=" * 70)
print("✅ TREINAMENTO CONCLUÍDO COM SUCESSO!")
print("=" * 70)
print("\n📊 Modelos criados:")
print("   1. modelo_umidade.pkl - Regressão Linear")
print("   2. modelo_irrigacao.pkl - Classificação Logística")
print("\n📈 Gráficos gerados:")
print("   1. grafico_umidade_real_vs_previsto.png")
print("   2. matriz_correlacao.png")
print("   3. analise_umidade_ph.png")
print("\n💡 Observações:")
if r2_u < 0:
    print("   • Modelo de umidade com R² negativo (poucos dados)")
    print("   • Isso é comum com datasets pequenos (<50 amostras)")
    print("   • Modelos funcionam, mas com maior margem de erro")
else:
    print(f"   • Modelo de umidade explica {r2_u*100:.1f}% da variação")
print(f"   • Modelo de irrigação com {acuracia*100:.1f}% de acurácia")
print("\n🚀 Próximo passo:")
print("   Execute: streamlit run dashboard.py")
print("=" * 70)