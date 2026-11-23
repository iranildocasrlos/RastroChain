# Apostila — RastroChain: rastreamento de cripto do zero, em Python

Sep 24, 2026 · @Iranildo

## Como esta apostila funciona

**Você escreve o código; a apostila diz o quê, em que ordem e por quê.** Cada passo cria ou altera um arquivo, mostra o conteúdo inteiro e termina com uma conferência que prova que funcionou antes de seguir.

Três regras que valem do começo ao fim:

1. **Todo bloco de código foi executado antes de entrar aqui.** Se o seu resultado for diferente do que a conferência diz, o problema está entre o bloco e o seu arquivo — compare os dois antes de mudar o código.
2. **Nada roda direto na sua máquina: tudo roda em Docker.** O código fica na sua pasta e o contêiner o enxerga; assim o projeto funciona igual no Mac, no servidor e na máquina de quem entrar no time.
3. **A ordem importa.** Cada parte usa o que a anterior deixou pronto. O núcleo (Parte 1) não sabe que existe tela nem banco, e é por isso que ele vem primeiro: é o que vale o produto, e é o que se testa mais fácil.

**Convenções**

| símbolo | significa |
| --- | --- |
| 📄 Crie o arquivo | arquivo novo, conteúdo inteiro no bloco |
| ✏️ Altere | trocar um trecho de um arquivo que já existe |
| ▶️ Rode | comando no terminal, dentro da pasta do projeto |
| ✅ Conferência | o que tem de aparecer para o passo contar como feito |
| ⚠️ | armadilha já conhecida, explicada antes de você cair nela |

Código e nomes em português, como nos outros projetos da casa; os nomes que vêm das bibliotecas e das redes (`from`, `to`, `block_timestamp`) ficam como a fonte os escreve.

## O mapa: o que existe no fim

O projeto é um servidor Python (FastAPI) com Postgres, rodando em Docker; as telas são geradas pelo servidor, e o único JavaScript de verdade é o grafo. Estes são os arquivos, com a parte da apostila que cria cada um.

```
rastrochain/                     (a pasta do projeto)
├── Dockerfile                   Parte 0   a imagem do Python
├── docker-compose.yml           Parte 0   o app (o Postgres entra na Parte 2)
├── requirements.txt             Parte 0   as dependências
├── .env.exemplo  .gitignore     Parte 0
├── pytest.ini                   Parte 0
├── rastrochain/                 (o código)
│   ├── __init__.py              Parte 0
│   ├── config.py                Parte 1   chaves e limites, vindos do .env
│   ├── modelos.py               Parte 1   Transferencia: o átomo do rastreio
│   ├── redes/
│   │   ├── tron.py              Parte 1   USDT na Tron (TronGrid)
│   │   ├── ethereum.py          Parte 8
│   │   └── bitcoin.py           Parte 8
│   ├── rastreio.py              Parte 1   o caminho do dinheiro, salto a salto
│   ├── grafo.py                 Parte 1   o nosso grafo: nós, arestas e o HTML
│   ├── arquivo.py               Parte 1   o arquivo do caso: .rchain
│   ├── __main__.py              Parte 1   `python -m rastrochain`: o núcleo pela linha de comando
│   ├── banco/                   Parte 2   tabelas (SQLAlchemy) e cache de transações
│   ├── api/                     Parte 2   as rotas da API (FastAPI)
│   ├── web/                     Parte 3   telas (Jinja + HTMX) e o grafo na tela
│   ├── contas/                  Parte 4   login, empresas, perfis, auditoria
│   ├── rotulos/                 Parte 5   corretoras, lista OFAC, denúncias
│   ├── laudo/                   Parte 6   PDF e OpenTimestamps
│   └── vigia/                   Parte 7   endereços observados e alertas
├── migracoes/                   Parte 2   Alembic: o esquema versionado
└── testes/                      desde a Parte 1
```

Três marcos:

| depois da | o que já funciona |
| --- | --- |
| Parte 1 | rastrear USDT na Tron pela linha de comando, ver o grafo no navegador e guardar o caso num arquivo .rchain — já serve para os primeiros laudos feitos "à mão" |
| Parte 3 | o produto na tela: colar um endereço e ver o grafo crescer |
| Parte 6 | o MVP vendável: casos, identificação de corretoras e laudo com prova de integridade |

## Parte 0 — A máquina e o esqueleto

No fim desta parte existe uma pasta com o projeto vazio, uma imagem Docker com o Python e as dependências, e um comando que roda os testes. São 5 passos curtos.

### Passo 1 — O que precisa estar instalado

- **Docker Desktop**, aberto. Tudo roda dentro dele.
- **Um editor** (VS Code serve bem) e o **git**.
- **Uma chave gratuita da TronGrid** (opcional agora, recomendada): crie a conta em trongrid.io e gere a chave em *Dashboard → API Keys*. Sem ela o projeto funciona, mas mais devagar.

Não é preciso instalar Python na máquina: ele vem dentro da imagem.

### Passo 2 — 📁 A pasta do projeto

▶️ **Rode:**

```bash
mkdir -p ~/Developer/Python/rastrochain/rastrochain/redes ~/Developer/Python/rastrochain/testes
cd ~/Developer/Python/rastrochain
git init
```

A pasta de fora (`rastrochain/`) é o projeto; a de dentro (`rastrochain/rastrochain/`) é o pacote Python com o código. Todos os comandos da apostila rodam **na pasta de fora**.

### Passo 3 — 📄 Os arquivos do esqueleto

📄 **Crie o arquivo** `requirements.txt`:

```text
# Parte 0: só o que o núcleo usa. FastAPI, banco e o resto entram nas partes
# que precisam deles — dependência que ninguém usa ainda é só superfície de ataque.
httpx>=0.27,<1
pytest>=8,<9
```

📄 **Crie o arquivo** `Dockerfile`:

```dockerfile
# A imagem só traz o Python e as dependências. O CÓDIGO não entra na imagem:
# ele fica na sua pasta e chega ao contêiner pelo volume do docker-compose.
# Assim, salvou o arquivo, rodou de novo — sem reconstruir nada.
FROM python:3.12-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```

📄 **Crie o arquivo** `docker-compose.yml`:

```yaml
services:
  app:
    build: .
    env_file: .env
    volumes:
      - .:/app
```

📄 **Crie o arquivo** `pytest.ini`:

```ini
[pytest]
# A raiz do projeto entra no caminho de import: é o que deixa os testes
# fazerem `from rastrochain...` sem instalar o pacote.
pythonpath = .
testpaths = testes
```

📄 **Crie o arquivo** `.env.exemplo`:

```bash
# Copie para .env (que NÃO vai para o git) e preencha.

# Chave gratuita em https://www.trongrid.io (Dashboard → API Keys).
# Sem ela funciona, mas a TronGrid limita as chamadas por segundo.
TRONGRID_CHAVE=

# Pausa entre duas chamadas à API, em segundos.
RASTROCHAIN_PAUSA=0.35
```

📄 **Crie o arquivo** `.gitignore`:

```text
.env
__pycache__/
.pytest_cache/
saidas/
```

### Passo 4 — 📄 O pacote

📄 **Crie o arquivo** `rastrochain/__init__.py`:

```python
"""RastroChain — rastreamento de criptoativos."""
__version__ = "0.1.0"
```

📄 **Crie o arquivo** `rastrochain/redes/__init__.py` **vazio**. É ele que faz a pasta `redes/` ser um pacote do Python.

### Passo 5 — ▶️ A primeira subida

▶️ **Rode:**

```bash
cp .env.exemplo .env          # e cole a sua chave da TronGrid, se tiver
docker compose build
docker compose run --rm app python -c "import rastrochain, httpx; print('rastrochain', rastrochain.__version__)"
docker compose run --rm app pytest -q
```

✅ **Conferência:** o terceiro comando imprime `rastrochain 0.1.0`, e o pytest diz `no tests ran` — ainda não há teste, e é isso que se espera agora.

⚠️ Se o Docker disser que não acha o `.env`, faltou o `cp` do primeiro comando: o `docker-compose.yml` exige o arquivo, mesmo com as chaves vazias.

## Parte 1 — O núcleo sem tela: USDT na Tron

No fim desta parte, um comando rastreia o USDT de uma carteira na rede Tron, salto a salto, desenha o nosso grafo (um HTML que abre em qualquer navegador) e guarda o caso num arquivo do RastroChain, o .rchain, que o sistema reabre depois. É o coração do produto: tudo o que vem depois (banco, API, tela, laudo) usa estas funções sem mudar nenhuma.

O núcleo não sabe que existe tela nem banco. Isso tem uma vantagem concreta: ele é testado sem internet, com uma "fonte falsa" no lugar da rede.

### Passo 6 — 📄 `rastrochain/config.py`

```python
"""Configuração que vem do ambiente: chaves e limites.

Nada de chave escrita no código. O .env fica fora do git, e cada máquina — a
sua, o servidor, a de quem entrar no time — tem o seu.
"""
import os

TRONGRID_URL = os.environ.get("TRONGRID_URL", "https://api.trongrid.io")

# Sem chave a TronGrid funciona, mas com limite baixo de chamadas por segundo.
TRONGRID_CHAVE = os.environ.get("TRONGRID_CHAVE", "").strip()

# Pausa mínima entre duas chamadas seguidas, em segundos: é a gentileza que
# evita o erro 429 ("muitas requisições").
PAUSA = float(os.environ.get("RASTROCHAIN_PAUSA", "0.35"))

# O contrato do USDT na Tron (TRC-20). É ESTE endereço que define o token, não
# o nome: qualquer pessoa pode criar um token chamado "USDT" — e golpe usa isso
# para mostrar à vítima um saldo que não vale nada.
USDT_TRON = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
```

⚠️ **O token se identifica pelo contrato, nunca pelo nome.** Um token criado por qualquer pessoa com o nome "USDT" aparece na carteira da vítima como se fosse dólar digital. Todo filtro do projeto usa o endereço do contrato.

### Passo 7 — 📄 `rastrochain/modelos.py`

```python
"""O átomo do rastreio: uma transferência de um endereço para outro."""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class Transferencia:
    rede: str            # "tron"
    token: str           # "USDT"
    hash: str            # identificador da transação na rede
    origem: str          # endereço que mandou
    destino: str         # endereço que recebeu
    valor: Decimal       # em unidades do token: 36.68, não 36680000
    momento: datetime    # em UTC — a blockchain não tem fuso de Brasília

    @property
    def chave(self):
        """O que distingue uma transferência de outra.

        Só o hash não basta: uma mesma transação pode mover o token mais de
        uma vez (um contrato que repassa para dois endereços, por exemplo).
        """
        return (self.hash, self.origem, self.destino, self.valor)
```

⚠️ **Dinheiro é `Decimal`, nunca `float`.** Em `float`, 0,1 + 0,2 dá 0,30000000000000004; num laudo, a soma dos saltos tem de fechar ao centavo.

### Passo 8 — 📄 `rastrochain/redes/tron.py`

O cliente da TronGrid: valida o endereço, busca as transferências de USDT de uma carteira página por página e respeita o limite de chamadas.

```python
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

_ALFABETO = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
_REPETIR_EM = {429, 500, 502, 503, 504}   # erros passageiros: vale tentar de novo


class ErroTron(Exception):
    """A TronGrid recusou, ou não respondeu mesmo depois das novas tentativas."""


def endereco_valido(endereco: str) -> bool:
    """Confere o formato E o dígito verificador de um endereço Tron (T…).

    Um endereço com uma letra trocada tem cara de válido e aponta para lugar
    nenhum. Os 4 bytes finais são um verificador calculado sobre o resto; se
    não baterem, o endereço foi digitado errado — e isso é pego antes de gastar
    uma chamada à API, e antes de um laudo citar a carteira errada.
    """
    if not isinstance(endereco, str) or len(endereco) != 34 or not endereco.startswith("T"):
        return False
    numero = 0
    for letra in endereco:
        posicao = _ALFABETO.find(letra)
        if posicao < 0:
            return False
        numero = numero * 58 + posicao
    try:
        bruto = numero.to_bytes(25, "big")
    except OverflowError:
        return False
    corpo, verificador = bruto[:21], bruto[21:]
    if corpo[0] != 0x41:          # todo endereço Tron começa com o byte 0x41
        return False
    return hashlib.sha256(hashlib.sha256(corpo).digest()).digest()[:4] == verificador


def _converter(item: dict) -> Transferencia | None:
    info = item.get("token_info") or {}
    # A API já foi filtrada pelo contrato do USDT; conferir de novo aqui custa
    # nada e protege contra o token falso se o filtro de lá um dia falhar.
    if info.get("address") != config.USDT_TRON or item.get("type") != "Transfer":
        return None
    casas = int(info.get("decimals", 6))
    return Transferencia(
        rede="tron",
        token=info.get("symbol") or "USDT",
        hash=item["transaction_id"],
        origem=item["from"],
        destino=item["to"],
        valor=Decimal(item["value"]) / (Decimal(10) ** casas),
        momento=datetime.fromtimestamp(item["block_timestamp"] / 1000, tz=timezone.utc),
    )


class ClienteTron:
    """Conversa com a TronGrid respeitando o limite de chamadas."""

    def __init__(self, url=None, chave=None, pausa=None, http=None):
        self.url = (url or config.TRONGRID_URL).rstrip("/")
        self.pausa = config.PAUSA if pausa is None else pausa
        chave = config.TRONGRID_CHAVE if chave is None else chave
        cabecalhos = {"Accept": "application/json", "User-Agent": f"rastrochain/{__version__}"}
        if chave:
            cabecalhos["TRON-PRO-API-KEY"] = chave
        self.http = http or httpx.Client(timeout=30, headers=cabecalhos)
        self._ultima_chamada = 0.0

    def _get(self, caminho: str, parametros: dict) -> dict:
        motivo = "sem resposta"
        for tentativa in range(5):
            falta = self.pausa - (time.monotonic() - self._ultima_chamada)
            if falta > 0:
                time.sleep(falta)
            self._ultima_chamada = time.monotonic()
            try:
                resposta = self.http.get(self.url + caminho, params=parametros)
            except httpx.TransportError as erro:
                motivo = f"falha de rede: {erro}"
            else:
                if resposta.status_code == 200:
                    return resposta.json()
                motivo = f"HTTP {resposta.status_code}: {resposta.text[:200]}"
                if resposta.status_code not in _REPETIR_EM:
                    break                     # 400, 404…: repetir não muda nada
            time.sleep(2 ** tentativa)        # espera 1, 2, 4, 8 s entre tentativas
        raise ErroTron(motivo)

    def transferencias_usdt(self, endereco, direcao="saida", desde=None, ate=None, limite=200):
        """As transferências de USDT de um endereço, da mais recente para a mais antiga.

        direcao: "saida" (o que o endereço mandou), "entrada" (o que recebeu)
                 ou "ambas".
        desde, ate: datetime com fuso; filtram pelo momento do bloco.
        limite: quantas no máximo. Endereço de corretora tem milhões, e buscar
                todas travaria o rastreio por horas.
        """
        if not endereco_valido(endereco):
            raise ValueError(f"endereço Tron inválido: {endereco!r}")
        parametros = {
            "contract_address": config.USDT_TRON,
            "limit": min(limite, 200),          # 200 é o máximo por página
            "only_confirmed": "true",           # bloco ainda não confirmado pode sumir
        }
        if direcao == "saida":
            parametros["only_from"] = "true"
        elif direcao == "entrada":
            parametros["only_to"] = "true"
        elif direcao != "ambas":
            raise ValueError(f"direção inválida: {direcao!r}")
        if desde:
            parametros["min_timestamp"] = int(desde.timestamp() * 1000)
        if ate:
            parametros["max_timestamp"] = int(ate.timestamp() * 1000)

        caminho = f"/v1/accounts/{endereco}/transactions/trc20"
        encontradas = []
        while len(encontradas) < limite:
            pagina = self._get(caminho, parametros)
            itens = pagina.get("data") or []
            for item in itens:
                transferencia = _converter(item)
                if transferencia:
                    encontradas.append(transferencia)
                    if len(encontradas) >= limite:
                        break
            # A próxima página vem por um marcador ("fingerprint"), não por número.
            marcador = (pagina.get("meta") or {}).get("fingerprint")
            if not itens or not marcador:
                break
            parametros["fingerprint"] = marcador
        return encontradas
```

Três decisões para entender antes de seguir:

- **O verificador do endereço** é conferido na nossa máquina, sem chamar a API: base58 para número, os 21 primeiros bytes são o endereço, os 4 últimos são um SHA-256 duplo deles.
- **As novas tentativas** só acontecem em erro passageiro (429 e 5xx), com espera dobrando a cada vez. Um 404 não melhora com insistência.
- **`only_confirmed`**: transação em bloco ainda não confirmado pode ser revertida. Laudo só com o que é definitivo.

✅ **Conferência** — contra a rede de verdade:

```bash
docker compose run --rm app python -c "
from rastrochain.redes.tron import ClienteTron, endereco_valido
from rastrochain import config
print('contrato válido?  ', endereco_valido(config.USDT_TRON))
print('letra trocada?    ', endereco_valido(config.USDT_TRON[:-1] + 'u'))
for t in ClienteTron().transferencias_usdt(config.USDT_TRON, direcao='entrada', limite=3):
    print(t.momento, t.origem, '->', t.destino, t.valor)
"
```

Tem de imprimir `True`, depois `False`, e três transferências recentes com data em UTC, os dois endereços começando com `T` e o valor com casas decimais (não um inteiro gigante).

### Passo 9 — 📄 `rastrochain/rastreio.py`

O rastreio em si: parte de um endereço e segue o dinheiro salto a salto, em largura (primeiro todos os vizinhos do salto 1, depois os do salto 2). Ele não conhece a TronGrid: recebe uma `fonte` qualquer que saiba responder `transferencias_usdt`. É isso que deixa os testes rodarem sem rede.

```python
"""O caminho do dinheiro, salto a salto.

Parte de um endereço e segue as transferências para a frente ("saida": para
onde o dinheiro foi) ou para trás ("entrada": de onde ele veio), até N saltos.

Três travas separam um rastreio útil de uma explosão de dados:

- valor mínimo: "poeira" de centavos não é o caminho do dinheiro — e golpistas
  mandam poeira de propósito, para sujar o histórico da vítima;
- o tempo: dinheiro que chegou a um endereço às 14h só pode ter saído dele
  DEPOIS das 14h. Sem essa regra, o salto 2 mistura o dinheiro do caso com
  tudo o que aquele endereço movimentou antes;
- tetos: endereço de corretora tem milhões de transferências. Chegar nele é o
  FIM do rastreio — é ali que se pede o bloqueio —, não um lugar para abrir.
"""
from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class Rastreio:
    inicio: str
    direcao: str
    saltos: int
    transferencias: list = field(default_factory=list)
    salto_de: dict = field(default_factory=dict)   # endereço → salto em que apareceu
    truncados: set = field(default_factory=set)    # endereços que bateram em algum teto

    def total_por_salto(self):
        """Quanto passou em cada salto — a primeira coisa que o analista olha."""
        totais = {}
        for t in self.transferencias:
            quem_manda = t.origem if self.direcao == "saida" else t.destino
            salto = self.salto_de[quem_manda] + 1
            totais[salto] = totais.get(salto, Decimal(0)) + t.valor
        return dict(sorted(totais.items()))


def rastrear(fonte, inicio, saltos=2, direcao="saida", valor_minimo=Decimal("0"),
             desde=None, ate=None, por_endereco=200, max_enderecos=60):
    """Monta o rastreio. `fonte` é quem busca as transferências — o ClienteTron
    de verdade, ou uma fonte falsa nos testes, sem rede nenhuma."""
    if direcao not in ("saida", "entrada"):
        raise ValueError("direção do rastreio é 'saida' ou 'entrada'")
    rastreio = Rastreio(inicio=inicio, direcao=direcao, saltos=saltos)
    rastreio.salto_de[inicio] = 0
    # O "relógio" de cada endereço: para a frente, o momento em que o dinheiro
    # CHEGOU nele; para trás, o momento em que SAIU dele.
    marco = {inicio: None}
    vistas = set()
    fronteira = [inicio]

    for salto in range(1, saltos + 1):
        proxima = []
        for endereco in fronteira:
            de, ate_aqui = desde, ate
            if marco[endereco] is not None:
                if direcao == "saida":
                    de = max(filter(None, [desde, marco[endereco]]))
                else:
                    ate_aqui = min(filter(None, [ate, marco[endereco]]))
            lista = fonte.transferencias_usdt(endereco, direcao=direcao, desde=de,
                                              ate=ate_aqui, limite=por_endereco)
            if len(lista) >= por_endereco:
                rastreio.truncados.add(endereco)
            for t in lista:
                if t.valor < valor_minimo or t.chave in vistas:
                    continue
                vizinho = t.destino if direcao == "saida" else t.origem
                novo = vizinho not in rastreio.salto_de
                if novo and len(rastreio.salto_de) >= max_enderecos:
                    rastreio.truncados.add(endereco)
                    continue
                vistas.add(t.chave)
                rastreio.transferencias.append(t)
                if novo:
                    rastreio.salto_de[vizinho] = salto
                    marco[vizinho] = t.momento
                    proxima.append(vizinho)
                elif direcao == "saida" and marco.get(vizinho) and t.momento < marco[vizinho]:
                    marco[vizinho] = t.momento      # chegou dinheiro antes: o relógio recua
                elif direcao == "entrada" and marco.get(vizinho) and t.momento > marco[vizinho]:
                    marco[vizinho] = t.momento
        fronteira = proxima
        if not fronteira:
            break
    return rastreio
```

⚠️ **A regra do tempo é o que separa rastreio de lista de transações.** Sem ela, o salto 2 traz tudo o que a carteira intermediária já movimentou na vida, inclusive meses antes do golpe. O `marco` guarda, para cada endereço, quando o dinheiro do caso chegou; só conta o que saiu depois disso.

⚠️ **Endereço "truncado" não é erro: é pista.** Quem bate no teto de 200 transferências quase sempre é corretora ou carteira de serviço. É ali que o rastreio termina e o ofício de bloqueio começa. Na Parte 5, esses endereços ganham nome.

### Passo 10 — 📄 `rastrochain/grafo.py`

O nosso grafo, sem depender do i2: carteiras são nós, dinheiro que passa é aresta. A função `montar` devolve dados puros; nesta parte eles viram um HTML de um arquivo só (Cytoscape.js pelo CDN), e na Parte 3 a mesma função alimenta a tela web.

```python
"""O rastreio como grafo: carteiras são nós, dinheiro que passa é aresta.

Várias transferências entre as mesmas duas carteiras viram UMA aresta, com o
total, a quantidade e o período. Com duzentas setas soltas entre os mesmos dois
pontos, ninguém lê o desenho. Os hashes de cada transferência continuam
guardados na aresta: são a prova de cada centavo.

`montar` devolve dados puros (dicionários), que servem tanto para o HTML desta
parte quanto para a tela web da Parte 3.
"""
import json
from pathlib import Path


def _usdt(valor):
    """1234.5 → '1.234,50 USDT': o jeito que o analista lê."""
    texto = f"{valor:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return f"{texto} USDT"


def montar(rastreio):
    nos, arestas = {}, {}

    def no(endereco):
        if endereco not in nos:
            nos[endereco] = {
                "id": endereco,
                "salto": rastreio.salto_de.get(endereco),
                "inicio": endereco == rastreio.inicio,
                "truncado": endereco in rastreio.truncados,
                "recebido": 0, "enviado": 0,
            }
        return nos[endereco]

    for t in sorted(rastreio.transferencias, key=lambda t: t.momento):
        no(t.origem)["enviado"] += t.valor
        no(t.destino)["recebido"] += t.valor
        par = (t.origem, t.destino)
        if par not in arestas:
            arestas[par] = {"id": f"{t.origem}>{t.destino}", "origem": t.origem,
                            "destino": t.destino, "total": 0, "quantidade": 0,
                            "primeira": t.momento, "ultima": t.momento, "hashes": []}
        a = arestas[par]
        a["total"] += t.valor
        a["quantidade"] += 1
        a["ultima"] = t.momento
        a["hashes"].append(t.hash)

    # Decimal e datetime não existem em JSON: o valor vai como texto exato
    # (nada de float) e a data em ISO, sempre UTC.
    for n in nos.values():
        n["recebido"], n["enviado"] = str(n["recebido"]), str(n["enviado"])
    for a in arestas.values():
        a["rotulo"] = _usdt(a["total"]) + (f" ({a['quantidade']}x)" if a["quantidade"] > 1 else "")
        a["total"] = str(a["total"])
        a["primeira"], a["ultima"] = a["primeira"].isoformat(), a["ultima"].isoformat()
    return {"inicio": rastreio.inicio, "direcao": rastreio.direcao,
            "nos": list(nos.values()), "arestas": list(arestas.values())}


def salvar_json(rastreio, arquivo):
    arquivo = Path(arquivo)
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(json.dumps(montar(rastreio), ensure_ascii=False, indent=2), encoding="utf-8")
    return arquivo


_PAGINA = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<title>RastroChain — __TITULO__</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.28.1/cytoscape.min.js"></script>
<style>
  body { margin: 0; font: 14px system-ui, sans-serif; display: flex; height: 100vh; }
  #grafo { flex: 1; background: #fafafa; }
  #lado { width: 340px; padding: 16px; border-left: 1px solid #ddd; overflow: auto; }
  code { word-break: break-all; font-size: 12px; }
  .leg span { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 6px; }
</style></head><body>
<div id="grafo"></div>
<div id="lado">
  <h3>__TITULO__</h3>
  <p class="leg"><span style="background:#c62828"></span>início do rastreio<br>
     <span style="background:#ef6c00"></span>bateu no teto (provável corretora)<br>
     <span style="background:#1565c0"></span>carteira</p>
  <div id="detalhe">Clique numa carteira ou numa seta.</div>
</div>
<script>
const G = __DADOS__;
const cor = n => n.inicio ? "#c62828" : n.truncado ? "#ef6c00" : "#1565c0";
const curto = e => e.slice(0, 6) + "…" + e.slice(-4);
// Uma coluna por salto: o dinheiro anda da esquerda para a direita (no
// rastreio para trás, a origem fica à esquerda do mesmo jeito).
const colunas = {};
for (const n of G.nos) (colunas[n.salto ?? 0] ||= []).push(n.id);
// Coluna muito alta espremeria o desenho: o passo horizontal cresce junto.
const passo = Math.max(320, 28 * Math.max(...Object.values(colunas).map(c => c.length)));
const posicao = {};
for (const [salto, ids] of Object.entries(colunas)) {
  const x = (G.direcao === "entrada" ? -1 : 1) * Number(salto) * passo;
  ids.forEach((id, i) => { posicao[id] = { x, y: (i - (ids.length - 1) / 2) * 46 }; });
}
const cy = cytoscape({
  container: document.getElementById("grafo"),
  elements: [
    ...G.nos.map(n => ({ data: { ...n, rotulo: curto(n.id), cor: cor(n) } })),
    ...G.arestas.map(a => ({ data: { ...a, source: a.origem, target: a.destino } })),
  ],
  style: [
    { selector: "node", style: { "background-color": "data(cor)", label: "data(rotulo)", "font-size": 10, "min-zoomed-font-size": 6 } },
    { selector: "edge", style: { width: 1.5, "curve-style": "bezier", "min-zoomed-font-size": 9, "target-arrow-shape": "triangle",
      label: "data(rotulo)", "font-size": 9, "text-rotation": "autorotate", "line-color": "#999",
      "target-arrow-color": "#999" } },
  ],
  layout: { name: "preset", positions: n => posicao[n.id()] },
});
const detalhe = document.getElementById("detalhe");
// Tudo o que veio da rede passa por esc() antes de virar HTML: um dado
// esquisito vindo da API não pode virar código rodando na tela do perito.
const esc = v => String(v).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const cod = v => `<code>${esc(v)}</code>`;
const linha = (r, v) => `<p><b>${r}</b><br>${v}</p>`;
cy.on("tap", "node", ev => {
  const n = ev.target.data();
  detalhe.innerHTML = linha("Carteira", cod(n.id)) + linha("Salto", esc(n.salto))
    + linha("Recebeu", esc(n.recebido) + " USDT") + linha("Enviou", esc(n.enviado) + " USDT")
    + (n.truncado ? linha("⚠", "Bateu no teto: pedir dados à corretora.") : "");
});
cy.on("tap", "edge", ev => {
  const a = ev.target.data();
  detalhe.innerHTML = linha("De", cod(a.origem)) + linha("Para", cod(a.destino))
    + linha("Total", esc(a.rotulo)) + linha("Período (UTC)", esc(a.primeira) + "<br>" + esc(a.ultima))
    + linha("Transações", a.hashes.map(cod).join("<br>"));
});
</script></body></html>
"""


def salvar_html(rastreio, arquivo, titulo=""):
    """Um arquivo só, que abre em qualquer navegador — sem servidor."""
    arquivo = Path(arquivo)
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    dados = json.dumps(montar(rastreio), ensure_ascii=False)
    # "</" dentro de um <script> fecharia a tag antes da hora. Trocado pelo
    # escape unicode do "<", continua o mesmo caractere para o JavaScript.
    dados = dados.replace("<", "\\u003c")
    titulo = (titulo or rastreio.inicio).replace("&", "&amp;").replace("<", "&lt;")
    arquivo.write_text(_PAGINA.replace("__TITULO__", titulo).replace("__DADOS__", dados),
                       encoding="utf-8")
    return arquivo
```

Três decisões:

- **Uma aresta por par de carteiras**, com total, quantidade e os hashes. O desenho fica legível e a prova continua inteira.
- **Uma coluna por salto**, da esquerda para a direita, em vez de um layout automático. O perito lê o caminho do dinheiro na ordem em que ele andou.
- **Nada que venha da rede vira HTML sem `esc()`**, e o JSON embutido tem o `<` trocado. O grafo é aberto por perito e por advogado; um dado malicioso na API não pode virar script rodando na máquina deles.

⚠️ **Valores vão como texto no JSON** (`"1234.5"`, não `1234.5`). Número em JSON vira `float` em quase toda linguagem, e o `Decimal` perderia a exatidão no caminho.

### Passo 11 — 📄 `rastrochain/arquivo.py`

O arquivo do caso, com extensão própria: `.rchain`. É o que o perito salva, manda por e-mail e reabre meses depois. Por dentro é um ZIP com três JSON, o mesmo truque do `.docx`: formato nosso, mas que qualquer pessoa consegue abrir se precisar auditar.

| parte | o que guarda |
| --- | --- |
| `manifesto.json` | quem gerou, quando, com que parâmetros, e o SHA-256 das outras partes |
| `rastreio.json` | as transferências completas; é daqui que o caso é reaberto |
| `grafo.json` | nós e arestas prontos, para quem só quer desenhar |

```python
"""O arquivo do caso: `.rchain`.

Um .rchain é um ZIP (como o .docx do Word) com três partes em JSON:

    manifesto.json   quem gerou, quando, com que parâmetros, e o SHA-256 das outras partes
    rastreio.json    as transferências completas: é daqui que o caso é reaberto
    grafo.json       nós e arestas prontos, para quem só quer desenhar

Ser ZIP de JSON tem vantagens concretas: é compacto, qualquer linguagem lê e,
se um dia o RastroChain sumir, o perito ainda consegue abrir o conteúdo.

A verificação dos SHA-256 pega arquivo corrompido e edição descuidada. Ela NÃO
prova que ninguém alterou o caso de propósito: quem altera recalcula os hashes.
A prova contra adulteração é o selo de tempo do laudo, na Parte 6.
"""
import hashlib
import json
import zipfile
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from rastrochain import __version__
from rastrochain.grafo import montar
from rastrochain.modelos import Transferencia
from rastrochain.rastreio import Rastreio

EXTENSAO = ".rchain"
FORMATO = "rastrochain-caso"
VERSAO_FORMATO = 1       # sobe quando o conteúdo mudar de um jeito que o leitor antigo não entenda
_PARTES = ("rastreio.json", "grafo.json")
_TETO_PARTE = 200 * 1024 * 1024   # um JSON de 200 MB já não é um caso: é um ataque ou um erro


class ErroArquivo(Exception):
    """O arquivo não é um .rchain, é de uma versão futura ou não confere."""


def _json(dados):
    return json.dumps(dados, ensure_ascii=False, indent=2).encode("utf-8")


def _rastreio_para_dict(r):
    return {
        "inicio": r.inicio, "direcao": r.direcao, "saltos": r.saltos,
        "salto_de": r.salto_de,
        "truncados": sorted(r.truncados),
        "transferencias": [{
            "rede": t.rede, "token": t.token, "hash": t.hash,
            "origem": t.origem, "destino": t.destino,
            "valor": str(t.valor),                  # texto: o Decimal volta exato
            "momento": t.momento.isoformat(),
        } for t in r.transferencias],
    }


def _dict_para_rastreio(d):
    r = Rastreio(inicio=d["inicio"], direcao=d["direcao"], saltos=d["saltos"])
    r.salto_de = dict(d["salto_de"])
    r.truncados = set(d["truncados"])
    r.transferencias = [Transferencia(
        rede=t["rede"], token=t["token"], hash=t["hash"],
        origem=t["origem"], destino=t["destino"],
        valor=Decimal(t["valor"]), momento=datetime.fromisoformat(t["momento"]),
    ) for t in d["transferencias"]]
    return r


def salvar(rastreio, arquivo, caso="", parametros=None):
    """Grava o caso. `parametros` são os filtros usados (mínimo, datas…): sem
    eles, ninguém reproduz o rastreio depois, e laudo que não se reproduz não
    se sustenta."""
    arquivo = Path(arquivo)
    if arquivo.suffix != EXTENSAO:
        arquivo = arquivo.with_suffix(EXTENSAO)
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    partes = {"rastreio.json": _json(_rastreio_para_dict(rastreio)),
              "grafo.json": _json(montar(rastreio))}
    manifesto = {
        "formato": FORMATO,
        "versao_formato": VERSAO_FORMATO,
        "gerado_por": f"rastrochain {__version__}",
        "gerado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "caso": caso,
        "parametros": parametros or {},
        "resumo": {"transferencias": len(rastreio.transferencias),
                   "enderecos": len(rastreio.salto_de)},
        "sha256": {nome: hashlib.sha256(conteudo).hexdigest() for nome, conteudo in partes.items()},
    }
    with zipfile.ZipFile(arquivo, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("manifesto.json", _json(manifesto))   # primeiro: é o que se lê primeiro
        for nome, conteudo in partes.items():
            z.writestr(nome, conteudo)
    return arquivo


def _ler(z, nome):
    try:
        info = z.getinfo(nome)
    except KeyError:
        raise ErroArquivo(f"falta a parte {nome}") from None
    if info.file_size > _TETO_PARTE:
        raise ErroArquivo(f"{nome} grande demais ({info.file_size} bytes)")
    return z.read(nome)


def abrir(arquivo):
    """Reabre o caso: devolve (manifesto, rastreio). Só lê as partes que
    conhece, pelo nome, e nunca extrai nada para o disco."""
    try:
        z = zipfile.ZipFile(arquivo)
    except (zipfile.BadZipFile, OSError) as erro:
        raise ErroArquivo(f"não é um arquivo {EXTENSAO}: {erro}") from None
    with z:
        try:
            manifesto = json.loads(_ler(z, "manifesto.json"))
        except ValueError:
            raise ErroArquivo("manifesto ilegível") from None
        if not isinstance(manifesto, dict) or manifesto.get("formato") != FORMATO:
            raise ErroArquivo(f"não é um arquivo {EXTENSAO}")
        if manifesto.get("versao_formato", 0) > VERSAO_FORMATO:
            raise ErroArquivo("caso gravado por uma versão mais nova do RastroChain: atualize")
        brutos = {nome: _ler(z, nome) for nome in _PARTES}
    for nome, conteudo in brutos.items():
        if hashlib.sha256(conteudo).hexdigest() != manifesto.get("sha256", {}).get(nome):
            raise ErroArquivo(f"{nome} não confere com o manifesto: arquivo corrompido ou alterado")
    try:
        return manifesto, _dict_para_rastreio(json.loads(brutos["rastreio.json"]))
    except (KeyError, TypeError, ValueError) as erro:
        # Hash confere mas o conteúdo não tem a forma esperada: arquivo montado à mão.
        raise ErroArquivo(f"rastreio.json com conteúdo inválido: {erro!r}") from None
```

⚠️ **O SHA-256 do manifesto pega corrupção, não fraude.** Quem altera o caso de propósito pode recalcular os hashes. Não venda o `.rchain` como "à prova de adulteração": essa garantia vem na Parte 6, com o selo de tempo do laudo.

⚠️ **O `.rchain` vem de fora, então é lido com desconfiança.** O código lê só as três partes que conhece, pelo nome, nunca extrai nada para o disco (um ZIP malicioso pode tentar gravar fora da pasta) e recusa parte acima de 200 MB (um ZIP pequeno pode descompactar em gigabytes).

⚠️ **`VERSAO_FORMATO` é promessa.** Quando o conteúdo mudar, ela sobe, e a versão nova do programa continua abrindo os casos antigos. Um cliente com 300 casos salvos não pode perder nenhum numa atualização.

### Passo 12 — 📄 `rastrochain/__main__.py`

O núcleo pela linha de comando, com dois comandos: `rastrear` (vai à rede) e `abrir` (reabre um `.rchain`, sem rede nenhuma).

```python
"""O núcleo pela linha de comando.

    python -m rastrochain rastrear <endereço> [--saltos 2] [--direcao saida]
                     [--minimo 10] [--desde 2026-01-01] [--salvar saidas/caso.rchain]
                     [--grafo saidas/caso.html]
    python -m rastrochain abrir saidas/caso.rchain [--grafo saidas/caso.html]
"""
import argparse
import sys
from datetime import datetime, timezone
from decimal import Decimal

from rastrochain import arquivo
from rastrochain.arquivo import ErroArquivo
from rastrochain.grafo import salvar_html, salvar_json
from rastrochain.rastreio import rastrear
from rastrochain.redes.tron import ClienteTron, ErroTron, endereco_valido


def _data(texto):
    return datetime.strptime(texto, "%Y-%m-%d").replace(tzinfo=timezone.utc)


def main(argv=None):
    p = argparse.ArgumentParser(prog="rastrochain")
    sub = p.add_subparsers(dest="comando", required=True)
    r = sub.add_parser("rastrear", help="segue o USDT de um endereço na Tron")
    r.add_argument("endereco")
    r.add_argument("--saltos", type=int, default=2)
    r.add_argument("--direcao", choices=["saida", "entrada"], default="saida")
    r.add_argument("--minimo", type=Decimal, default=Decimal("1"),
                   help="ignora transferências abaixo deste valor em USDT")
    r.add_argument("--desde", type=_data, help="AAAA-MM-DD")
    r.add_argument("--ate", type=_data, help="AAAA-MM-DD")
    r.add_argument("--por-endereco", type=int, default=200)
    r.add_argument("--salvar", help="grava o caso num arquivo .rchain")
    r.add_argument("--grafo", help="grava o grafo num HTML que abre no navegador")
    r.add_argument("--json", help="grava o grafo em JSON (nós e arestas)")
    r.add_argument("--caso", default="", help="nome do caso")
    a = sub.add_parser("abrir", help="reabre um caso .rchain")
    a.add_argument("arquivo")
    a.add_argument("--grafo", help="grava o grafo num HTML que abre no navegador")
    a.add_argument("--json", help="grava o grafo em JSON (nós e arestas)")
    args = p.parse_args(argv)
    if args.comando == "abrir":
        return _abrir(args)

    if not endereco_valido(args.endereco):
        print(f"✗ endereço Tron inválido: {args.endereco}", file=sys.stderr)
        return 2
    try:
        resultado = rastrear(ClienteTron(), args.endereco, saltos=args.saltos,
                             direcao=args.direcao, valor_minimo=args.minimo,
                             desde=args.desde, ate=args.ate,
                             por_endereco=args.por_endereco)
    except ErroTron as erro:
        print(f"✗ a TronGrid não respondeu: {erro}", file=sys.stderr)
        return 1

    _resumo(resultado)
    if args.salvar:
        parametros = {"minimo": str(args.minimo), "por_endereco": args.por_endereco,
                      "desde": args.desde and args.desde.date().isoformat(),
                      "ate": args.ate and args.ate.date().isoformat()}
        print(f"  ✓ caso: {arquivo.salvar(resultado, args.salvar, args.caso, parametros)}")
    _saidas(resultado, args, args.caso)
    return 0


def _abrir(args):
    try:
        manifesto, resultado = arquivo.abrir(args.arquivo)
    except ErroArquivo as erro:
        print(f"✗ {erro}", file=sys.stderr)
        return 1
    caso = manifesto.get("caso") or ""
    print(f"Caso {caso or '(sem nome)'} · gerado em {manifesto.get('gerado_em')} "
          f"por {manifesto.get('gerado_por')} · parâmetros {manifesto.get('parametros')}")
    _resumo(resultado)
    _saidas(resultado, args, caso)
    return 0


def _resumo(resultado):
    print(f"Rastreio de {resultado.inicio} ({resultado.direcao}, {resultado.saltos} saltos)")
    print(f"  {len(resultado.transferencias)} transferências, "
          f"{len(resultado.salto_de) - 1} endereços alcançados")
    for salto, total in resultado.total_por_salto().items():
        print(f"  salto {salto}: {total:,.2f} USDT")
    if resultado.truncados:
        print(f"  ⚠ {len(resultado.truncados)} endereço(s) bateram no teto — "
              "provável corretora ou carteira muito movimentada:")
        for e in sorted(resultado.truncados):
            print(f"    {e}")


def _saidas(resultado, args, caso):
    if args.grafo:
        print(f"  ✓ grafo: {salvar_html(resultado, args.grafo, caso)}")
    if args.json:
        print(f"  ✓ JSON: {salvar_json(resultado, args.json)}")


if __name__ == "__main__":
    sys.exit(main())
```

### Passo 13 — 📄 Os testes

Quatro arquivos em `testes/`, mais um `testes/__init__.py` **vazio**: é ele que deixa um teste importar o exemplo do outro (`from testes.test_grafo import rastreio_exemplo`). Nenhum deles usa a rede: a TronGrid é trocada por uma `FonteFalsa` que devolve o que o teste mandar.

📄 `testes/test_tron.py`

```python
"""O cliente da Tron, sem rede: validação de endereço e leitura do formato."""
from decimal import Decimal

from rastrochain import config
from rastrochain.redes.tron import _converter, endereco_valido


def test_endereco_do_contrato_usdt_e_valido():
    assert endereco_valido(config.USDT_TRON)


def test_uma_letra_trocada_e_recusada():
    trocado = config.USDT_TRON[:-1] + ("u" if config.USDT_TRON[-1] != "u" else "v")
    assert not endereco_valido(trocado)


def test_formatos_errados_sao_recusados():
    for errado in ["", "T123", "0x" + "a" * 40, config.USDT_TRON + "x", None]:
        assert not endereco_valido(errado)


def _item(contrato=config.USDT_TRON, valor="36680000"):
    return {"transaction_id": "abc", "type": "Transfer", "value": valor,
            "from": "Torigem", "to": "Tdestino", "block_timestamp": 1790301963000,
            "token_info": {"symbol": "USDT", "address": contrato, "decimals": 6}}


def test_valor_vem_em_unidades_do_token():
    t = _converter(_item())
    assert t.valor == Decimal("36.68")
    assert t.momento.tzinfo is not None


def test_token_falso_com_nome_usdt_e_descartado():
    assert _converter(_item(contrato="TFalsoFalsoFalsoFalsoFalsoFalsoXY")) is None
```

📄 `testes/test_rastreio.py`

```python
"""O rastreio com uma fonte falsa: as três travas, sem depender da rede."""
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from rastrochain.modelos import Transferencia
from rastrochain.rastreio import rastrear

T0 = datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc)


def tr(origem, destino, valor, minutos, hash_=None):
    return Transferencia("tron", "USDT", hash_ or f"{origem}{destino}{minutos}",
                         origem, destino, Decimal(valor), T0 + timedelta(minutes=minutos))


class FonteFalsa:
    """Faz o papel da TronGrid: devolve o que estiver na lista, com os filtros dela."""

    def __init__(self, transferencias):
        self.todas = transferencias
        self.chamadas = []

    def transferencias_usdt(self, endereco, direcao="saida", desde=None, ate=None, limite=200):
        self.chamadas.append(endereco)
        lado = (lambda t: t.origem == endereco) if direcao == "saida" else (lambda t: t.destino == endereco)
        lista = [t for t in self.todas if lado(t)
                 and (desde is None or t.momento >= desde)
                 and (ate is None or t.momento <= ate)]
        return sorted(lista, key=lambda t: t.momento, reverse=True)[:limite]


def test_segue_dois_saltos_para_a_frente():
    fonte = FonteFalsa([tr("VITIMA", "A", 1000, 0), tr("A", "B", 900, 10), tr("B", "C", 800, 20)])
    r = rastrear(fonte, "VITIMA", saltos=2)
    assert r.salto_de == {"VITIMA": 0, "A": 1, "B": 2}
    assert "C" not in r.salto_de                      # o terceiro salto não foi pedido


def test_poeira_abaixo_do_minimo_nao_entra():
    fonte = FonteFalsa([tr("VITIMA", "A", 1000, 0), tr("VITIMA", "POEIRA", "0.01", 1)])
    r = rastrear(fonte, "VITIMA", saltos=1, valor_minimo=Decimal("1"))
    assert "POEIRA" not in r.salto_de


def test_dinheiro_nao_sai_antes_de_chegar():
    # A mandou para X ANTES de receber da vítima: não é o dinheiro do caso.
    fonte = FonteFalsa([tr("A", "X", 500, -60), tr("VITIMA", "A", 1000, 0), tr("A", "B", 900, 10)])
    r = rastrear(fonte, "VITIMA", saltos=2)
    assert "B" in r.salto_de
    assert "X" not in r.salto_de


def test_para_tras_encontra_a_origem():
    fonte = FonteFalsa([tr("ORIGEM", "MEIO", 2000, 0), tr("MEIO", "GOLPISTA", 1900, 30)])
    r = rastrear(fonte, "GOLPISTA", saltos=2, direcao="entrada")
    assert r.salto_de == {"GOLPISTA": 0, "MEIO": 1, "ORIGEM": 2}


def test_teto_por_endereco_marca_como_truncado():
    muitas = [tr("CORRETORA", f"D{i}", 10, i) for i in range(5)]
    fonte = FonteFalsa([tr("VITIMA", "CORRETORA", 1000, -1)] + muitas)
    r = rastrear(fonte, "VITIMA", saltos=2, por_endereco=3)
    assert "CORRETORA" in r.truncados


def test_total_por_salto():
    fonte = FonteFalsa([tr("V", "A", 100, 0), tr("V", "B", 50, 1), tr("A", "C", 90, 5)])
    r = rastrear(fonte, "V", saltos=2)
    assert r.total_por_salto() == {1: Decimal(150), 2: Decimal(90)}
```

📄 `testes/test_grafo.py`

```python
"""O grafo: arestas somadas, marcas nos nós e o HTML que não quebra."""
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from rastrochain.grafo import montar, salvar_html
from rastrochain.modelos import Transferencia
from rastrochain.rastreio import Rastreio

T0 = datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc)


def rastreio_exemplo():
    r = Rastreio(inicio="TA", direcao="saida", saltos=2)
    r.salto_de = {"TA": 0, "TB": 1, "TC": 2}
    r.truncados = {"TC"}
    r.transferencias = [
        Transferencia("tron", "USDT", "h1", "TA", "TB", Decimal("1000.5"), T0),
        Transferencia("tron", "USDT", "h2", "TA", "TB", Decimal("234"), T0 + timedelta(hours=1)),
        Transferencia("tron", "USDT", "h3", "TB", "TC", Decimal("1200"), T0 + timedelta(hours=2)),
    ]
    return r


def test_mesmo_par_vira_uma_aresta_com_total():
    g = montar(rastreio_exemplo())
    assert len(g["arestas"]) == 2
    ab = next(a for a in g["arestas"] if a["destino"] == "TB")
    assert ab["total"] == "1234.5" and ab["quantidade"] == 2
    assert ab["hashes"] == ["h1", "h2"]
    assert ab["rotulo"] == "1.234,50 USDT (2x)"


def test_nos_marcados():
    nos = {n["id"]: n for n in montar(rastreio_exemplo())["nos"]}
    assert nos["TA"]["inicio"] and not nos["TB"]["inicio"]
    assert nos["TC"]["truncado"]
    assert nos["TB"]["recebido"] == "1234.5" and nos["TB"]["enviado"] == "1200"


def test_html_nao_deixa_fechar_o_script(tmp_path):
    arquivo = salvar_html(rastreio_exemplo(), tmp_path / "g.html", titulo="caso </script>")
    html = arquivo.read_text(encoding="utf-8")
    assert html.count("</script>") == 2          # só a do CDN e a nossa
    assert '"TA"' in html
```

📄 `testes/test_arquivo.py`

```python
"""O .rchain: salva e reabre igual, e recusa o que não confere."""
import zipfile

import pytest

from rastrochain.arquivo import ErroArquivo, abrir, salvar
from testes.test_grafo import rastreio_exemplo


def test_salva_e_reabre_igual(tmp_path):
    original = rastreio_exemplo()
    arquivo = salvar(original, tmp_path / "caso", caso="CASO-7", parametros={"minimo": "50"})
    assert arquivo.name == "caso.rchain"                   # a extensão entra sozinha
    manifesto, reaberto = abrir(arquivo)
    assert manifesto["caso"] == "CASO-7" and manifesto["parametros"] == {"minimo": "50"}
    assert reaberto.transferencias == original.transferencias   # Decimal e data exatos
    assert reaberto.salto_de == original.salto_de and reaberto.truncados == original.truncados


def test_parte_alterada_e_recusada(tmp_path):
    arquivo = salvar(rastreio_exemplo(), tmp_path / "caso.rchain")
    with zipfile.ZipFile(arquivo) as z:
        partes = {n: z.read(n) for n in z.namelist()}
    partes["rastreio.json"] = partes["rastreio.json"].replace(b"1000.5", b"9000.5")
    with zipfile.ZipFile(arquivo, "w") as z:
        for nome, conteudo in partes.items():
            z.writestr(nome, conteudo)
    with pytest.raises(ErroArquivo, match="não confere"):
        abrir(arquivo)


def test_arquivo_qualquer_e_recusado(tmp_path):
    falso = tmp_path / "foto.rchain"
    falso.write_bytes(b"isto nao e um zip")
    with pytest.raises(ErroArquivo):
        abrir(falso)
```

▶️ **Rode os testes:**

```bash
docker compose run --rm app pytest -q
```

✅ **Conferência:** `17 passed`.

▶️ **Rode o primeiro caso de verdade** (uma carteira pública movimentada, dois saltos, ignorando o que for menor que 50 USDT):

```bash
docker compose run --rm app python -m rastrochain rastrear TGVn9kTn7P5ystdi6SC6KXjXqps5RmmAwk \
    --saltos 2 --minimo 50 --salvar saidas/teste --grafo saidas/teste.html --caso TESTE
docker compose run --rm app python -m rastrochain abrir saidas/teste.rchain
open saidas/teste.html
```

✅ **Conferência:**

- O primeiro comando lista o total por salto, avisa quais endereços bateram no teto e termina com `✓ caso: saidas/teste.rchain` e `✓ grafo: saidas/teste.html`. Os números mudam a cada dia: a carteira continua movimentando.
- O segundo reabre o caso **sem rede** e mostra o mesmo resumo, mais a data de geração e os parâmetros usados.
- O `open` abre o grafo no navegador: a carteira inicial em vermelho à esquerda, uma coluna por salto, as prováveis corretoras em laranja. Clicar numa carteira ou numa seta mostra valores, período e hashes.

⚠️ **`saidas/` está no `.gitignore` de propósito.** Caso de cliente é dado sensível e nunca vai para o repositório, nem os de teste.

⚠️ **Datas são UTC em todo lugar.** `--desde 2026-09-01` começa às 21h do dia 31 de agosto em Brasília. No laudo (Parte 6), a conversão para o horário de Brasília aparece ao lado, nunca no lugar.

Com isso, a Parte 1 está fechada: o núcleo rastreia, desenha e guarda o caso. Hora de um `git add . && git commit -m "Parte 1: núcleo"`.

## Roteiro das próximas partes

Cada parte entra na apostila quando a anterior estiver rodando na sua máquina, no mesmo formato: arquivo inteiro, conferência, armadilhas. A Parte 1 não muda; as seguintes só a usam.

| parte | o que entra | pronto quando |
| --- | --- | --- |
| 2 — Banco e API | Postgres no compose, SQLAlchemy 2 + Alembic, cache das transferências já buscadas, FastAPI com `POST /rastreios` e `GET /casos/{id}` | o mesmo rastreio da Parte 1 sai pela API, e a segunda vez vem do cache, sem chamar a TronGrid |
| 3 — A tela | Jinja + HTMX, o grafo da Parte 1 dentro da página, expandir uma carteira com um clique, abrir e baixar o `.rchain` | colar um endereço e ver o grafo crescer salto a salto |
| 4 — Contas | login com senha forte e 2FA (TOTP), empresa → usuários → perfis, cada caso preso à empresa, trilha de auditoria de quem viu o quê | um usuário de outra empresa recebe 404 no caso, e a auditoria registra a tentativa |
| 5 — Rótulos | carteiras conhecidas das corretoras que operam no Brasil, lista de sanções da OFAC, denúncias; os nós laranja ganham nome | o rastreio de teste mostra "provável corretora X" com a fonte do rótulo |
| 6 — Laudo | PDF em português com grafo, tabela de saltos, hashes e horário de Brasília ao lado do UTC; selo OpenTimestamps no `.rchain` e no PDF | alterar um byte do laudo faz a verificação do selo falhar |
| 7 — Vigia | carteiras observadas, checagem periódica, alerta por e-mail quando o dinheiro se mexe | mover USDT numa carteira de teste gera o alerta em minutos |
| 8 — Outras redes | USDT na Ethereum (mesma `Transferencia`, outra fonte) e Bitcoin (modelo de saídas, que muda a regra de "quem mandou") | o mesmo teste da Parte 1 passa trocando só a fonte |
| 9 — Produção | servidor, HTTPS, backup do banco e dos `.rchain`, monitoramento, limites por plano | um cliente de teste usa sozinho, do cadastro ao laudo |

O MVP vendável fecha na Parte 6. As Partes 7 a 9 são o que faz o cliente renovar.

## Como tocamos juntos

Você digita, eu reviso e escrevo a próxima parte. O ritmo é o seu.

- **Travou num passo?** Cole no chat o comando, a saída inteira e o número do passo. Com o erro exato eu acho a diferença em minutos; com "não funcionou", não.
- **Terminou uma parte?** Me diga a pasta do projeto. Eu rodo os testes em Docker, comparo com a apostila e aponto o que mudou. Mudança sua que ficou melhor entra na apostila.
- **Dúvida de conceito** (por que `Decimal`, por que UTC, como funciona o SHA-256): comentário direto no trecho da apostila. A resposta fica ali, para você e para quem entrar no time depois.
- **Quer mudar o rumo** (outra rede primeiro, outra tela, outro formato)? Decidimos antes de escrever. Nada da apostila muda sem você pedir.

Quando a Parte 1 rodar aí, com `17 passed` e o grafo abrindo, me avise e eu escrevo a Parte 2.

## Para estudar

A apostila ensina o RastroChain; estes livros ensinam o terreno em volta. Ordem sugerida: Mastering Bitcoin (capítulos 1 a 6), Investigating Cryptocurrencies, Programming Bitcoin junto com a Parte 1 e Tracers in the Dark como leitura leve. Disponibilidade no Kindle e edição em português variam: confira na loja.

**Desenvolvedor**

| livro | por que ler | serve para |
| --- | --- | --- |
| Mastering Bitcoin, 3ª ed. (Antonopoulos e Harding) | transações, endereços, chaves e UTXO; gratuito no GitHub dos autores, em inglês | base de tudo |
| Programming Bitcoin (Jimmy Song) | constrói uma biblioteca de Bitcoin do zero, em Python | Parte 8 (Bitcoin) |
| Mastering Ethereum (Antonopoulos e Wood) | contratos, tokens ERC-20 e eventos; o USDT é um contrato e a Tron copia o modelo; gratuito no GitHub | Partes 1 e 8 |
| Grokking Bitcoin (Kalle Rosenbaum) | os mesmos conceitos com muitos diagramas | fixar a base |
| Bitcoin and Cryptocurrency Technologies (Princeton) | anonimato e desanonimização, a teoria do rastreio; PDF gratuito | Partes 5 e 8 |

**Forense e investigação**

| livro | por que ler | serve para |
| --- | --- | --- |
| Investigating Cryptocurrencies (Nick Furneaux) | manual prático: rastrear, atribuir carteiras e documentar para a Justiça | Parte 6 (laudo) |
| Tracers in the Dark (Andy Greenberg) | casos reais em que investigadores quebraram o anonimato | entender o cliente |
| Number Go Up (Zeke Faux) | a Tether e o golpe "pig butchering", que termina em USDT na Tron | entender o golpe que o produto rastreia |
| Graph Algorithms (Needham e Hodler) | centralidade, comunidades e caminhos em grafos; a Neo4j costuma distribuir de graça | agrupamento de carteiras |

Fora do Kindle e gratuito: o **Crypto Crime Report** anual da Chainalysis, com os números e as tipologias de golpe que o laudo vai citar.
