# syntax=docker/dockerfile:1

# =============================================================================
# Hotel Booking API - Dockerfile (multi-stage, otimizado)
# Build:  docker build -t hotel-booking-api:1.0.0 --build-arg APP_VERSION=1.0.0 .
# Run:    docker run -p 8000:8000 hotel-booking-api:1.0.0
# =============================================================================

ARG PYTHON_VERSION=3.12

# -----------------------------------------------------------------------------
# Stage 1 - builder: instala as dependências em um virtualenv isolado
# -----------------------------------------------------------------------------
FROM python:${PYTHON_VERSION}-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copia só o requirements.txt primeiro para aproveitar o cache de camadas:
# a instalação só é refeita quando as dependências mudam.
COPY requirements.txt .
RUN pip install -r requirements.txt

# -----------------------------------------------------------------------------
# Stage 2 - runtime: imagem final enxuta, sem ferramentas de build
# -----------------------------------------------------------------------------
FROM python:${PYTHON_VERSION}-slim AS runtime

ARG APP_VERSION=dev
ARG VCS_REF=unknown

LABEL org.opencontainers.image.title="hotel-booking-api" \
      org.opencontainers.image.description="API REST de reserva de quartos de hotel (FastAPI)" \
      org.opencontainers.image.version="${APP_VERSION}" \
      org.opencontainers.image.revision="${VCS_REF}"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    APP_VERSION=${APP_VERSION} \
    DATABASE_URL="sqlite:////data/hotel.db"

# Usuário sem privilégios (não rodar como root)
RUN groupadd --system --gid 1001 app \
 && useradd  --system --uid 1001 --gid app --home-dir /app --no-create-home --shell /usr/sbin/nologin app \
 && mkdir -p /app /data \
 && chown -R app:app /app /data

WORKDIR /app

# Dependências já instaladas no stage anterior
COPY --from=builder /opt/venv /opt/venv

# Código da aplicação (o que não é necessário é filtrado pelo .dockerignore)
COPY --chown=app:app app ./app
COPY --chown=app:app static ./static

USER app

# Dados do SQLite persistem aqui quando montado um volume (-v hotel-data:/data)
VOLUME ["/data"]

EXPOSE 8000

# Healthcheck usando o endpoint /health (python já está na imagem; não precisa de curl)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).status == 200 else 1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
