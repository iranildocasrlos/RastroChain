"""Configuração que vem do ambiente: chaves e limites.

Nada de chave escrita no código. O .env fica fora do git, e cada máquina — a
sua, o servidor, a de quem entrar no time — tem o seu.
"""


import os



TRONGRID_URL = os.environ.get("TRONGRID_URL", "https://api.trongrid.io")


# Funciona sem a chave do TronGrid mas com limite de baixo de chamadas por segundos
TRONGRID_API_KEY = os.environ.get("TRONGRID_API_KEY", "").strip()


# Implmentando a pausa mínima entre duas chamadas seguidasa fim de evitar o erro 429, (Muitas requisições)
PAUSA = float(os.environ.get("RASTROCHAIN_PAUSA", "0.35"))


# O contrato do USDT na Tron (TRC-20). É ESTE endereço que define o token, não
# o nome: qualquer pessoa pode criar um token chamado "USDT" — e golpe usa isso
# para mostrar à vítima um saldo que não vale nada.
USDT_TRON = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"