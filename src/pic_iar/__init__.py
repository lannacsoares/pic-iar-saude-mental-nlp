"""PIC_PIBIC_11: deteccao de depressao e ansiedade em redes sociais (UniCEUB)."""

__version__ = "0.1.0"

# Modelos avaliados (ids no Hugging Face Hub).
MODELS = {
    "bertimbau": "neuralmind/bert-base-portuguese-cased",
    "xlmr": "FacebookAI/xlm-roberta-base",
    "mbert": "google-bert/bert-base-multilingual-cased",
}

SEED = 42
