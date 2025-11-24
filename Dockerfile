# Lightweight runtime image capable of running both pipelines
FROM python:3.12-slim AS runtime

# System deps for DB drivers and some Python wheels (pyodbc, psycopg2, etc.)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ca-certificates \
       curl \
       gnupg \
       build-essential \
       gcc \
       g++ \
       unixodbc \
       unixodbc-dev \
       libpq5 \
         libpq-dev \
       unzip \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get update \
    && (apt-get install -y --no-install-recommends libaio1 || apt-get install -y --no-install-recommends libaio1t64) \
    && rm -rf /var/lib/apt/lists/*

# Install Microsoft ODBC Driver 18 for SQL Server and tooling
RUN set -eux; \
    mkdir -p /etc/apt/keyrings; \
    curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /etc/apt/keyrings/microsoft.gpg; \
    chmod a+r /etc/apt/keyrings/microsoft.gpg; \
    echo "deb [arch=amd64,arm64 signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list; \
    apt-get update; \
    ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 mssql-tools18; \
    rm -rf /var/lib/apt/lists/*
ENV PATH="/opt/mssql-tools18/bin:${PATH}"

# Set working directory
WORKDIR /app

# Install uv (Python package manager); install packages
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY pyproject.toml uv.lock LICENSE.md README.md ./
# Try to sync with lock; if lock is out-of-date, regenerate and sync
RUN (uv sync --locked) || (uv lock --upgrade && uv sync --locked)

# Copy the rest of the project
COPY . .

# Ensure a data directory exists for parquet dumps and allow host mount
RUN mkdir -p /app/data
VOLUME ["/app/data"]

# Optional: install Oracle Instant Client at build time if a URL is provided
# Provide a direct download URL via build-arg ORACLE_IC_URL and directory name via ORACLE_IC_DIR.
ARG ORACLE_IC_URL=""
ARG ORACLE_IC_DIR="instantclient_21_12"
RUN if [ -n "$ORACLE_IC_URL" ]; then \
            set -eux; \
            mkdir -p /opt/oracle; \
            cd /opt/oracle; \
            curl -L "$ORACLE_IC_URL" -o ic.zip; \
            unzip -q ic.zip; \
            rm ic.zip; \
            echo "Installed Oracle Instant Client into /opt/oracle"; \
        else \
            echo "Skipping Oracle Instant Client (no ORACLE_IC_URL provided)"; \
        fi
ENV ORACLE_IC_DIR=${ORACLE_IC_DIR}
# Set library path to Oracle client dir if present; won't break if missing
ENV LD_LIBRARY_PATH="/opt/oracle/${ORACLE_IC_DIR}"

# Add a user-friendly entrypoint to choose the module
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Default to source-to-staging; override by passing a first arg or PIPELINE env
ENV PIPELINE=source-to-staging
# Ensure the venv Python is on PATH and top-level packages are importable
ENV PATH="/app/.venv/bin:${PATH}"
ENV PYTHONPATH="/app"
ENTRYPOINT ["/entrypoint.sh"]

# Example overrides:
# docker run --rm ggmpilot staging-to-silver -c staging_to_silver/config.ini
