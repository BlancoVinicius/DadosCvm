from __future__ import annotations

import io
from pathlib import Path
from typing import Iterator, Optional

import pandas as pd

from .endpoints import DocType, Scope, StatementType, UrlBuilder
from .download import ZipDownloader
from .extract import ZipExtractor
from .read import CSVReader
from .normalize import standardize_dataframe

__all__ = ["CVMClient"]


class CVMClient:
    """Cliente de alto nível para baixar, extrair e ler dados públicos da CVM.

    Exemplos:
        client = CVMClient(data_dir="./arquivos")
        client.get_dfp(2024, extrair=True)
        df = client.load_statement(2024, StatementType.DRE, Scope.CON)
    """

    def __init__(self, data_dir: str | Path = "./arquivos", cache_dir: Optional[str | Path] = None):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir = Path(cache_dir) if cache_dir else None
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    # -----------------------------
    # Download / Extração de DFP
    # -----------------------------
    def get_dfp(self, ano: int, *, extrair: bool = True) -> Path:
        """Baixa o ZIP do DFP para o ano e, opcionalmente, extrai para `data_dir`.

        Returns:
            Caminho do diretório de dados (self.data_dir) após extração ou download.
        """
        zip_bytes = ZipDownloader.download_zip(DocType.DFP, ano)
        if extrair:
            ZipExtractor.extract_all(zip_bytes, self.data_dir)
        return self.data_dir

    # -----------------------------
    # Leitura de demonstrativos
    # -----------------------------
    def load_statement(
        self,
        ano: int,
        statement: StatementType,
        scope: Scope,
        *,
        chunks: bool = False,
        chunksize: int = 250_000,
        usecols: Optional[list[str]] = None,
        normalize: bool = False,
        sep: Optional[str] = ";",
        encoding: Optional[str] = "latin1",
    ) -> pd.DataFrame | Iterator[pd.DataFrame]:
        """Carrega um CSV de demonstrativo (ex.: DRE CON) para o ano informado.

        Requer que os arquivos já estejam presentes em `self.data_dir`.
        """
        csv_path = self._find_csv_path(DocType.DFP, statement, scope, ano)

        reader = CSVReader.read_csv(
            csv_path,
            chunksize=chunksize if chunks else None,
            usecols=usecols,
            statement=statement,
            encoding=encoding,
            sep=sep,
        )

        if chunks:
            def _norm_iter() -> Iterator[pd.DataFrame]:
                for df in reader:  # type: ignore[assignment]
                    yield standardize_dataframe(df) if normalize else df

            return _norm_iter()

        df = reader  # type: ignore[assignment]
        return standardize_dataframe(df) if normalize else df

    # -----------------------------
    # Helpers
    # -----------------------------
    def _find_csv_path(self, doc_type: DocType, statement: StatementType, scope: Scope, ano: int) -> Path:
        """Resolve o caminho do CSV com base no padrão oficial dos arquivos.

        Padrão esperado (exemplos reais de DFP):
            dfp_cia_aberta_DRE_con_2024.csv
            dfp_cia_aberta_BPA_ind_2024.csv
        """
        # Nome no padrão visto nos arquivos oficiais
        filename = f"{doc_type.value}_cia_aberta_{statement.value}_{scope.value}_{ano}.csv"
        path = self.data_dir / filename
        if not path.exists():
            raise FileNotFoundError(
                f"Arquivo não encontrado: {path}. Baixe e extraia o ZIP primeiro (ex.: get_dfp({ano}))."
            )
        return path

