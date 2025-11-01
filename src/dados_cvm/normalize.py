from __future__ import annotations

import re
from typing import Iterable, List, Optional

import pandas as pd

__all__ = [
    "to_snake_case",
    "normalize_columns",
    "coerce_numeric",
    "parse_dates",
    "standardize_dataframe",
]


_WHITESPACE_RE = re.compile(r"\s+")
_NON_ALNUM_RE = re.compile(r"[^0-9a-zA-Z_]")


def to_snake_case(name: str) -> str:
    """Converte um nome para snake_case básico, removendo acentos/símbolos."""
    # Normalização simples sem remover acentos de forma sofisticada (evita deps extras)
    s = name.strip()
    s = s.replace("-", " ")
    s = s.replace("/", " ")
    s = s.replace(".", " ")
    s = _WHITESPACE_RE.sub("_", s)
    s = _NON_ALNUM_RE.sub("", s)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    return s.lower()


def normalize_columns(df: pd.DataFrame, columns_map: Optional[dict] = None) -> pd.DataFrame:
    """Padroniza nomes de colunas para snake_case.

    Se `columns_map` for fornecido, aplica substituições específicas após snake_case.
    """
    new_cols = {c: to_snake_case(c) for c in df.columns}
    df = df.rename(columns=new_cols)
    if columns_map:
        df = df.rename(columns=columns_map)
    return df


def coerce_numeric(df: pd.DataFrame, cols: Iterable[str]) -> pd.DataFrame:
    """Converte colunas para numérico com `pd.to_numeric(errors='coerce')`."""
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def parse_dates(df: pd.DataFrame, cols: Iterable[str], dayfirst: bool = False, format: Optional[str] = None) -> pd.DataFrame:
    """Converte colunas para datetime com `pd.to_datetime`.

    Define `errors='coerce'` para evitar falhas e resultar em NaT em casos inválidos.
    """
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce", dayfirst=dayfirst, format=format)
    return df


def standardize_dataframe(
    df: pd.DataFrame,
    *,
    date_cols: Optional[Iterable[str]] = None,
    numeric_cols: Optional[Iterable[str]] = None,
    columns_map: Optional[dict] = None,
) -> pd.DataFrame:
    """Pipeline simples: renomeia colunas → datas → numéricos.

    Exemplo de uso:
        df = standardize_dataframe(df, date_cols=["dt_referencia"], numeric_cols=["vl_conta"]) 
    """
    df = normalize_columns(df, columns_map=columns_map)
    if date_cols:
        df = parse_dates(df, date_cols)
    if numeric_cols:
        df = coerce_numeric(df, numeric_cols)
    return df

