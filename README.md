📁 Projeto CVM – Download e Extração de Dados Públicos

Este projeto em Python permite baixar e extrair automaticamente arquivos ZIP da CVM (Comissão de Valores Mobiliários) contendo dados de companhias abertas, como DFP (Demonstrações Financeiras Padronizadas) e CIA (Cadastro de Companhias Abertas).

Os arquivos extraídos são arquivos CSV, prontos para análise com ferramentas como pandas.

✅ Funcionalidades

Download automático dos arquivos .zip da CVM.

Listagem dos CSVs contidos no ZIP.

Extração dos CSVs para uma pasta local chamada arquivos.

📦 Requisitos

Python 3.9 ou superior

Pacotes: requests, zipfile (nativo), io (nativo), os (nativo), pandas

Você pode instalar os pacotes necessários com:

pip install requests pandas

🚀 Como usar
1. Baixe o arquivo ZIP da CVM
zip_bytes = baixar_zip_cvm('dfp', 2024)  # tipo: 'dfp' ou 'cia'; ano: int

2. Liste os CSVs dentro do ZIP
arquivos_csv = listar_csvs_zip(zip_bytes)
print(arquivos_csv)

3. Extraia os arquivos para a pasta ./arquivos
extrair_csv(zip_bytes)

📘 Referência das Funções
baixar_zip_cvm(tipo: str, ano: int) -> io.BytesIO

Baixa o arquivo ZIP da CVM com base no tipo e ano informados.

tipo: 'dfp' ou 'cia'

ano: ano desejado (ex: 2024)

Retorna: objeto BytesIO com o conteúdo do ZIP

listar_csvs_zip(zip_bytes: io.BytesIO) -> list

Retorna uma lista com os nomes dos arquivos .csv contidos no ZIP.

extrair_csv(zip_bytes: io.BytesIO) -> None

Extrai os arquivos do ZIP para uma pasta local chamada arquivos.

🌐 Estrutura das URLs da CVM

Os arquivos ZIP seguem a seguinte estrutura de URL:

https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/{TIPO}/DADOS/{tipo}_cia_aberta_{ANO}.zip


Exemplo real:

https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/dfp_cia_aberta_2024.zip

📁 Organização de Saída

Após a extração, os arquivos .csv ficarão salvos na pasta:

./arquivos/

📝 Observações

O código não depende de bibliotecas externas pesadas, o que o torna leve e portátil.

A pasta de destino será criada automaticamente se não existir.

A extração será completa — todos os arquivos dentro do ZIP são extraídos.

📄 Licença

Uso educacional e experimental. Os dados pertencem à CVM – Comissão de Valores Mobiliários
.
