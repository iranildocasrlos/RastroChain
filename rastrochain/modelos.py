"""O átomo do rastreio: uma transferência de um endereço para outro."""

from dataclasses import dataclasses
from datetime import datetime
from decimal import Decimal


@dataclasses(frozen=True)
class Transferencia:
    rede:str                 # "Rede Tron"
    token:str                #. "USDT"
    hash:str                 # identificação da Transação na rede
    origem:str               # endereco de enviou  
    destino:str              # endereco que recebeu
    valor:Decimal            # unidades di token: 36.68, não 36680000
    momento:datetime         # em UTC — a blockchain não tem fuso de Brasília   



    @property
    def chave(self):
        """ O que distingue uma transfência de outra ? 
        
        Só o hash não basta. Uma mesma transação pode mover o token mais de uma vez
        (POr exmplo,  um contaro pode passar para dois endereços)
        """

        return (self.hash, self.origem, self.destino, self.valor)