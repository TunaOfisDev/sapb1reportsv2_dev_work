# backend/hanadbintegration/middleware.py

import time
import json
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from .utils.logs import log_hana_request, log_hana_error
from .utils.exceptions import HANADBIntegrationError

class HANADBRequestMiddleware(MiddlewareMixin):
    """
    HANA DB API çağrılarını merkezi olarak loglayan middleware.
    - Tüm gelen istekleri loglar.
    - API performansını ölçer.
    - Hata yönetimi yaparak, düzgün hata yanıtları döndürür.
    """

    def process_request(self, request):
        """
        Gelen isteği yakalayarak loglar.
        """
        request.start_time = time.time()
        log_hana_request(
            request.method,
            request.get_full_path(),
            response_status="REQUESTED",
            response_data={"headers": dict(request.headers), "body": self.get_request_body(request)}
        )

    def process_response(self, request, response):
        """
        Yanıtları loglar ve API performansını ölçer.
        """
        if hasattr(request, "start_time"):
            duration = time.time() - request.start_time
            log_hana_request(
                request.method,
                request.get_full_path(),
                response_status=response.status_code,
                response_data={"duration": f"{duration:.2f}s", "body": self.get_response_body(response)}
            )

        return response

    def process_exception(self, request, exception):
        """
        Hata yönetimi sağlar ve hata loglarını kaydeder.
        """
        log_hana_error(f"API Hatası: {exception}")

        if isinstance(exception, HANADBIntegrationError):
            return JsonResponse(
                {"error": str(exception)},
                status=exception.status_code if hasattr(exception, "status_code") else 500
            )

        return JsonResponse({"error": "Bilinmeyen bir hata oluştu!"}, status=500)

    def get_request_body(self, request):
        """
        İstek gövdesini güvenli bir şekilde alır.
        """
        try:
            if request.body:
                return json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return "Geçersiz JSON"
        return None

    def get_response_body(self, response):
        """
        Yanıt gövdesini güvenli bir şekilde alır.
        """
        try:
            return json.loads(response.content.decode("utf-8"))
        except (json.JSONDecodeError, AttributeError):
            return "Yanıt gövdesi alınamadı"
