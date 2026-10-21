# PIC-IAR: Detecção de depressão e ansiedade em redes sociais

**PIC_PIBIC_11** · Edital PIC IA e Robótica 2026 · Ciência da Computação (UniCEUB)
Cronograma: agosto/2026 a julho/2027

Pesquisa que compara abordagens clássicas de PLN (SVM + TF-IDF/BoW, Random Forest) com modelos
transformer ajustados (BERTimbau, XLM-RoBERTa, mBERT) para detectar sofrimento psíquico em
postagens de redes sociais em português, com análise de viés e uma API REST de código aberto.

- Orientador: Salvador Alves de Melo Junior
- Aluna: Lanna Corrêa Soares (bolsista, responsável por todas as frentes do projeto)

## Início rápido (local)

```bash
# 1. Ambiente (Python 3.12) com uv: https://docs.astral.sh/uv/
uv venv --python 3.12
source .venv/bin/activate

# 2. Dependências (núcleo + API + ferramentas de dev) e o pacote em modo editável
uv pip install -r requirements-dev.txt
uv pip install -e .

# 3. Confira o ambiente (versões, GPU, bf16)
python scripts/check_env.py
```

Sem `uv`: `python3.12 -m venv .venv && source .venv/bin/activate && pip install -r requirements-dev.txt`.

- **Google Colab**: `grep -v '^torch' requirements.txt > /tmp/req.txt && pip install -r /tmp/req.txt`
  (mantém o torch que o Colab já traz).
- **Databricks**: veja `requirements-databricks.txt` e `docs/AMBIENTE.md`.

Para configurar tokens (Hugging Face, W&B), copie `.env.example` para `.env`.

## Estrutura

```
configs/      parâmetros de referência do experimento (experiment.yaml)
data/         dados locais (NÃO versionados; ver data/README.md)
docs/         AMBIENTE.md: proposta completa do ambiente e decisões
notebooks/    exploração e análises
scripts/      utilitários (check_env.py)
src/pic_iar/  código do projeto
tests/        testes
api/          API REST FastAPI (Fase 4)
```

## Arquivos de dependências

| Arquivo | Conteúdo |
|---|---|
| `requirements.txt` | Núcleo do experimento (versões fixadas) |
| `requirements-api.txt` | + FastAPI/Uvicorn/Pydantic |
| `requirements-dev.txt` | + pytest, ruff, JupyterLab |
| `requirements.lock.txt` | Lock completo (Python 3.12, Linux x86_64) |
| `requirements.in` | Fonte do lock |
| `requirements-databricks.txt` | Ajustes para o cluster Databricks |

## Dados e ética

Somente dados públicos e previamente anonimizados; resultados sempre agregados. Nenhum dado é
versionado neste repositório (LGPD, Lei 13.709/2018; CEP/CEUB, Res. CNS 466/2012).

## Licença

A definir (o pré-projeto prevê MIT na publicação da API).
