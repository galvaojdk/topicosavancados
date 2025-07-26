from kafka import KafkaConsumer
import json
import sqlite3
import os

# Configurações
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'
TOPICO = 'transformed-data'
DB_PATH = 'data/insidentes.db'
TABELA = 'insidentes'

# Inicializa consumidor Kafka
consumer = KafkaConsumer(
    TOPICO,
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='carga',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    consumer_timeout_ms=5000  # Finaliza após 5s sem mensagens
)

# Garante que diretório 'data' exista
os.makedirs('data', exist_ok=True)

# Conecta ao banco SQLite
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Cria tabela se não existir
cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS {TABELA} (
        pais TEXT,
        ano INTEGER,
        tipo_ataque TEXT,
        industria_alvo TEXT,
        perda_financeira_milhoes_usd REAL,
        usuarios_afetados INTEGER,
        origem_ataque TEXT,
        tipo_vulnerabilidade TEXT,
        mecanismo_defesa TEXT,
        tempo_resolucao_horas REAL
    )
''')
conn.commit()

print("📥 Aguardando mensagens de 'transformed-data'...")

# Processamento das mensagens
contador = 0
for mensagem in consumer:
    dados = mensagem.value

    try:
        cursor.execute(f'''
            INSERT INTO {TABELA} (
                pais, ano, tipo_ataque, industria_alvo,
                perda_financeira_milhoes_usd, usuarios_afetados,
                origem_ataque, tipo_vulnerabilidade, mecanismo_defesa, tempo_resolucao_horas
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            dados['pais'],
            dados['ano'],
            dados['tipo_ataque'],
            dados['industria_alvo'],
            dados['perda_financeira_milhoes_usd'],
            dados['usuarios_afetados'],
            dados['origem_ataque'],
            dados['tipo_vulnerabilidade'],
            dados['mecanismo_defesa'],
            dados['tempo_resolucao_horas']
        ))

        contador += 1

    except Exception as e:
        print(f"❌ Erro ao inserir no banco: {e}")

conn.commit()
conn.close()

print(f"\n✅ {contador} registros inseridos no banco SQLite '{DB_PATH}'")
