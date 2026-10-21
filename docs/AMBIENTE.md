# Ambiente de desenvolvimento: PIC_PIBIC_11

Proposta de ambiente para o projeto *Detecção de Depressão e Ansiedade em Redes Sociais:
Evoluindo do Aprendizado de Máquina Clássico para Modelos de Linguagem de Grande Escala*
(Edital PIC IA e Robótica 2026, UniCEUB). Versões verificadas em 21/10/2026.

## 1. Visão geral: três ambientes, um lockfile

O pré-projeto usa três lugares de execução. A estratégia é manter **um único conjunto de
versões** (`requirements.lock.txt`) para tudo que roda fora do Databricks, e só ajustar o mínimo
no cluster.

| Ambiente | Para quê | Quem | Arquivo |
|---|---|---|---|
| Local (Linux/macOS/WSL2) | Desenvolvimento, EDA, baselines clássicos, testes, API | Lanna | `requirements-dev.txt` |
| Google Colab Pro (T4/A100) | Plano B de GPU, prototipagem | Lanna | `requirements.txt` (sem a linha `torch`) |
| Databricks (A10/H100, UniCEUB) | Pré-processamento em Spark, fine-tuning, MLflow, Delta Lake | Lanna | `requirements-databricks.txt` |

## 2. Versões recomendadas

| Componente | Versão | Por quê |
|---|---|---|
| Python | **3.12** | Denominador comum seguro: suportado por todas as bibliotecas abaixo e pelos runtimes recentes do Databricks. Existem 3.13 e 3.14, mas não trazem ganho para este projeto. |
| PyTorch | **2.9.0** | Mesma versão do Databricks Runtime 18.2 ML (CUDA 12.9). Há torch 2.12, mas ele migrou os wheels padrão para CUDA 13; sem benefício para modelos base. |
| Transformers | **4.57.6** | Última da série 4.x e a mesma linha do Runtime 18.2 ML. A série 5.x (atual: 5.20) removeu `tokenizer=` do `Trainer`. Veja a seção 5. |
| tokenizers / huggingface_hub | 0.22.2 / 0.36.2 | Exigidos por transformers 4.57. |
| datasets | 5.0.1 | Pipeline de dados em formato Arrow. |
| accelerate | 1.15.0 | Necessário para o `Trainer` com bf16/fp16 e multi-GPU. |
| scikit-learn | 1.9.1 | Baselines SVM+TF-IDF, SVM+BoW e Random Forest. |
| numpy / scipy | 2.5.4 / 1.18.1 | |
| pandas | **2.3.3** (fixado em `<3`) | O Databricks usa 2.2.x. O pandas 3 muda o dtype de strings e pode divergir entre ambientes. |
| statsmodels | 0.15.0 | Teste de McNemar (`mcnemar`). |
| fairlearn | 0.15.0 | `equalized_odds_difference`, `demographic_parity_difference`. |
| mlflow / wandb | 3.17.2 / 0.31.0 | Rastreamento de experimentos (o pré-projeto prevê os dois). |
| emoji, ftfy | 2.16.0 / 6.3.1 | Pré-processamento: emojis e normalização de encoding. |
| sentencepiece, protobuf | 0.2.2 / 7.36.2 | Tokenizador do XLM-RoBERTa. |
| FastAPI / Uvicorn / Pydantic | 0.156.4 / 0.54.0 / 2.14.1 | API REST (Fase 4). |
| pytest / ruff / jupyterlab | 9.1.1 / 0.17.1 / 4.6.4 | Qualidade e notebooks. |

As versões foram resolvidas juntas (`uv pip compile`, Python 3.12, Linux x86_64) sem conflito.
A instalação completa com GPU **não** foi executada na preparação deste repositório; rode
`python scripts/check_env.py` após instalar.

## 3. Databricks

- **Runtime recomendado: 17.3 LTS ML (GPU)**: torch 2.7.0, CUDA 12.6, transformers 4.51.3. É LTS,
  então se mantém estável até o fim do projeto (jul/2027). Instale só o delta de
  `requirements-databricks.txt` (transformers, tokenizers, huggingface_hub, fairlearn…). **Não
  reinstale o torch no cluster.**
- **Alternativa: 18.2 ML**: já traz torch 2.9.0 e transformers 4.57.1, exatamente a pilha deste
  repositório. Confirme no CloudLabs qual runtime está liberado e se ele tem suporte até jul/2027.
- Pré-processamento em Spark e Delta Lake já vêm no runtime; não há necessidade de instalar
  `pyspark`/`delta-spark` localmente (se precisar testar Spark local, instale à parte).
- MLflow é nativo do Databricks; no `TrainingArguments` use `report_to=["mlflow", "wandb"]`.

## 4. GPU e memória (orientação aproximada)

- **A10 (24 GB) e H100**: use `bf16=True`. BERTimbau-base e mBERT cabem com batch 32.
  XLM-RoBERTa-base (270M, vocabulário grande) pode precisar de batch 16 com
  `gradient_accumulation_steps=2` para manter batch efetivo de 32.
- **T4 (Colab)**: não tem bf16; use `fp16=True`, batch 16 e acumulação.
- **Padding dinâmico** (`DataCollatorWithPadding`): tweets têm cerca de 12 palavras em média
  (ex.: DepressBR, Santos et al. 2020), então truncar em 512 quase nunca ocorre e preencher tudo
  até 512 desperdiça computação. O truncamento fica como salvaguarda.
- Para CPU/macOS (sem CUDA) tudo funciona para baselines e testes; o fine-tuning é impraticável.

## 5. Decisões que valem registrar

1. **`tokenizer=` → `processing_class=`** e **`evaluation_strategy` → `eval_strategy`**: use os
   nomes novos desde já; eles funcionam em transformers 4.57 e em 5.x, e a migração futura fica
   trivial.
2. **Reprodutibilidade**: `set_seed(42)` do `transformers`, seeds fixas nos folds, e logue o hash
   de `requirements.lock.txt` e o `pip freeze` como artefato no MLflow/W&B de cada execução.
3. **Mesma pilha para os experimentos finais**: baselines clássicos (scikit-learn 1.9.1) e
   transformers devem rodar com as versões do lockfile; o Databricks traz scikit-learn 1.6.1,
   então rode os baselines fora do cluster ou instale a versão do lockfile.
4. **Segredos**: tokens de Hugging Face, W&B e Databricks só em `.env` (ignorado pelo Git) ou nos
   *secrets* do Databricks.
5. **Dados fora do Git**: ver `data/README.md`.

## 6. Pontos a decidir com o orientador

- **Atributos demográficos para a análise de viés.** `equalized_odds` e `demographic_parity`
  exigem um atributo sensível por registro, e os corpora de tweets listados no pré-projeto não
  trazem metadados demográficos. É preciso definir de onde virão (inferência, subconjunto
  anotado, outra fonte) ou ajustar a metodologia.
- **Runtime do Databricks** (17.3 LTS vs 18.2) e a data de fim de suporte em relação a jul/2027.
- **Licença** do repositório (o pré-projeto prevê MIT na publicação da API).

## 7. VS Code e Windows

O VS Code é só o editor e o cliente do notebook: o desempenho vem de **onde o kernel roda**,
não do editor. Não há perda de desempenho por usá-lo no lugar do JupyterLab.

**Extensões**: Python, Jupyter, Pylance e Ruff (Microsoft/Astral); *Databricks* (para o
cluster) e *Google Colab* (para GPU do Colab). Selecione o interpretador do ambiente fora do
OneDrive (`Ctrl+Shift+P` → *Python: Select Interpreter*) e use o mesmo como kernel do notebook.

**Onde rodar cada tarefa**

| Tarefa | Onde | Observação |
|---|---|---|
| EDA, pré-processamento leve, baselines clássicos, testes, API | Local (VS Code) | CPU basta. |
| Prototipagem e fine-tuning pequeno | GPU local ou Colab | Extensão do Colab liga o `.ipynb` local a um runtime do Colab; GPUs premium exigem Colab Pro. |
| Pré-processamento em Spark | Databricks Connect (VS Code) | Só operações de DataFrame rodam no cluster (exige Databricks Runtime ≥ 13.3). |
| Fine-tuning e grid search no A10/H100 | Notebook ou job **no próprio Databricks** | Na extensão do VS Code, "todo o código roda localmente, exceto operações de DataFrame": um `Trainer` do PyTorch numa célula usaria a máquina local, **não** a GPU do cluster. |

**Limitações práticas**

- **GPU do notebook:** verifique com `nvidia-smi`. Com 6 GB de VRAM, BERTimbau e mBERT cabem com
  `fp16`, batch pequeno e `gradient_accumulation_steps`; o XLM-RoBERTa-base (270M) pode não
  caber, então rode-o no Colab ou no Databricks.
- **Treino longo em script, não em célula:** notebook morre se o computador hibernar ou o VS Code
  fechar. Rode o grid search como script (`python -m ...`) com logs no MLflow/W&B.
- **Saída de célula:** barras de progresso e prints grandes deixam o notebook lento. Use
  `tqdm.auto` e registre métricas no W&B em vez de imprimir.
- **Windows:** use `dataloader_num_workers=0` em notebooks (multiprocessamento usa *spawn*);
  scripts precisam de `if __name__ == "__main__":`; evite `torch.compile` e `flash-attn`
  (sem suporte oficial no Windows) e não use `make` (sem ele, rode os comandos do README).
- **PyTorch no Windows:** o `pip install torch` padrão instala a versão **CPU**. Instale com o
  índice CUDA (README, passo 2). Requer driver NVIDIA recente (`nvidia-smi`).
- **OneDrive:** mantenha `.venv`, `data/` e checkpoints fora da pasta sincronizada.

## 8. API REST (Fase 4, mar–abr/2027)

Para a imagem Docker use `python:3.12-slim` e instale o torch **CPU** (índice
`https://download.pytorch.org/whl/cpu`), o que reduz a imagem de vários GB para algumas centenas
de MB. Dependências em `requirements-api.txt`.
