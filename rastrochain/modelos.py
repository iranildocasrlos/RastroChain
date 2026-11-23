"""O átomo do rastreio: uma transferência de um endereço para outro."""

from dataclasses import dataclasses
from datetime import datetime
from decimal import Decimal


@dataclasses
class Transferencia:
    rede:str                 # "Rede Tron"
    token:str                #. "USDT"
    fash:str                 # identificação da Transação na rede
    origem:str               # endereco de enviou  
    destino:str              # endereco que recebeu
    valor:Decimal            # unidades di token: 36.68, não 36680000
    momento:datetime         # em UTC — a blockchain não tem fuso de Brasília   
