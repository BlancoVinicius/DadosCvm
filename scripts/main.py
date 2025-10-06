from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    # Preferir pacote instalado
    from src.dados_cvm.client import CVMClient
    from src.dados_cvm.endpoints import Scope, StatementType
except ImportError:
    # Fallback: adicionar ./src ao PYTHONPATH para desenvolvimento local
    sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))
    from src.dados_cvm.client import CVMClient
    from src.dados_cvm.endpoints import Scope, StatementType

# def parse_args() -> argparse.Namespace:
#     parser = argparse.ArgumentParser(description="Exemplo: baixar/extrair DFP e ler demonstrativo com CVMClient")
#     parser.add_argument("--ano", type=int, required=True, help="Ano de referência (>=2010)")
#     parser.add_argument(
#         "--statement",
#         type=str,
#         default="DRE",
#         help="Demonstrativo: BPA,BPP,DRE,DFC_MD,DFC_MI,DMPL,DRA,DVA",
#     )
#     parser.add_argument(
#         "--scope",
#         type=str,
#         default="con",
#         choices=["con", "ind"],
#         help="Escopo: con (consolidado) ou ind (individual)",
#     )
#     parser.add_argument(
#         "--data-dir",
#         type=Path,
#         default=Path("./arquivos"),
#         help="Diretório para extração/leitura dos CSVs",
#     )
#     parser.add_argument("--normalize", action="store_true", help="Padroniza colunas, datas e tipos")
#     parser.add_argument("--chunks", action="store_true", help="Lê o CSV em chunks")
#     parser.add_argument("--chunksize", type=int, default=250_000, help="Tamanho do chunk")
#     return parser.parse_args()


# def main() -> None:
#     args = parse_args()

#     client = CVMClient(data_dir=args.data_dir)

#     # Baixar e extrair DFP do ano solicitado
#     client.get_dfp(ano=args.ano, extrair=True)

#     # Mapear argumentos para enums
#     st = StatementType(args.statement.upper())
#     sc = Scope(args.scope.lower())

#     # Ler demonstrativo e imprimir amostra
#     df_or_iter = client.load_statement(
#         ano=args.ano,
#         statement=st,
#         scope=sc,
#         chunks=args.chunks,
#         chunksize=args.chunksize,
#         normalize=args.normalize,
#     )

#     if args.chunks:
#         for i, chunk in enumerate(df_or_iter):
#             print(chunk.head())
#             if i >= 0:
#                 break
#     else:
#         print(df_or_iter.head())


# if __name__ == "__main__":
#     main()


def main() -> None:
 
    client = CVMClient()

    # Baixar e extrair DFP do ano solicitado
    # client.get_dfp(2024, extrair=True)

    # Mapear argumentos para enums
    st = StatementType.BPA
    sc = Scope.CON

    # Ler demonstrativo e imprimir amostra
    df_or_iter = client.load_statement(
        ano=2024,
        statement=st,
        scope=sc,
    )

    print(df_or_iter.head())

if __name__ == "__main__":
    main()