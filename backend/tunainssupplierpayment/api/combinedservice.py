# backend/tunainssupplierpayment/api/combinedservice.py
from django.http import JsonResponse
from rest_framework.views import APIView
from celery.result import AsyncResult
from ..tasks import fetch_and_update_supplier_payments

class CombinedServiceView(APIView):
    def get(self, request, *args, **kwargs):
        token = request.headers.get('Authorization').split(' ')[1]
        task = fetch_and_update_supplier_payments.delay(token)
        return JsonResponse({'task_id': task.id}, status=202)

class TaskStatusView(APIView):
    def get(self, request, task_id, *args, **kwargs):
        task = AsyncResult(task_id)
        if task.state == 'PENDING':
            response = {
                'state': task.state,
                'progress': 0,
                'info': 'Waiting to start...',
            }
        elif task.state != 'FAILURE':
            response = {
                'state': task.state,
                'progress': task.info.get('progress', 0) if task.info else 0,
                'info': task.info.get('description', '') if task.info else 'No progress info available',
            }
        else:
            response = {
                'state': task.state,
                'progress': 0,
                'info': str(task.info),
            }
        return JsonResponse(response)