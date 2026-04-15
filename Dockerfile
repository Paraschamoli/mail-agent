FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS base

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_HTTP_TIMEOUT=300
ENV UV_CONCURRENT_DOWNLOADS=2

# --- THE FIX: Install C compilers and Python headers ---
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*
# -------------------------------------------------------

WORKDIR /app

COPY pyproject.toml uv.lock* ./

# Now when uv sync runs, gcc is available to build ed25519-blake2b
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-dev

COPY . /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

ENV PATH="/app/.venv/bin:${PATH}"

RUN mkdir -p /app/uploads/resumes \
    /app/uploads/cover_letters \
    /app/uploads/other

EXPOSE 8000
EXPOSE 3773

ENTRYPOINT []

CMD ["python", "-m", "main"]