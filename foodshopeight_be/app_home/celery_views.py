import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .tasks import background_job

class DoWorkView(APIView):
    def post(self, request):
        # Nhận payload từ client
        payload = request.data or {}
        # Tạo job_id (hoặc client gửi lên để idempotent theo nghiệp vụ)
        job_id = payload.get("job_id") or uuid.uuid4().hex

        # Đẩy vào Celery (queue 'background' theo routes)
        res = background_job.apply_async(args=[job_id, payload])

        return Response(
            {"accepted": True, "job_id": job_id, "task_id": res.id},
            status=status.HTTP_202_ACCEPTED
        )
