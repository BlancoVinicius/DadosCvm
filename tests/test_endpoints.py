"""Testes para o módulo endpoints.py"""
import pytest

from dados_cvm.endpoints import DocType, StatementType, Scope, UrlBuilder

class TestDocType:
    """Testes para a enum DocType."""
    
    def test_doc_type_values(self):
        """Verifica os valores da enum DocType."""
        assert DocType.DFP.value == "dfp"
        assert DocType.ITR.value == "itr"
    
    def test_doc_type_members(self):
        """Verifica os membros da enum DocType."""
        assert isinstance(DocType.DFP, DocType)
        assert isinstance(DocType.ITR, DocType)
        assert len(DocType) == 2


class TestStatementType:
    """Testes para a enum StatementType."""
    
    def test_statement_type_values(self):
        """Verifica os valores da enum StatementType."""
        assert StatementType.BPA.value == "BPA"
        assert StatementType.BPP.value == "BPP"
        assert StatementType.DRE.value == "DRE"
        assert StatementType.DFC_MD.value == "DFC_MD"
        assert StatementType.DFC_MI.value == "DFC_MI"
        assert StatementType.DMPL.value == "DMPL"
        assert StatementType.DRA.value == "DRA"
        assert StatementType.DVA.value == "DVA"
    
    def test_statement_type_members(self):
        """Verifica os membros da enum StatementType."""
        assert isinstance(StatementType.BPA, StatementType)
        assert isinstance(StatementType.DRE, StatementType)
        assert len(StatementType) == 8


class TestScope:
    """Testes para a enum Scope."""
    
    def test_scope_values(self):
        """Verifica os valores da enum Scope."""
        assert Scope.CON.value == "con"
        assert Scope.IND.value == "ind"
    
    def test_scope_members(self):
        """Verifica os membros da enum Scope."""
        assert isinstance(Scope.CON, Scope)
        assert isinstance(Scope.IND, Scope)
        assert len(Scope) == 2


class TestUrlBuilder:
    """Testes para a classe UrlBuilder."""
    
    def test_build_zip_url_dfp(self):
        """Testa a construção de URL para DFP."""
        url = UrlBuilder.build_zip_url(DocType.DFP, 2023)
        expected = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/dfp_cia_aberta_2023.zip"
        assert url == expected
    
    def test_build_zip_url_itr(self):
        """Testa a construção de URL para ITR."""
        url = UrlBuilder.build_zip_url(DocType.ITR, 2024)
        expected = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/ITR/DADOS/itr_cia_aberta_2024.zip"
        assert url == expected
    
    def test_build_zip_url_invalid_year(self):
        """Testa o tratamento de ano inválido."""
        # Ano como string deve levantar exceção
        with pytest.raises(ValueError, match="Ano inválido"):
            UrlBuilder.build_zip_url(DocType.DFP, "2023")  # type: ignore
        
        # Ano muito antigo
        with pytest.raises(ValueError, match="Ano inválido"):
            UrlBuilder.build_zip_url(DocType.DFP, 2009)
        
        # Ano negativo
        with pytest.raises(ValueError, match="Ano inválido"):
            UrlBuilder.build_zip_url(DocType.DFP, -2023)
    
    def test_base_url_constant(self):
        """Verifica se a constante BASE_URL está correta."""
        expected = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/{TIPO}/DADOS/{tipo}_cia_aberta_{ANO}.zip"
        assert UrlBuilder.BASE_URL == expected
