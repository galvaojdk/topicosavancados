import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Conectar ao banco SQLite
conn = sqlite3.connect('data/insidentes.db')

# 1. Perda financeira total por país (Top 10)
df1 = pd.read_sql_query("""
    SELECT pais, 
           ROUND(SUM(perda_financeira_milhoes_usd), 2) AS perda_total
    FROM insidentes
    WHERE perda_financeira_milhoes_usd IS NOT NULL
    GROUP BY pais
    ORDER BY perda_total DESC
    LIMIT 10
""", conn)

# 2. Tempo médio de resolução por tipo de ataque (Top 10)
df2 = pd.read_sql_query("""
    SELECT tipo_ataque, 
           ROUND(AVG(tempo_resolucao_horas), 1) AS tempo_medio
    FROM insidentes
    WHERE tempo_resolucao_horas IS NOT NULL
    GROUP BY tipo_ataque
    ORDER BY tempo_medio DESC
    LIMIT 10
""", conn)

# 3. Indústrias mais visadas (Top 10)
df3 = pd.read_sql_query("""
    SELECT industria_alvo, 
           COUNT(*) AS ocorrencias
    FROM insidentes
    WHERE industria_alvo IS NOT NULL
    GROUP BY industria_alvo
    ORDER BY ocorrencias DESC
    LIMIT 10
""", conn)

# 4. Evolução anual de ataques
df4 = pd.read_sql_query("""
    SELECT ano, COUNT(*) AS ataques
    FROM insidentes
    WHERE ano IS NOT NULL
    GROUP BY ano
    ORDER BY ano
""", conn)

conn.close()

# Visualização
fig, axs = plt.subplots(2, 2, figsize=(16, 10))

# Gráfico 1: Perda por país
axs[0, 0].barh(df1['pais'], df1['perda_total'], color='darkred')
axs[0, 0].set_title('💸 Perda Financeira por País (Top 10)')
axs[0, 0].set_xlabel('Perda Total (Milhões USD)')
axs[0, 0].invert_yaxis()

# Gráfico 2: Tempo médio por tipo de ataque
axs[0, 1].bar(df2['tipo_ataque'], df2['tempo_medio'], color='seagreen')
axs[0, 1].set_title('⏱️ Tempo Médio de Resolução por Tipo de Ataque')
axs[0, 1].set_ylabel('Horas')
axs[0, 1].tick_params(axis='x', labelrotation=45)

# Gráfico 3: Indústrias mais visadas
axs[1, 0].bar(df3['industria_alvo'], df3['ocorrencias'], color='steelblue')
axs[1, 0].set_title('🏭 Indústrias Mais Visadas (Top 10)')
axs[1, 0].tick_params(axis='x', labelrotation=45)

# Gráfico 4: Evolução anual
axs[1, 1].plot(df4['ano'], df4['ataques'], marker='o', linestyle='-', color='orange')
axs[1, 1].set_title('📈 Evolução Anual de Ataques Cibernéticos')
axs[1, 1].set_xlabel('Ano')
axs[1, 1].set_ylabel('Número de Ataques')

plt.tight_layout()
plt.show()
