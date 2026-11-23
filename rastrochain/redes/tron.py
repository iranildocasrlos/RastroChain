"""USDT na rede Tron, pela API pública da TronGrid.

Só LEITURA de dados públicos: nenhuma chave privada, nenhuma assinatura, nenhum
envio. É o que a blockchain mostra a qualquer um, organizado.
"""

import hashlib
import time
from datetime import datetime, timezone
from decimal import Decimal

import httpx

from rastrochain import __version__, config
from rastrochain.modelos import Transferencia 


_ALFABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
_REPETIR_EM =  {429, 500, 502, 503, 504}   # erros passageiros: vale tentar de novo

class ErroTron(Exception):
    """ A TronGrid recusou, ou não respondeu mesmo depois das novas tentativas """

def endereco_valido(endereco:str ) --> bool:

    """  Confere o formato e o dígito verificador de um endereço TRON (T...)  
         
         Um enderço com uma letra tem cara de válido, mas aponta para luguar nenhum. 
         Os 4 bytes finais são um verificador calculado sobre o resto; se não baterem, o endereço foi digitado errado e isso é pago antes de gastar 
         uma chamada a API,  antes de um laudo citar a carteira errada

         
    
    """
