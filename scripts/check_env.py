#!/usr/bin/env python
"""Verifica se o ambiente atual corresponde ao esperado pelo projeto.

Uso:
    python scripts/check_env.py

Imprime versões de Python, bibliotecas e GPU, e compara com os pins de
requirements.txt. Sai com código 1 se houver biblioteca ausente ou divergente
(divergências de versão só geram aviso quando --lenient é passado).
"""

from __future__ import annotations

import argparse
import platform
import re
import sys
from importlib import metadata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPECTED_PYTHON = (3, 12)


def parse_pins(path: Path) -> dict[str, str]:
    pins: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        m = re.match(r"^([A-Za-z0-9_.\-]+)(?:\[.*?\])?==(\S+)$", line)
        if m:
            pins[m.group(1).lower().replace("_", "-")] = m.group(2)
    return pins


def installed(name: str) -> str | None:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return None


def gpu_report() -> None:
    try:
        import torch
    except ImportError:
        print("\n[GPU] torch não instalado.")
        return
    print(f"\n[GPU] torch {torch.__version__} | CUDA build: {torch.version.cuda}")
    if not torch.cuda.is_available():
        print("[GPU] Nenhuma GPU CUDA disponível (treino será em CPU; ok para baselines).")
        return
    for i in range(torch.cuda.device_count()):
        props = torch.cuda.get_device_properties(i)
        mem_gib = props.total_memory / 2**30
        print(f"[GPU] {i}: {props.name} | {mem_gib:.1f} GiB | sm_{props.major}{props.minor}")
    print(f"[GPU] bf16 suportado: {torch.cuda.is_bf16_supported()}  (use fp16 se False, ex.: T4)")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lenient", action="store_true", help="divergência de versão vira aviso")
    args = parser.parse_args()

    print(f"Python {platform.python_version()} em {platform.platform()}")
    if sys.version_info[:2] != EXPECTED_PYTHON:
        print(f"AVISO: o projeto foi fixado em Python {EXPECTED_PYTHON[0]}.{EXPECTED_PYTHON[1]}.")

    pins = parse_pins(ROOT / "requirements.txt")
    problems = 0
    print(f"\n{'pacote':<18}{'esperado':<12}{'instalado':<12}status")
    for name, want in sorted(pins.items()):
        have = installed(name)
        if have is None:
            status, problems = "AUSENTE", problems + 1
        elif have.split("+")[0] != want:
            status = "DIVERGE"
            problems += 0 if args.lenient else 1
        else:
            status = "ok"
        print(f"{name:<18}{want:<12}{have or '-':<12}{status}")

    gpu_report()
    summary = "ambiente OK" if problems == 0 else f"{problems} problema(s) encontrado(s)"
    print("\nResultado:", summary)
    return 0 if problems == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
