# from __future__ import annotations

# from pathlib import Path
# from typing import Optional

# import typer

# from .client import CVMClient
# from .endpoints import DocType, Scope, StatementType
# from .extract import ZipExtractor
# from .download import ZipDownloader

# app = typer.Typer(help="CLI para baixar, listar e ler dados públicos da CVM.")


# @app.command()
# def download(
#     doc: str = typer.Option("dfp", help="Tipo de documento (dfp, itr)."),
#     ano: int = typer.Option(..., help="Ano de referência (>=2010)."),
#     dest: Path = typer.Option(Path("./arquivos"), help="Diretório de destino para extração."),
#     extrair: bool = typer.Option(True, help="Extrair arquivos após download."),
# ):
#     """Baixa o ZIP do tipo/ano e opcionalmente extrai para DEST."""
#     doc_type = DocType(doc.lower())
#     zip_bytes = ZipDownloader.download_zip(doc_type, ano)
#     if extrair:
#         ZipExtractor.extract_all(zip_bytes, dest)
#         typer.echo(f"Arquivos extraídos em: {dest}")
#     else:
#         out = dest / f"{doc_type.value}_{ano}.zip"
#         dest.mkdir(parents=True, exist_ok=True)
#         out.write_bytes(zip_bytes.getvalue())
#         typer.echo(f"ZIP salvo em: {out}")


# @app.command()
# def listar(
#     doc: str = typer.Option("dfp", help="Tipo de documento (dfp, itr)."),
#     ano: int = typer.Option(..., help="Ano de referência (>=2010)."),
# ):
#     """Lista os CSVs dentro do ZIP sem extrair."""
#     doc_type = DocType(doc.lower())
#     zip_bytes = ZipDownloader.download_zip(doc_type, ano)
#     files = ZipExtractor.list_csv(zip_bytes)
#     for f in files:
#         typer.echo(f)


# @app.command()
# def ler(
#     statement: str = typer.Option(..., help="Demonstrativo (BPA,BPP,DRE,DFC_MD,DFC_MI,DMPL,DRA,DVA)"),
#     scope: str = typer.Option("con", help="Escopo (con, ind)."),
#     ano: int = typer.Option(..., help="Ano."),
#     data_dir: Path = typer.Option(Path("./arquivos"), help="Diretório com os CSVs extraídos."),
#     chunks: bool = typer.Option(False, help="Ler em chunks."),
#     chunksize: int = typer.Option(250_000, help="Tamanho do chunk."),
#     normalize: bool = typer.Option(False, help="Padronizar nomes de colunas e tipos."),
# ):
#     """Lê um demonstrativo já baixado e extraído no diretório informado."""
#     client = CVMClient(data_dir=data_dir)
#     st = StatementType(statement.upper())
#     sc = Scope(scope.lower())
#     df_or_iter = client.load_statement(
#         ano=ano, statement=st, scope=sc, chunks=chunks, chunksize=chunksize, normalize=normalize
#     )
#     if chunks:
#         # Apenas mostra o primeiro chunk como amostra
#         for i, chunk in enumerate(df_or_iter):
#             typer.echo(chunk.head().to_string())
#             if i >= 0:
#                 break
#     else:
#         typer.echo(df_or_iter.head().to_string())


# if __name__ == "__main__":
#     app()

