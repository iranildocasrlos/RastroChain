# RastroChain

**Follow the money on public blockchains: from a victim's wallet, hop by hop, to where the funds end up.**

RastroChain is a crypto tracing tool focused on the Brazilian scam pattern *Pix → USDT*: a victim pays by Pix, the money is converted into USDT on the Tron network and moved through a chain of wallets. RastroChain reads the public transaction history, rebuilds that path as a graph and saves the whole case in a single verifiable file.

> **Status: work in progress.** This is a learning project, written by hand step by step while studying Python. The core (Tron + graph + case file) is being built now; the API, web UI and reports come later. See the [roadmap](#roadmap).

*Versão em português [mais abaixo](#em-português).*

## What it does

- **Reads only public data.** No private keys, no signing, no sending. It organizes what any block explorer already shows.
- **Traces USDT on Tron (TRC-20)** through the TronGrid API, validating every address checksum before spending an API call.
- **Checks the token contract, not the name.** Anyone can create a token called "USDT"; only the official contract counts.
- **Builds its own graph** (nodes = wallets, edges = transfers) and draws it as an interactive HTML page.
- **Saves each case as a `.rchain` file**: a ZIP with a manifest, the trace and the graph, each part protected by a SHA-256 hash, so a tampered case is detected when it is opened.
- **Bitcoin support** with the usual heuristics: probable change output and common-input ownership.

## Design decisions

| Decision | Why |
| --- | --- |
| Money is `Decimal`, never `float` | `0.1 + 0.2` must be `0.3` in a forensic report |
| Timestamps in UTC | The blockchain has no time zone; conversion happens only on screen |
| Pause and retry on every API call | Respect rate limits (HTTP 429) instead of being blocked |
| Own graph and file format | No dependency on paid analysis software licenses |
| Everything runs in Docker | Same environment on any machine, nothing installed on the host |

## Tech stack

Python 3.12 · httpx · pytest · Docker. Planned: FastAPI, PostgreSQL (SQLAlchemy + Alembic), HTMX, Cytoscape.js.

## Getting started

Requirements: Docker and Docker Compose.

```bash
git clone https://github.com/iranildocasrlos/RastroChain.git
cd RastroChain
cp .env.exemplo .env          # optional: add a free TronGrid API key
docker compose build
docker compose run --rm app pytest
```

The TronGrid key is optional (it only raises the rate limit). It lives in `.env`, which is never committed.

## Project layout

```
rastrochain/
├── config.py        settings from the environment (.env)
├── modelos.py       Transferencia: one transfer, the unit of a trace
├── redes/           one client per network (Tron, Bitcoin, Ethereum)
├── rastreio.py      the money trail, hop by hop
├── grafo.py         graph model and HTML rendering
├── arquivo.py       the .rchain case file
└── __main__.py      command line: python -m rastrochain
testes/              automated tests (pytest)
```

## Roadmap

- [ ] Core: Tron (USDT), trace, graph, `.rchain` file, command line
- [ ] Bitcoin: change detection and common-input ownership
- [ ] Database and REST API (FastAPI + PostgreSQL)
- [ ] Web UI with the interactive graph
- [ ] Pattern alerts: structuring, round trips, exchange deposits
- [ ] PDF report of the trace
- [ ] Ethereum and Monero (payment proof and exchange entry/exit points)

## Responsible use

RastroChain only reads public blockchain data. Tracing results are investigative leads, not proof of identity: a wallet is not a person. Always confirm findings with the exchange or the competent authority before acting on them.

---

## Em português

RastroChain segue o dinheiro em blockchains públicas: parte da carteira da vítima e vai, salto a salto, até onde os valores param. O foco é o golpe comum no Brasil em que o Pix vira USDT na rede Tron.

- Só lê dados públicos: nenhuma chave privada, nenhuma assinatura, nenhum envio.
- Rastreia USDT na Tron pela TronGrid, conferindo o endereço e o contrato oficial do token.
- Monta um grafo próprio e salva o caso num arquivo `.rchain`, com SHA-256 de cada parte.
- Projeto de estudo em andamento, escrito à mão passo a passo. Roda inteiro em Docker.

Para rodar: `cp .env.exemplo .env`, depois `docker compose build` e `docker compose run --rm app pytest`.
