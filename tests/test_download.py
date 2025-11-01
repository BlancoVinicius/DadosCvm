"""Testes para o módulo download.py"""
import io
from unittest.mock import patch, MagicMock
import pytest
import requests
from requests.exceptions import HTTPError, RequestException

from dados_cvm.download import ZipDownloader
from dados_cvm.endpoints import DocType

class TestZipDownloader:
    """Testes para a classe ZipDownloader."""

    @patch('requests.get')
    def test_download_zip_success(self, mock_get):
        """Testa o download bem-sucedido de um arquivo ZIP."""
        # Configura o mock para simular uma resposta de sucesso
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'PK\x03\x04\x14\x00\x00\x00\x08\x00'  # Assinatura ZIP
        mock_response.headers = {'Content-Type': 'application/zip'}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Chama o método sob teste
        result = ZipDownloader.download_zip(DocType.DFP, 2023)
        
        # Verificações
        assert isinstance(result, io.BytesIO)
        assert result.getvalue() == mock_response.content
        mock_get.assert_called_once()
        
    @patch('requests.get')
    def test_download_zip_with_octet_stream(self, mock_get):
        """Testa o download quando o Content-Type é octet-stream mas o conteúdo é ZIP."""
        # Configura o mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'PK\x03\x04\x14\x00\x00\x00\x08\x00'  # Assinatura ZIP
        mock_response.headers = {'Content-Type': 'application/octet-stream'}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Chama o método sob teste
        result = ZipDownloader.download_zip(DocType.ITR, 2023)
        
        # Verificações
        assert isinstance(result, io.BytesIO)
        assert result.getvalue() == mock_response.content
        
    @patch('requests.get')
    def test_download_zip_invalid_content_type(self, mock_get):
        """Testa o download quando o Content-Type não é ZIP ou octet-stream."""
        # Configura o mock para retornar um conteúdo inválido
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'Not a zip file'
        mock_response.headers = {'Content-Type': 'text/plain'}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Verifica se a exceção correta é levantada
        with pytest.raises(RequestException, match="Conteúdo inesperado"):
            ZipDownloader.download_zip(DocType.DFP, 2023)
    
    @patch('requests.get')
    @patch('time.sleep')  # Para evitar espera real durante os testes
    def test_download_zip_with_retries(self, mock_sleep, mock_get):
        """Testa o comportamento de retry em caso de falha temporária."""
        # Configura o mock para falhar duas vezes e depois ter sucesso
        mock_response_success = MagicMock()
        mock_response_success.status_code = 200
        mock_response_success.content = b'PK\x03\x04'
        mock_response_success.headers = {'Content-Type': 'application/zip'}
        mock_response_success.raise_for_status.return_value = None
        
        mock_get.side_effect = [
            RequestException("Erro de conexão"),
            RequestException("Timeout"),
            mock_response_success
        ]
        
        # Chama o método sob teste com 3 tentativas
        result = ZipDownloader.download_zip(DocType.DFP, 2023, retries=3)
        
        # Verificações
        assert mock_get.call_count == 3
        assert isinstance(result, io.BytesIO)
        assert result.getvalue() == mock_response_success.content
    
    @patch('requests.get')
    def test_download_zip_http_error_4xx(self, mock_get):
        """Testa o comportamento com erros HTTP 4xx (exceto 429)."""
        # Configura o mock para simular um erro 404
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        # Verifica se a exceção é propagada imediatamente para erros 4xx
        with pytest.raises(HTTPError, match="404"):
            ZipDownloader.download_zip(DocType.DFP, 2023, retries=3)
        
        # Verifica que não houve tentativas adicionais
        assert mock_get.call_count == 1
    
    @patch('requests.get')
    @patch('time.sleep')  # Para evitar espera real durante os testes
    def test_download_zip_rate_limit_429(self, mock_sleep, mock_get):
        """Testa o comportamento com erro 429 (Too Many Requests)."""
        # Configura o mock para simular um erro 429 seguido de sucesso
        mock_response_error = MagicMock()
        mock_response_error.status_code = 429
        mock_response_error.raise_for_status.side_effect = HTTPError("429 Too Many Requests")
        
        mock_response_success = MagicMock()
        mock_response_success.status_code = 200
        mock_response_success.content = b'PK\x03\x04'
        mock_response_success.headers = {'Content-Type': 'application/zip'}
        mock_response_success.raise_for_status.return_value = None
        
        mock_get.side_effect = [
            mock_response_error,
            mock_response_success
        ]
        
        # Chama o método sob teste
        result = ZipDownloader.download_zip(DocType.DFP, 2023, retries=2)
        
        # Verificações
        assert mock_get.call_count == 2
        assert isinstance(result, io.BytesIO)
        assert result.getvalue() == mock_response_success.content
    
    @patch('requests.get')
    @patch('time.sleep')  # Para evitar espera real durante os testes
    def test_download_zip_exhaust_retries(self, mock_sleep, mock_get):
        """Testa o esgotamento de tentativas."""
        # Configura o mock para falhar sempre
        mock_get.side_effect = RequestException("Falha na conexão")
        
        # Verifica se a exceção é levantada após esgotar as tentativas
        with pytest.raises(RequestException, match="Falha na conexão"):
            ZipDownloader.download_zip(DocType.DFP, 2023, retries=2)
        
        # Verifica o número de chamadas
        assert mock_get.call_count == 2
    
    def test_default_constants(self):
        """Testa os valores padrão das constantes da classe."""
        assert ZipDownloader.DEFAULT_RETRIES == 3
        assert ZipDownloader.BACKOFF_SECONDS == 1.5
        assert ZipDownloader.TIMEOUT_SECONDS == 60.0
