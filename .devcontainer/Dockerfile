FROM mcr.microsoft.com/devcontainers/python:3.14

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# tox-uv fetches the other interpreters on demand
ENV UV_PYTHON_DOWNLOADS=automatic
