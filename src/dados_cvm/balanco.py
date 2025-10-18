import pandas as pd
from typing import Literal

class Balanco:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        
    def filtrar_por_cnpj(self, cnpj: str) -> 'Balanco':
        self.df = self.df[self.df['CNPJ_CIA'] == cnpj]
        return self
    
    def filtrar_por_cd_cvm(self, cd_cvm: int) -> 'Balanco':
        self.df = self.df[self.df['CD_CVM'] == cd_cvm]
        return self    
    

    # def filtrar_por_ano(self, ano: int) -> 'Balanco':
    #     self.df = self.df[self.df['ANO'] == ano]
    #     return self
        
    def filtrar_por_exercicio(self, ordem_exerc:Literal['PENÚLTIMO', 'ÚLTIMO']) -> 'Balanco':
        self.df = self.df[self.df['ORDEM_EXERC'] == ordem_exerc]
        return self
        
    def get_dataframe(self) -> pd.DataFrame:
        return self.df