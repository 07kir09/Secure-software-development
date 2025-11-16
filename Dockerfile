# syntax=docker/dockerfile:1.7

###############################
# Dependency layer
###############################
FROM python:3.11-slim AS deps

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ROOT_USER_ACTION=ignore \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

RUN python -m venv "$VIRTUAL_ENV"

COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt


###############################
# Test/build layer
###############################
FROM deps AS test

COPY requirements-dev.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements-dev.txt

COPY . .

# Provide dummy API token for integration tests
ENV APP_API_TOKEN=test-token

RUN pytest -q


###############################
# Runtime layer
###############################
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Create non-root user and set ownership of the working directory
RUN groupadd --system --gid 1000 appuser \
    && useradd --system --create-home --uid 1000 --gid 1000 --shell /usr/sbin/nologin appuser \
    && chown -R appuser:appuser /app

COPY --from=deps --chown=appuser:appuser /opt/venv /opt/venv

# Copy only runtime artifacts
COPY --chown=appuser:appuser app ./app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD ["python", "-c", "import sys, urllib.request; req = urllib.request.Request('http://localhost:8000/health'); req.add_header('User-Agent', 'healthcheck'); sys.exit(0 if urllib.request.urlopen(req, timeout=2).status == 200 else 1)"]

USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
