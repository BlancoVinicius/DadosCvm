"""Testes para o módulo client.py"""
import io
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
import pandas as pd

from dados_cvm.client import CVMClient
from dados_cvm.endpoints import DocType, Scope, StatementType

class TestCVMClient:
    """Testes para a classe CVMClient."""

    def test_init_default_values(self):
        """Testa a inicialização com valores padrão."""
        client = CVMClient()
        assert client.path_data_dir == Path("./arquivos")
        assert client.path_data_dir.exists()
        assert client._path_cache_dir is None

    def test_init_custom_dirs(self, tmp_path):
        """Testa a inicialização com diretórios personalizados."""
        data_dir = tmp_path / "data"
        cache_dir = tmp_path / "cache"
        
        client = CVMClient(data_dir=data_dir, cache_dir=cache_dir)
        
        assert client.path_data_dir == data_dir
        assert client._path_cache_dir == cache_dir
        assert data_dir.exists()
        assert cache_dir.exists()

    def test_path_data_dir_setter(self, tmp_path):
        """Testa o setter de path_data_dir."""
        client = CVMClient()
        new_path = tmp_path / "new_data"
        
        client.path_data_dir = new_path
        
        assert client.path_data_dir == new_path
        assert client.path_data_dir.exists()

    @patch('dados_cvm.client.ZipDownloader.download_zip')
    @patch('dados_cvm.client.ZipExtractor.extract_all')
    def test_get_zip(self, mock_extract, mock_download, tmp_path):
        """Testa o método get_zip."""
        # Configuração dos mocks
        mock_zip_content = io.BytesIO(b"zip content")
        mock_download.return_value = mock_zip_content
        
        # Teste com extração
        client = CVMClient(data_dir=tmp_path)
        result = client.get_zip(2023, DocType.DFP, extrair=True)
        
        # Verificações
        mock_download.assert_called_once_with(DocType.DFP, 2023)
        mock_extract.assert_called_once_with(mock_zip_content, tmp_path)
        assert result == mock_zip_content
        
        # Reset dos mocks
        mock_download.reset_mock()
        mock_extract.reset_mock()
        
        # Teste sem extração
        result = client.get_zip(2023, DocType.DFP, extrair=False)
        mock_download.assert_called_once_with(DocType.DFP, 2023)
        mock_extract.assert_not_called()

    @patch('dados_cvm.client.CSVReader.read_csv')
    def test_load_statement(self, mock_read_csv, tmp_path):
        """Testa o método load_statement."""
        # Configuração
        client = CVMClient(data_dir=tmp_path)
        test_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        mock_read_csv.return_value = test_df
        
        # Cria um arquivo CSV falso para o teste de _find_csv_path
        csv_path = tmp_path / "dfp_cia_aberta_DRE_con_2023.csv"
        csv_path.touch()
        
        # Teste sem normalização
        result = client.load_statement(
            ano=2023,
            statement=StatementType.DRE,
            scope=Scope.CONSOLIDADO,
            doc_type=DocType.DFP
        )
        
        # Verificações
        assert isinstance(result, pd.DataFrame)
        pd.testing.assert_frame_equal(result, test_df)
        mock_read_csv.assert_called_once()
        
        # Teste com normalização
        with patch('dados_cvm.client.standardize_dataframe') as mock_normalize:
            mock_normalize.return_value = test_df.rename(columns={"col1": "col1_normalized"})
            
            result = client.load_statement(
                ano=2023,
                statement=StatementType.DRE,
                scope=Scope.CONSOLIDADO,
                doc_type=DocType.DFP,
                normalize=True
            )
            
            mock_normalize.assert_called_once()
            assert "col1_normalized" in result.columns

    def test_find_csv_path(self, tmp_path):
        """Testa o método _find_csv_path."""
        client = CVMClient(data_dir=tmp_path)
        
        # Cria um arquivo CSV de teste
        test_file = tmp_path / "dfp_cia_aberta_DRE_con_2023.csv"
        test_file.touch()
        
        # Teste com arquivo existente
        result = client._find_csv_path(DocType.DFP, StatementType.DRE, Scope.CONSOLIDADO, 2023)
        assert result == test_file
        
        # Teste com arquivo inexistente
        with pytest.raises(FileNotFoundError):
            client._find_csv_path(DocType.ITR, StatementType.BPA, Scope.INDIVIDUAL, 2023)

    @patch('dados_cvm.client.CSVReader.read_csv')
    def test_load_statement_chunks(self, mock_read_csv, tmp_path):
        """Testa o carregamento em chunks."""
        # Configuração
        client = CVMClient(data_dir=tmp_path)
        test_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        mock_read_csv.return_value = [test_df, test_df]  # Dois chunks para teste
        
        # Cria um arquivo CSV falso para o teste de _find_csv_path
        csv_path = tmp_path / "dfp_cia_aberta_DRE_con_2023.csv"
        csv_path.touch()
        
        # Teste com chunks
        result = client.load_statement(
            ano=2023,
            statement=StatementType.DRE,
            scope=Scope.CONSOLIDADO,
            doc_type=DocType.DFP,
            chunks=True
        )
        
        # Verificações
        assert hasattr(result, '__iter__')
        chunks = list(result)
        assert len(chunks) == 2
        for chunk in chunks:
            pd.testing.assert_frame_equal(chunk, test_df)
