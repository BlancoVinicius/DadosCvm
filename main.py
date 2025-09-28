# %% [markdown]
# # Análise de Dados CVM
# Este script baixa e processa dados da CVM (Comissão de Valores Mobiliários)

# %% Importações
import requests
import zipfile
import io
import os
# import pandas as pd

# %% Função para baixar ZIP da CVM
def baixar_zip_cvm(tipo:str, ano:int) -> io.BytesIO:
    url_base = f"https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/{tipo.upper()}/DADOS/{tipo.lower()}_cia_aberta_{ano}.zip"

    if tipo.lower() not in ['dfp', 'cia']:
        raise ValueError("Tipo deve ser 'dfp' ou 'cia'")

    response = requests.get(url_base)
    response.raise_for_status()
    return io.BytesIO(response.content)

# %% Função para listar CSVs
def listar_csvs_zip(zip_bytes:io.BytesIO) -> list:
    """Lista os CSVs dentro de um arquivo zip."""
    with zipfile.ZipFile(zip_bytes, 'r') as zip_ref:
        return [name for name in zip_ref.namelist() if name.endswith('.csv')]

# %% Função para extrair CSVs
def extrair_csv(zip_bytes: io.BytesIO) -> None:
    """Extrai todos os CSVs do zip e salva na pasta 'arquivos'."""
    # Criar pasta 'arquivos' se não existir
    pasta_arquivos = os.path.join(os.getcwd(), 'arquivos')
    os.makedirs(pasta_arquivos, exist_ok=True)
    
    with zipfile.ZipFile(zip_bytes, 'r') as file_zip:
        # Extrair todos os arquivos para a pasta 'arquivos'
        file_zip.extractall(pasta_arquivos)
        print(f"Arquivos extraídos para: {pasta_arquivos}")

# %% Execução principal
if __name__ == "__main__":
    tipo = 'dfp'
    ano = 2024
    zip_bytes = baixar_zip_cvm(tipo, ano)
    extrair_csv(zip_bytes)

# %% Teste: Listar CSVs (opcional)
# Descomente as linhas abaixo para listar os CSVs antes de extrair
# tipo = 'dfp'
# ano = 2024
# zip_bytes = baixar_zip_cvm(tipo, ano)
# csvs = listar_csvs_zip(zip_bytes)
# print(f"CSVs encontrados: {csvs}")

# %% [markdown]
# ## Como usar:
# 1. Execute a célula "Execução principal" para baixar e extrair todos os arquivos
# 2. Execute a célula "Teste" para apenas listar os CSVs disponíveis
# 3. Os arquivos serão salvos na pasta 'arquivos'
