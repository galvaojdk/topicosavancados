import os
import json
import pandas as pd
from pathlib import Path
from kafka import KafkaProducer

# === 1. Configuração manual das credenciais ===
KAGGLE_USERNAME = "galvaojdk"
KAGGLE_KEY = "545542da37e3a308c9f74f127aa6437e"

# === 2. Caminhos ===
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# === 3. Kafka ===
KAFKA_TOPIC = 'raw-data'
KAFKA_SERVERS = ['localhost:9092']

def setup_kaggle():
    os.environ["KAGGLE_USERNAME"] = KAGGLE_USERNAME
    os.environ["KAGGLE_KEY"] = KAGGLE_KEY

def download_dataset():
    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()
    
    print("📥 Baixando dataset do Kaggle...")
    api.dataset_download_files(
        "atharvasoundankar/global-cybersecurity-threats-2015-2024",
        path=DATA_DIR,
        unzip=True,
        force=True
    )
    print("✅ Download concluído!")

def load_data():
    csv_files = list(DATA_DIR.glob("*.csv"))
    if not csv_files:
        print("❌ Nenhum CSV encontrado após o download.")
        return None
    
    print(f"🔍 CSV encontrado: {csv_files[0].name}")
    return pd.read_csv(csv_files[0])

def produce_to_kafka(df):
    print(f"🚀 Enviando dados para Kafka ({KAFKA_TOPIC})...")
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    for _, row in df.iterrows():
        message = row.to_dict()
        producer.send(KAFKA_TOPIC, message)
    producer.flush()
    print("✅ Dados enviados com sucesso!")

if __name__ == "__main__":
    print("=== Iniciando ingestão ===")
    
    setup_kaggle()
    download_dataset()
    df = load_data()

    if df is not None:
        print(df.head())
        produce_to_kafka(df)
