# 🛡️ Pipeline de Engenharia de Dados: Análise de Ameaças Cibernéticas Globais

> **Pós-Graduação em Engenharia de Dados**  
> **Universidade de Fortaleza (UNIFOR)**  
> **Disciplina:** Tópicos Avançados em Engenharia de Dados  

---

## 📌 Sobre o Projeto

Este projeto consiste na implementação de uma **esteira completa de dados (End-to-End Data Pipeline)** para ingestão, processamento em streaming, armazenamento, análise exploratória e consulta orientada por Inteligência Artificial (NL2SQL).

O tema abordado é a **análise de ameaças cibernéticas globais (2015–2024)**, consumindo dados públicos do Kaggle, trafegando eventos via **Apache Kafka**, tratando e padronizando as mensagens em tempo real, persistindo em um banco relacional **SQLite** e disponibilizando interfaces analíticas via **Matplotlib** e **Streamlit integrado a LLM (OpenAI GPT-4o via LangChain)**.

---

## 🏛️ Arquitetura da Solução

O fluxo de dados segue uma arquitetura orientada a eventos e em camadas:

```
┌───────────────────────┐
│     Kaggle API        │  (Dataset: Global Cybersecurity Threats 2015-2024)
└──────────┬────────────┘
           │ Download & Leitura (01_ingestao.py)
           ▼
┌───────────────────────┐
│  Kafka: raw-data      │  (Mensageria / Tópico Bruto)
└──────────┬────────────┘
           │ Consumo, Limpeza e Validação (02_transformacao.py)
           ▼
┌───────────────────────┐
│Kafka: transformed-data│  (Mensageria / Tópico Tratado)
└──────────┬────────────┘
           │ Carga Contínua (03_carga.py)
           ▼
┌───────────────────────┐
│   SQLite Database     │  (data/insidentes.db)
└──────┬─────────┬──────┘
       │         │
       │         └─────────────────────────────────┐
       ▼                                           ▼
┌───────────────────────────┐         ┌───────────────────────────┐
│   04_consumo.py           │         │  app.py (Streamlit + LLM) │
│   (Dashboards Matplotlib) │         │  llm.py (CLI Text-to-SQL) │
└───────────────────────────┘         └───────────────────────────┘
```

---

## 🛠️ Tecnologias e Ferramentas

| Componente | Tecnologia | Finalidade |
| :--- | :--- | :--- |
| **Mensageria & Streaming** | Apache Kafka & Zookeeper (Confluent) | Transmissão de eventos em tempo real com desacoplamento de etapas |
| **Containerização** | Docker & Docker Compose | Orquestração local do broker Kafka e Zookeeper |
| **Linguagem & Processamento** | Python 3, Pandas, kafka-python | Ingestão, higienização, tipagem e enriquecimento dos registros |
| **Armazenamento** | SQLite | Armazenamento relacional estruturado dos incidentes tratados |
| **Visualização de Dados** | Matplotlib & Seaborn | Geração de gráficos analíticos de séries temporais, perdas e setores |
| **IA Generativa & NL2SQL** | LangChain & OpenAI (GPT-4o) | Conversão de perguntas em linguagem natural para consultas SQL |
| **Interface Web** | Streamlit | Dashboard interativo para o usuário realizar consultas com IA |

---

## 📁 Estrutura do Repositório

```bash
├── data/                    # Diretório local para armazenamento dos CSVs e banco SQLite
├── 01_ingestao.py           # Download do dataset Kaggle e publicação no tópico Kafka 'raw-data'
├── 02_transformacao.py      # Consumo do 'raw-data', limpeza, tradução/padronização e envio para 'transformed-data'
├── 03_carga.py              # Consumo do 'transformed-data' e persistência na tabela 'insidentes' do SQLite
├── 04_consumo.py            # Consultas analíticas SQL e geração de gráficos com Matplotlib
├── app.py                   # Aplicação web Streamlit com LangChain (consulta inteligente em linguagem natural)
├── llm.py                   # CLI interativa para consultas Text-to-SQL via terminal
├── docker-compose.yml       # Configuração dos serviços Zookeeper e Kafka
├── kaggle.json              # Credenciais de autenticação da Kaggle API
└── README.md                # Documentação técnica do trabalho
```

---

## 📊 Dataset Utilizado

* **Fonte:** [Global Cybersecurity Threats (2015-2024) - Kaggle](https://www.kaggle.com/datasets/atharvasoundankar/global-cybersecurity-threats-2015-2024)
* **Atributos Principais:**
  * `pais` (Country)
  * `ano` (Year)
  * `tipo_ataque` (Attack Type: Ransomware, Phishing, DDoS, etc.)
  * `industria_alvo` (Target Industry: Finance, Healthcare, Tech, etc.)
  * `perda_financeira_milhoes_usd` (Financial Loss in Million $)
  * `usuarios_afetados` (Number of Affected Users)
  * `origem_ataque` (Attack Source)
  * `tipo_vulnerabilidade` (Security Vulnerability Type)
  * `mecanismo_defesa` (Defense Mechanism Used)
  * `tempo_resolucao_horas` (Incident Resolution Time)

---

## 🚀 Como Executar o Projeto

### 1. Pré-requisitos
* [Docker](https://www.docker.com/) e Docker Compose instalados
* [Python 3.10+](https://www.python.org/)
* Chave de API da OpenAI (caso deseje utilizar a interface inteligente com LLM)
* Credenciais ativas do Kaggle (configuradas no `kaggle.json` ou variáveis de ambiente)

### 2. Instalação das Dependências

Crie e ative um ambiente virtual (recomendado):

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

Instale as bibliotecas necessárias:

```bash
pip install pandas kafka-python kaggle matplotlib streamlit langchain langchain-openai langchain-community langchain-experimental python-dotenv
```

### 3. Configuração de Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com sua chave da OpenAI:

```env
OPENAI_API_KEY=sua-chave-aqui
```

### 4. Inicialização dos Serviços (Docker)

Suba os contêineres do **Zookeeper** e **Kafka**:

```bash
docker-compose up -d
```

Verifique se os contêineres estão em execução:

```bash
docker ps
```

---

### 5. Execução do Pipeline

Execute os scripts na ordem estabelecida pela esteira de dados:

#### Passo 1: Ingestão de Dados
Baixa o dataset do Kaggle e envia os eventos brutos para o Kafka:
```bash
python 01_ingestao.py
```

#### Passo 2: Transformação em Tempo Real
Lê os dados do tópico `raw-data`, higieniza, valida atributos essenciais e publica no tópico `transformed-data`:
```bash
python 02_transformacao.py
```

#### Passo 3: Carga no Banco de Dados
Consome os dados transformados e persiste no banco SQLite `data/insidentes.db`:
```bash
python 03_carga.py
```

---

### 6. Consumo e Visualização

#### Opção A: Gráficos e Estatísticas (Matplotlib)
Gera uma visão geral em 4 gráficos analíticos (Top 10 perdas financeiras por país, tempo médio de resolução, indústrias mais visadas e evolução temporal):
```bash
python 04_consumo.py
```

#### Opção B: Interface Web com Consulta Inteligente (Streamlit + LLM)
Inicia uma aplicação web onde é possível realizar perguntas em português (e.g., *"Quais os 5 países com maiores prejuízos financeiros?"*) e obter a resposta gerada dinamicamente via consulta SQL:
```bash
streamlit run app.py
```

#### Opção C: Consulta via Terminal (CLI LLM)
```bash
python llm.py
```

---

## 🎯 Conclusão e Destaques do Trabalho

1. **Desacoplamento e Escalabilidade:** Uso do Kafka como espinha dorsal de mensageria, garantindo que etapas de ingestão, transformação e carga possam escalar de forma independente.
2. **Qualidade dos Dados:** Validação de esquemas e descarte de dados inconsistentes antes da persistência analítica.
3. **Inovação com IA Generativa (Text-to-SQL):** Democratização do acesso aos dados analíticos ao permitir que usuários de negócio façam perguntas em linguagem natural que são convertidas em consultas SQL validadas pelo LangChain.

---

## 👨‍💻 Autoria

* **Instituição:** Universidade de Fortaleza (UNIFOR)
* **Curso:** Pós-Graduação em Engenharia de Dados
* **Disciplina:** Tópicos Avançados em Engenharia de Dados

