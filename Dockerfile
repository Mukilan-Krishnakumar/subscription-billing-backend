FROM python:3.12-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.6.14 /uv /uvx /bin/
ENV PATH="/root/.local/bin/:$PATH"

WORKDIR /core

ENV UV_COMPILE_BYTECODE=1

ENV UV_LINK_MODE=copy

ENV DJANGO_SETTINGS_MODULE=subscription_billing.settings
ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install -y gcc python3-dev libpq-dev gunicorn
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*


RUN mkdir -p /web
RUN mkdir -p /website/static
RUN mkdir -p /website/media