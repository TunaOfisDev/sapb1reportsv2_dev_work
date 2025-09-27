# backend/authcentral/middleware.py
from django.http import JsonResponse
from .models import BlacklistedToken

class CheckBlacklistedTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Token kontrolü
        header = request.META.get('HTTP_AUTHORIZATION')
        if header:
            token = header.split()[1]
            if BlacklistedToken.objects.filter(token=token).exists():
                return JsonResponse({'error': 'Token blacklisted'}, status=401)

        response = self.get_response(request)
        return response
