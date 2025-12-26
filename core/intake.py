# core/intake.py

import pandas as pd
import json
import re


def _normalize_column(col: str) -> str:
    """
    Normalize column names safely:
    - strip whitespace
    - collapse multiple spaces
    - remove hidden unicode spaces
    - lowercase
    """
    col = col.replace("\u00a0", " ")      # non-breaking space
    col = col.replace("\n", " ")
    col = re.sub(r"\s+", " ", col)
    return col.strip().lower()


def load_input(file):
    """
    Unified intake layer for tabular data.
    """

    filename = file.name.lower()

    # ---------------- CSV ----------------
    if filename.endswith(".csv"):
        df = pd.read_csv(
            file,
            comment="#",
            skip_blank_lines=True
        )

    # ---------------- TSV ----------------
    elif filename.endswith(".tsv"):
        df = pd.read_csv(
            file,
            sep="\t",
            comment="#",
            skip_blank_lines=True
        )

    # ---------------- EXCEL ----------------
    elif filename.endswith(".xlsx") or filename.endswith(".xls"):
        df = pd.read_excel(file)

    # ---------------- JSON ----------------
    elif filename.endswith(".json"):
        data = json.load(file)
        if not isinstance(data, list):
            raise ValueError("JSON must be an array of records")
        df = pd.DataFrame(data)

    else:
        raise ValueError(f"Unsupported file type: {file.name}")

    # 🔑 SAFE HEADER NORMALIZATION
    df.columns = [_normalize_column(c) for c in df.columns]

    return df
