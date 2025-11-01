from __future__ import annotations

from enum import Enum
from typing import Final

__all__ = [
    "DocType",
    "StatementType",
    "Scope",
    "UrlBuilder",
]


class DocType(str, Enum):
    """Tipos de documentos disponíveis no portal de dados da CVM.

    Atualmente suportamos:
    - DFP: Demonstrações Financeiras Padronizadas
    - ITR: Informes trimestrais
    """

    DFP = "dfp"
    ITR = "itr"


class StatementType(str, Enum):
    """Tipos de demonstrativos usados nos arquivos da CVM.

    BPA: Balanço Patrimonial Ativo
    BPP: Balanço Patrimonial Passivo
    DRE: Demonstração do Resultado do Exercício
    DFC_MD: Demonstração de Fluxo de Caixa (Método Direto)
    DFC_MI: Demonstração de Fluxo de Caixa (Método Indireto)
    DMPL: Demonstração das Mutações do Patrimônio Líquido
    DRA: Demonstração do Resultado Abrangente
    DVA: Demonstração do Valor Adicionado
    """

    BPA = "BPA"
    BPP = "BPP"
    DRE = "DRE"
    DFC_MD = "DFC_MD"
    DFC_MI = "DFC_MI"
    DMPL = "DMPL"
    DRA = "DRA"
    DVA = "DVA"


class Scope(str, Enum):
    """Escopo do demonstrativo.

    CON: Consolidado
    IND: Individual
    """

    CON = "con"
    IND = "ind"


class UrlBuilder:
    """Helper para construir URLs dos arquivos ZIP no portal da CVM.

    Padrão de URL (conforme README):
    https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/{TIPO}/DADOS/{tipo}_cia_aberta_{ANO}.zip

    Onde:
    - {TIPO} = doc_type em maiúsculas (ex.: DFP, ITR)
    - {tipo} = doc_type em minúsculas (ex.: dfp, itr)
    - {ANO}  = ano desejado (ex.: 2024)
    """

    BASE_URL: Final[str] = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/{TIPO}/DADOS/{tipo}_cia_aberta_{ANO}.zip"

    @classmethod
    def build_zip_url(cls, doc_type: DocType, ano: int) -> str:
        """Monta a URL do ZIP para o tipo de documento e ano informados.

        Args:
            doc_type: Tipo de documento (DocType.DFP, DocType.ITR).
            ano: Ano de referência (ex.: 2024).

        Returns:
            URL completa para download do ZIP correspondente.

        Raises:
            ValueError: se o ano for inválido (menor que 2010, por exemplo).
        """
        if not isinstance(ano, int) or ano < 2010:
            raise ValueError("Ano inválido. Utilize um ano >= 2010.")

        tipo_lower = doc_type.value.lower()
        tipo_upper = doc_type.value.upper()

        return cls.BASE_URL.format(TIPO=tipo_upper, tipo=tipo_lower, ANO=ano)


