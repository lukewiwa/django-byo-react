FROM python:3.13

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
COPY --from=ghcr.io/astral-sh/uv:latest /uvx /bin/uvx

RUN uv python install 3.11 3.12 3.14

RUN apt-get update && apt-get install -y --no-install-recommends ssh-client \
    && rm -rf /var/lib/apt/lists/*
