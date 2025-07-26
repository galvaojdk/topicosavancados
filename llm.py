import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain.prompts import PromptTemplate

# 1. Carrega variáveis do .env
load_dotenv()

# 2. Verifica e usa a chave da OpenAI
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ OPENAI_API_KEY não definida. Configure no .env ou no ambiente.")

# 3. Caminho absoluto do banco SQLite
db_path = Path("data/insidentes.db").resolve()
db = SQLDatabase.from_uri(f"sqlite:///{db_path}")

# 4. Inicializa modelo GPT-4o com chave explícita
llm = ChatOpenAI(temperature=0, model="gpt-4o", api_key=api_key)

# 5. Prompt com variáveis exigidas (input, table_info, top_k)
custom_prompt = PromptTemplate.from_template("""
Você é um assistente que gera apenas código SQL puro.
NÃO inclua blocos como ```sql ou ```.

Base de dados:
{table_info}

Pergunta:
{input}

Número máximo de resultados: {top_k}

SQLQuery:
""")

# 6. Cria a cadeia completa com prompt
db_chain = SQLDatabaseChain.from_llm(
    llm=llm,
    db=db,
    prompt=custom_prompt,
    return_intermediate_steps=True,
    verbose=True
)

# 7. Interface interativa
print("🧠 Assistente LLM conectado ao banco SQLite.")
print("Digite sua pergunta ou 'sair' para encerrar.\n")

while True:
    pergunta = input("Pergunta: ")
    if pergunta.lower() in ["sair", "exit", "quit"]:
        print("👋 Encerrando...")
        break
    try:
        resposta = db_chain.invoke(pergunta)
        print("\n📊 Resposta:\n", resposta['result'], "\n")
    except Exception as e:
        print(f"❌ Erro ao processar consulta: {e}")
