from celery import shared_task
from celery.utils.log import get_task_logger
from django.db import transaction
import os, redis, time, json

logger = get_task_logger(__name__)
r = redis.Redis.from_url(os.environ.get("CELERY_BROKER_URL", "redis://127.0.0.1:6379/0"))

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_jitter=True)
def background_job(self, job_id: str, payload: dict):
    """
    Chạy nền khi API gọi. Nhận job_id (để idempotent) + payload JSON.
    """
    lock = r.lock(f"bg:{job_id}", timeout=600)
    if not lock.acquire(blocking=False):
        # job trùng đang chạy → thử lại sau
        raise self.retry(countdown=15)

    try:
        logger.info(f"[{job_id}] start payload={json.dumps(payload, ensure_ascii=False)}")

        # Nếu API gọi trong transaction DB, nên xếp việc sau khi commit:
        def _do():
            # TODO: xử lý thật ở đây (ví dụ crawl, gọi API ngoài, gửi mail, render report…)
            time.sleep(2)  # giả lập xử lý nặng
            logger.info(f"[{job_id}] done")

        if transaction.get_connection().in_atomic_block:
            transaction.on_commit(_do)
        else:
            _do()

        return {"job_id": job_id, "status": "done"}
    finally:
        try:
            lock.release()
        except Exception:
            pass

@shared_task
def health_check():
    logger.info("health check ok")
    return "ok"
