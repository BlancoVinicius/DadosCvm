"""Testes para o módulo extract.py"""
import io
import zipfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from dados_cvm.extract import ZipExtractor

class TestZipExtractor:
    """Testes para a classe ZipExtractor."""
    
    def test_list_csv_empty_zip(self):
        """Testa list_csv com um ZIP vazio."""
        # Cria um ZIP vazio em memória
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            pass
        
        # Testa a listagem
        zip_buffer.seek(0)
        result = ZipExtractor.list_csv(zip_buffer)
        assert result == []
    
    def test_list_csv_with_files(self):
        """Testa list_csv com um ZIP contendo arquivos CSV e não-CSV."""
        # Cria um ZIP com arquivos
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            # Adiciona arquivos CSV
            zf.writestr('arquivo1.csv', 'conteudo')
            zf.writestr('pasta/arquivo2.csv', 'conteudo')
            # Adiciona arquivo não-CSV
            zf.writestr('documento.txt', 'texto')
        
        # Testa a listagem
        zip_buffer.seek(0)
        result = ZipExtractor.list_csv(zip_buffer)
        
        # Verifica se apenas os arquivos CSV foram listados
        assert sorted(result) == ['arquivo1.csv', 'pasta/arquivo2.csv']
    
    def test_extract_all_normal_case(self, tmp_path):
        """Testa a extração normal de arquivos."""
        # Cria um ZIP com alguns arquivos
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            zf.writestr('arquivo1.txt', 'conteudo1')
            zf.writestr('pasta/arquivo2.txt', 'conteudo2')
        
        # Extrai para um diretório temporário
        zip_buffer.seek(0)
        ZipExtractor.extract_all(zip_buffer, tmp_path)
        
        # Verifica se os arquivos foram extraídos corretamente
        assert (tmp_path / 'arquivo1.txt').read_text() == 'conteudo1'
        assert (tmp_path / 'pasta' / 'arquivo2.txt').read_text() == 'conteudo2'
    
    def test_extract_all_path_traversal_attempt(self, tmp_path):
        """Testa a proteção contra path traversal."""
        # Cria um ZIP com tentativa de path traversal
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            # Tenta extrair para fora do diretório de destino
            info = zipfile.ZipInfo()
            info.filename = '../../arquivo_malicioso.txt'
            zf.writestr(info, 'conteúdo malicioso')
        
        # Verifica se a extração falha com RuntimeError
        zip_buffer.seek(0)
        with pytest.raises(RuntimeError, match="Path traversal detectado"):
            ZipExtractor.extract_all(zip_buffer, tmp_path)
        
        # Verifica se o arquivo malicioso não foi criado
        assert not (tmp_path / 'arquivo_malicioso.txt').exists()
    
    def test_extract_all_creates_destination_dir(self, tmp_path):
        """Testa se o diretório de destino é criado se não existir."""
        # Diretório que não existe ainda
        dest_dir = tmp_path / 'novo_diretorio'
        
        # Cria um ZIP simples
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            zf.writestr('teste.txt', 'teste')
        
        # Extrai para o diretório que não existe
        zip_buffer.seek(0)
        ZipExtractor.extract_all(zip_buffer, dest_dir)
        
        # Verifica se o diretório foi criado e o arquivo extraído
        assert dest_dir.exists()
        assert (dest_dir / 'teste.txt').read_text() == 'teste'
    
    @patch('zipfile.ZipFile')
    def test_extract_all_handles_zip_errors(self, mock_zip, tmp_path):
        """Testa o tratamento de erros durante a extração."""
        # Configura o mock para simular um erro ao extrair
        mock_zip.return_value.__enter__.return_value.infolist.side_effect = zipfile.BadZipFile("Arquivo ZIP corrompido")
        
        # Verifica se a exceção é propagada
        with pytest.raises(zipfile.BadZipFile):
            ZipExtractor.extract_all(io.BytesIO(b'not a zip'), tmp_path)
