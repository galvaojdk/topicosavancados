from kafka import KafkaConsumer, KafkaProducer
import json

# Configurações
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'
TOPICO_ENTRADA = 'raw-data'
TOPICO_SAIDA = 'transformed-data'

# Inicializa consumidor Kafka com timeout
consumer = KafkaConsumer(
    TOPICO_ENTRADA,
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='transformador',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    consumer_timeout_ms=5000
)

# Inicializa produtor Kafka
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

print("🚀 Processando mensagens do tópico 'raw-data'...")

contador = 0
descartados = 0

for mensagem in consumer:
    dado = mensagem.value

    try:
        transformado = {
            'pais': dado.get('Country'),
            'ano': int(dado.get('Year')) if str(dado.get('Year')).isdigit() else None,
            'tipo_ataque': dado.get('Attack Type'),
            'industria_alvo': dado.get('Target Industry'),
            'perda_financeira_milhoes_usd': float(dado.get('Financial Loss (in Million $)', 0)) if dado.get('Financial Loss (in Million $)') not in [None, '', 'NA'] else None,
            'usuarios_afetados': int(float(dado.get('Number of Affected Users', 0))) if dado.get('Number of Affected Users') not in [None, '', 'NA'] else None,
            'origem_ataque': dado.get('Attack Source'),
            'tipo_vulnerabilidade': dado.get('Security Vulnerability Type'),
            'mecanismo_defesa': dado.get('Defense Mechanism Used'),
            'tempo_resolucao_horas': float(dado.get('Incident Resolution Time (in Hours)', 0)) if dado.get('Incident Resolution Time (in Hours)') not in [None, '', 'NA'] else None
        }

        # Validação mínima: país, ano e tipo de ataque devem existir
        if not all([transformado['pais'], transformado['ano'], transformado['tipo_ataque']]):
            descartados += 1
            continue

        producer.send(TOPICO_SAIDA, transformado)
        contador += 1
        print(f"✅ Transformado [{contador}]: {transformado['pais']} ({transformado['ano']})")

    except Exception as e:
        descartados += 1
        print(f"❌ Erro ao transformar mensagem: {e}")

producer.flush()
print(f"\n🏁 Fim do processamento.")
print(f"✅ {contador} mensagens transformadas e enviadas")
print(f"⚠️ {descartados} mensagens descartadas por dados inválidos")
