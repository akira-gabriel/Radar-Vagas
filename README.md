# Radar-Vagas 📡

Pipeline de coleta, tratamento e enriquecimento de **vagas de emprego na área de dados**, a partir da [API da Adzuna](https://developer.adzuna.com/). Segue a arquitetura **medallion** (bronze → silver), com uma camada de enriquecimento via LLM (Groq) para extração automática de skills.

## Arquitetura

```
Adzuna API  ──►  bronze (raw .jsonl)  ──►  silver (parquet limpo)  ──►  enrich (skills via LLM)
```

| Camada | Notebook | O que faz | Saída |
|--------|----------|-----------|-------|
| 🥉 **bronze** | `bronze/extract.ipynb` | Consulta a API da Adzuna (vagas de "dados" no Brasil) e salva a resposta crua, uma requisição por linha | `bronze/data/<dd_mm_aaaa__hh_mm>.jsonl` |
| 🥈 **silver** | `silver/transform.ipynb` | Normaliza o JSON, remove duplicatas por `id`, descarta colunas irrelevantes e renomeia campos | `silver/data/data.parquet` |
| ✨ **enrich** | `silver/enrich.ipynb` | Usa a Groq (API compatível com OpenAI) para extrair as skills de cada vaga, classificando-as em obrigatórias, desejáveis ou não especificadas *(em construção)* | — |

## Detalhes de cada etapa

### 🥉 bronze — extração
- Fonte: `https://api.adzuna.com/v1/api/jobs/br/search/` com `what=dados`.
- Coleta **5 páginas × 20 resultados** por execução (~100 vagas).
- Cada run gera um `.jsonl` novo, nomeado com o timestamp da coleta — preservando o histórico bruto.

### 🥈 silver — transformação
- Lê todos os `.jsonl` da camada bronze e explode `results` em um DataFrame (`json_normalize`).
- Remove duplicatas por `id` (mantém a ocorrência mais recente).
- Renomeia campos para nomes mais limpos: `created → collected_at`, `redirect_url → url`, `company.display_name → company`, `location.display_name → location`, etc.
- Persiste em **Parquet** (via PyArrow).

### ✨ enrich — enriquecimento com LLM *(WIP)*
- Modelo: `openai/gpt-oss-20b` na Groq, via cliente OpenAI (`base_url` da Groq).
- Usa **structured output** (JSON Schema) para devolver uma lista de skills, cada uma classificada como:
  - `Obrigatorio`
  - `Desejado/Diferencial`
  - `Não especificado`
- Importa `psycopg2`, sinalizando carga futura em **PostgreSQL**.

## Setup

```bash
# ambiente virtual (já existe .venv na pasta Python pai)
python -m venv .venv && source .venv/bin/activate

# dependências
pip install requests python-dotenv pandas pyarrow groq openai psycopg2-binary
```

Crie um arquivo `.env` na raiz com:

```env
api_ID=<seu_app_id_da_adzuna>
api_key=<sua_app_key_da_adzuna>
GROQ_API_KEY=<sua_chave_groq>
```

> As credenciais da Adzuna saem do [portal de desenvolvedores](https://developer.adzuna.com/); a chave da Groq, do [console da Groq](https://console.groq.com/).

## Como rodar

1. Execute `bronze/extract.ipynb` para coletar uma nova leva de vagas.
2. Execute `silver/transform.ipynb` para consolidar e limpar em Parquet.
3. Execute `silver/enrich.ipynb` para extrair as skills *(quando finalizado)*.

## Roadmap / pendências

- [ ] Finalizar a chamada da Groq em `enrich.ipynb` (hoje está comentada) e corrigir a célula `print(vagas.)`.
- [ ] Alinhar o caminho de leitura da transform: o notebook lê de `../bronze/data/records/`, mas os `.jsonl` estão em `../bronze/data/`.
- [ ] Persistir o resultado enriquecido no PostgreSQL (`psycopg2` já importado).
- [ ] Parametrizar a busca (`what`, país, nº de páginas) em vez de hardcode.
- [ ] Agendar a coleta (cron) para acompanhar o mercado ao longo do tempo.

## Stack

`Python` · `Adzuna API` · `pandas` · `PyArrow/Parquet` · `Groq (LLM)` · `PostgreSQL` · Jupyter
