import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain.prompts import PromptTemplate

# 1. Carrega variáveis do .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# 2. Conecta ao banco SQLite
db_path = Path("data/insidentes.db").resolve()
db = SQLDatabase.from_uri(f"sqlite:///{db_path}")
llm = ChatOpenAI(temperature=0, model="gpt-4o", api_key=api_key)

# 3. Prompt customizado para SQL puro
prompt = PromptTemplate.from_template("""
Você é um assistente que gera apenas código SQL puro.
NÃO inclua blocos como ```sql ou ```.

Base de dados:
{table_info}

Pergunta:
{input}

SQLQuery:
""")

# 4. Cadeia LangChain para gerar a SQL
db_chain = SQLDatabaseChain.from_llm(
    llm=llm,
    db=db,
    prompt=prompt,
    return_intermediate_steps=True,
    verbose=False
)

# 5. Interface Streamlit
st.set_page_config(page_title="Consulta Inteligente", layout="wide")
st.title("🔍 Consulta Inteligente ao Banco de Dados")

pergunta = st.text_input("Digite sua pergunta:", placeholder="Ex: quais os países com maior número de ataques?")

if st.button("Consultar") and pergunta.strip():
    with st.spinner("Consultando LLM e banco de dados..."):
        try:
            resposta = db_chain.invoke(pergunta)

            # Extrai SQL gerado e limpa blocos markdown
            sql_gerado = ""
            for step in resposta["intermediate_steps"]:
                if isinstance(step, str) and "SELECT" in step.upper():
                    sql_gerado = step.strip().replace("```sql", "").replace("```", "")
                    break

            if sql_gerado:
                st.markdown("📄 **SQL gerado:**")
                st.code(sql_gerado, language="sql")

                # Executa a query no banco real
                resultado = db.run(sql_gerado)
                st.markdown("**📊 Resultado:**")
                st.text(resultado)
            else:
                st.warning("⚠️ Nenhuma query SQL foi identificada.")

        except Exception as e:
            st.error(f"❌ Erro ao processar consulta: {e}")
