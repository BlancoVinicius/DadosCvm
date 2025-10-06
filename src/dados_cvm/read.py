from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, Iterator, Optional

import pandas as pd

from .endpoints import StatementType

__all__ = ["CSVReader"]


# Presets simples de dtypes por StatementType.
# Observação: os esquemas completos variam; mantenha flexível e sobrescrevível via parâmetro.
_COMMON_DTYPES: Dict[str, str] = {
    "cnpj_cia": "string",
    "dt_referencia": "string",  # será convertido depois para datetime, se desejado
    "vl_conta": "float64",
}

_DTYPES_BY_STATEMENT: Dict[StatementType, Dict[str, str]] = {
    StatementType.BPA: _COMMON_DTYPES,
    StatementType.BPP: _COMMON_DTYPES,
    StatementType.DRE: _COMMON_DTYPES,
    StatementType.DFC_MD: _COMMON_DTYPES,
    StatementType.DFC_MI: _COMMON_DTYPES,
    StatementType.DMPL: _COMMON_DTYPES,
    StatementType.DRA: _COMMON_DTYPES,
    StatementType.DVA: _COMMON_DTYPES,
}


class CSVReader:
    """Leitor de CSVs grandes com suporte a chunks e dtypes configuráveis."""

    @staticmethod
    def get_default_dtypes(statement: Optional[StatementType]) -> Optional[Dict[str, str]]:
        if statement is None:
            return None
        return _DTYPES_BY_STATEMENT.get(statement)

    @staticmethod
    def read_csv(
        path: str | Path,
        *,
        dtypes: Optional[Dict[str, str]] = None,
        chunksize: Optional[int] = None,
        usecols: Optional[Iterable[str]] = None,
        encoding: Optional[str] = "latin1",
        sep: str = ",",
        statement: Optional[StatementType] = None,
    ) -> pd.DataFrame | Iterator[pd.DataFrame]:
        """Lê um CSV com pandas, suportando chunks e dtypes presets.

        Args:
            path: caminho do arquivo CSV.
            dtypes: mapeamento de colunas -> dtype pandas (sobrepõe preset).
            chunksize: se definido, retorna um iterador de DataFrames.
            usecols: colunas a carregar (otimiza memória e tempo).
            encoding: encoding do arquivo (default: utf-8).
            sep: separador (default: ',').
            statement: se informado, usa presets básicos de dtypes.

        Returns:
            DataFrame completo ou Iterator[DataFrame] quando chunksize for usado.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Arquivo CSV não encontrado: {path}")

        # Define dtypes padrão por statement, permitindo override pelo usuário
        final_dtypes = dict(CSVReader.get_default_dtypes(statement) or {})
        if dtypes:
            final_dtypes.update(dtypes)

        read_kwargs = dict(
            dtype=final_dtypes if final_dtypes else None,
            usecols=list(usecols) if usecols is not None else None,
            encoding=encoding,
            sep=sep,
            low_memory=False,
        )

        if chunksize is not None:
            return pd.read_csv(path, chunksize=chunksize, **read_kwargs)
        return pd.read_csv(path, **read_kwargs)

