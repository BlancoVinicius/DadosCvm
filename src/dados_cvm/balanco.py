import pandas as pd
from typing import Literal
from datetime import datetime, date

class Balanco:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        
    def filtrar_por_cnpj(self, cnpj: str) -> 'Balanco':
        self.df = self.df[self.df['CNPJ_CIA'] == cnpj]
        return self
    
    def filtrar_por_cd_cvm(self, cd_cvm: int) -> 'Balanco':
        self.df = self.df[self.df['CD_CVM'] == cd_cvm]
        return self    
    
    def filtrar_por_data_referencia(self, dt_refer: str | date) -> 'Balanco':
        """
        Filtra o balanço pela data de referência.

        Args:
            dt_refer (date): Data de referência (ex: dd/MM/YYYY)

        Returns:
            Balanco: O balanço filtrado.
        """
        # Se dt_refer vier como string, você pode converter:
        if isinstance(dt_refer, str):
            dt_refer = datetime.strptime(dt_refer, "%d/%m/%Y").date()

        self.df['DT_REFER'] = pd.to_datetime(self.df['DT_REFER'])
        dt_refer = pd.to_datetime(dt_refer, dayfirst=True, format='%d/%m/%Y')
        self.df = self.df[self.df['DT_REFER'] >= dt_refer]
        return self
        
    def filtrar_por_exercicio(self, ordem_exerc:Literal['PENÚLTIMO', 'ÚLTIMO']) -> 'Balanco':
        self.df = self.df[self.df['ORDEM_EXERC'] == ordem_exerc]
        return self
        
    def get_dataframe(self) -> pd.DataFrame:
        return self.df