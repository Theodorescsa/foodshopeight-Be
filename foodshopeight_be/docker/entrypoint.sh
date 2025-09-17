#!/usr/bin/env bash
set -e

# Optional: chờ DB nếu dùng DB ngoài (sửa host/port nếu cần)
if [ -n "$WAIT_FOR_HOST" ] && [ -n "$WAIT_FOR_PORT" ]; then
  echo "Waiting for $WAIT_FOR_HOST:$WAIT_FOR_PORT ..."
  until nc -z "$WAIT_FOR_HOST" "$WAIT_FOR_PORT"; do
    sleep 1
  done
fi

# Migrate & collectstatic (idempotent)
python manage.py migrate --noinput
python manage.py collectstatic --noinput || true

# Chạy đúng role theo biến CONTAINER_ROLE
# web / worker / beat
case "$CONTAINER_ROLE" in
  "worker")
    echo "Starting Celery worker..."
    exec celery -A foodshopeight_be worker -l info -Q default,posting,background
    ;;
  "beat")
    echo "Starting Celery beat..."
    exec celery -A foodshopeight_be beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    ;;
  *)
    echo "Starting Gunicorn web..."
    exec gunicorn foodshopeight_be.wsgi:application \
      --bind 0.0.0.0:8000 \
      --workers ${GUNICORN_WORKERS:-3} \
      --threads ${GUNICORN_THREADS:-2} \
      --timeout 120
    ;;
esac
