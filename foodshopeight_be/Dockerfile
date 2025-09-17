# ---------- Base image ----------
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    netcat-traditional \
    pkg-config \
    default-libmysqlclient-dev \
    # nếu bạn còn xài Postgres ở đâu đó thì giữ, không thì có thể bỏ:
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# Copy requirements (pip)
# Nếu bạn dùng requirements.txt:
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy project
COPY . /app

# Create dirs for static/media
RUN mkdir -p /app/static_root /app/media

# Collectstatic lúc build (an toàn nếu settings đọc ENV đúng)
# Có thể bỏ nếu muốn collect khi container start
RUN python manage.py collectstatic --noinput || true

# Add entrypoint
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose app port
EXPOSE 8000

# Default command = gunicorn (web)
CMD ["/entrypoint.sh"]
