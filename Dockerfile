# A imagem só traz o Python e as dependências. O CÓDIGO não entra na imagem:
# ele fica na sua pasta e chega ao contêiner pelo volume do docker-compose.
# Assim, salvou o arquivo, rodou de novo — sem reconstruir nada.
FROM python:3.12-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt