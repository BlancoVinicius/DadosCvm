from __future__ import annotations

import io
from pathlib import Path
from typing import Optional, List
import pandas as pd
from typing import Iterator

from .endpoints import DocType, Scope, StatementType
from .download import ZipDownloader
from .extract import ZipExtractor

from .read import CSVReader 
from .normalize import standardize_dataframe

__all__ = ["CVMClient"]


class CVMClient:
    """A classe CVMClient extrai e lê dados públicos da CVM (Comissão de Valores Mobiliários).

    Args:
    data_dir = (str | Path, optional): Diretório onde os dados extraídos serão armazenados.
        Padrão é "./arquivos".
    cache_dir (str | Path, optional): Diretório para armazenamento em cache dos dados,
        para evitar downloads repetidos. Se None, o cache não será utilizado.

    Exemplo:
    Para instanciar a classe, fornecendo um diretório específico para os dados:

        client = CVMClient(data_dir="./arquivos")
    """

    def __init__(self, data_dir: str | Path = "./arquivos", cache_dir: Optional[str | Path] = None):
        self._path_data_dir = Path(data_dir)
        self._path_data_dir.mkdir(parents=True, exist_ok=True)
        self._path_cache_dir = Path(cache_dir) if cache_dir else None
        self._files_downloaded: List[str] = []
        if self._path_cache_dir:
            self._path_cache_dir.mkdir(parents=True, exist_ok=True)

    @property
    def path_data_dir(self):
        """Getter: obtém o valor do caminho do diretório de dados"""
        return self._path_data_dir

    @path_data_dir.setter
    def path_data_dir(self, caminho: str | Path):
        """Setter: define o valor do caminho do diretório de dados"""
        if not isinstance(caminho, (str, Path)):
            raise ValueError("O caminho precisa ser um diretório válido ou da classe Path.")
        self._path_data_dir = Path(caminho)


    # -----------------------------
    # Download / Extração de DFP    
    # -----------------------------
    def get_zip(self, ano: int, doc_type: DocType, extrair: bool = True) -> io.BytesIO:
        """
        Baixa o arquivo ZIP em memória do Demonstrativo Financeiro solicitado (DFP/ITR/DRE) para o ano especificado e,
        opcionalmente, extrai o conteúdo para o diretório padrão.

        Args:
            ano (int): Ano para o arquivo DFP/ITR/DRE.
            extrair (bool, opcional): Se True, extrai o conteúdo do ZIP para o diretório `path_data_dir`.
                Padrão é True.

        Returns:
            io.BytesIO: BytesIO contendo o conteúdo do zip.

        Exemplo:
            Para baixar e extrair os dados do DFP de 2023:

                caminho = client.get_dfp(2023, extrair=True)
        """
        zip_bytes = ZipDownloader.download_zip(doc_type, ano)
        if extrair:
            ZipExtractor.extract_all(zip_bytes, self.path_data_dir)
        return zip_bytes

    # -----------------------------
    # Leitura de demonstrativos
    # -----------------------------
    def load_statement(
        self,
        ano: int,
        statement: StatementType, # Qual demonstrativo (ex.: BPA, BPP, DRE ...)
        scope: Scope, # escopo do demonstrativo (ex.: CON, IND)
        doc_type: DocType, # tipo do demonstrativo (ex.: DFP, ITR)
        chunks: bool = False,
        chunksize: int = 250_000,
        cols: Optional[list[str]] = None, # colunas a serem lidas
        normalize: bool = False, 
        sep: Optional[str] = ";",
        encoding: Optional[str] = "latin1",
    ) -> pd.DataFrame | Iterator[pd.DataFrame]:
        """Essa função carrega um CSV de demonstrativo (ex.: DRE CON / BPA CON) para o ano informado.

        Args:
            ano (int): Ano para o arquivo DFP/ITR/DRE.
            statement (StatementType): Tipo do demonstrativo (
                ex: 
                    BPA = "BPA"
                    BPP = "BPP"
                    DRE = "DRE"
                    DFC_MD = "DFC_MD"
                    DFC_MI = "DFC_MI"
                    DMPL = "DMPL"
                    DRA = "DRA"
                    DVA = "DVA"
            ).
            scope (Scope): Escopo do demonstrativo (ex.: CON, IND).
            chunks (bool, opcional): Se True, retorna um iterador de DataFrames.
                Padrão é False.
            chunksize (int, opcional): Tamanho do chunk para leitura em chunks.
                Padrão é 250_000.
            cols (list[str], opcional): Lista de colunas a serem lidas.
                Padrão é None. Se None, todas as colunas serão lidas.
            normalize (bool, opcional): Se True, normaliza o DataFrame.
                Padrão é False.
            sep (str, opcional): Separador do arquivo CSV.
                Padrão é ";".
            encoding (str, opcional): Codificação do arquivo CSV.
                Padrão é "latin1".

        Returns:
            pd.DataFrame | Iterator[pd.DataFrame]: DataFrame ou iterador de DataFrames.

        Raises:
            FileNotFoundError: se o arquivo CSV não for encontrado.

        Requer que os arquivos já estejam presentes em `path_data_dir`.
        """
        csv_path = self._find_csv_path(doc_type, statement, scope, ano)

        reader = CSVReader.read_csv(
            csv_path,
            chunksize=chunksize if chunks else None,
            usecols=cols,
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
        path = self.path_data_dir / filename
        if not path.exists():
            raise FileNotFoundError(
                f"Arquivo não encontrado: {path}. Baixe e extraia o ZIP primeiro (ex.: get_zip({ano}))."
            )
        return path

