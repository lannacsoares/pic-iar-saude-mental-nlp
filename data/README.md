# Dados

Esta pasta **nao deve conter dados versionados no Git**. Os corpora de saude mental sao
sensiveis (LGPD, Lei 13.709/2018; submissao ao CEP/CEUB, Resolucao CNS 466/2012), e as
licencas de varios datasets nao permitem redistribuicao.

- `raw/`: dados originais baixados das fontes (Casani et al. 2021, Kaggle, Hugging Face).
- `processed/`: saidas do pre-processamento (Arrow/Parquet).

No Databricks, o corpus consolidado e versionado em Delta Lake, nao aqui.

Registre a origem, o volume real e a licenca de cada fonte ingerida em
`docs/CORPUS.md` (criar quando o primeiro dataset for baixado).
