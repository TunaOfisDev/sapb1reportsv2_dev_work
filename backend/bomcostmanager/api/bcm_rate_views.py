# backend/bomcostmanager/api/bcm_rate_views.py
import requests
import logging
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
from django.core.cache import cache

logger = logging.getLogger(__name__)

class ExchangeRateView(APIView):
    """
    Tüm döviz kurlarını getiren API view.
    API: https://api.exchangerate-api.com/v4/latest/TRY
    Önbellek süresi: 6 saat
    """
    
    def get(self, request, *args, **kwargs):
        # Önbellekten döviz kurlarını kontrol et
        cached_rates = cache.get('exchange_rates')
        
        if cached_rates:
            logger.info("Döviz kurları önbellekten alındı.")
            return Response(cached_rates)
        
        try:
            # ExchangeRate API'den verileri al
            response = requests.get("https://api.exchangerate-api.com/v4/latest/TRY", timeout=10)
            
            if not response.ok:
                logger.error(f"ExchangeRate API'ye erişilemedi: {response.status_code}")
                return Response(
                    {"error": f"API'ye erişilemedi: {response.status_code}"}, 
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            data = response.json()
            
            # API'den dönen kurlar TRY bazlı değil (1 TRY = x Döviz),
            # bu yüzden tersini alıyoruz (1 / oran), böylece 1 Döviz = x TRY olur
            try_based_rates = {
                'TRY': 1  # TRY'nin kendi değeri 1
            }
            
            for currency, rate in data['rates'].items():
                if rate > 0:  # Sıfıra bölme hatasını önle
                    try_based_rates[currency] = 1 / rate
                else:
                    try_based_rates[currency] = 0
            
            # Sonuçları önbelleğe al (6 saat)
            cache.set('exchange_rates', try_based_rates, 60 * 60 * 6)
            
            logger.info("Döviz kurları API'den başarıyla alındı.")
            return Response(try_based_rates)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"ExchangeRate API isteği başarısız: {str(e)}")
            return Response(
                {"error": "Döviz kuru servisi şu anda kullanılamıyor."}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            logger.exception(f"Döviz kurları alınırken beklenmeyen hata: {str(e)}")
            return Response(
                {"error": "Beklenmeyen bir hata oluştu."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SingleExchangeRateView(APIView):
    """
    Belirli bir para birimi için döviz kurunu getiren API view.
    URL parametresi: currencyCode (örn: USD, EUR, GBP)
    """
    
    def get(self, request, currency_code, *args, **kwargs):
        if currency_code.upper() == "TRY":
            return Response({"rate": 1})
        
        # Önbellekten tüm kurları kontrol et
        cached_rates = cache.get('exchange_rates')
        
        if cached_rates and currency_code.upper() in cached_rates:
            rate = cached_rates[currency_code.upper()]
            return Response({"rate": rate})
        
        try:
            # ExchangeRate API'den verileri al
            response = requests.get("https://api.exchangerate-api.com/v4/latest/TRY", timeout=10)
            
            if not response.ok:
                logger.error(f"ExchangeRate API'ye erişilemedi: {response.status_code}")
                return Response(
                    {"error": f"API'ye erişilemedi: {response.status_code}"}, 
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            data = response.json()
            
            # İstenen para birimi için kur değerini al
            if currency_code.upper() in data['rates']:
                rate = data['rates'][currency_code.upper()]
                
                # API'den gelen oran TRY bazlı değil, tersini alıyoruz
                try_based_rate = 1 / rate if rate > 0 else 0
                
                # Tüm kurları önbelleğe almak için diğer endpoint tarafından yapılacak
                
                return Response({"rate": try_based_rate})
            else:
                logger.warning(f"{currency_code} için kur bulunamadı.")
                return Response(
                    {"error": f"{currency_code} için kur bulunamadı."}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
        except requests.exceptions.RequestException as e:
            logger.error(f"ExchangeRate API isteği başarısız: {str(e)}")
            return Response(
                {"error": "Döviz kuru servisi şu anda kullanılamıyor."}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            logger.exception(f"Döviz kuru alınırken beklenmeyen hata: {str(e)}")
            return Response(
                {"error": "Beklenmeyen bir hata oluştu."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ExchangeRateLastUpdatedView(APIView):
    """
    Döviz kurlarının son güncellenme zamanını döndüren API view.
    """
    
    def get(self, request, *args, **kwargs):
        # Önbellek anahtarının son değiştirilme zamanını al
        last_updated = cache.get('exchange_rates_last_updated')
        
        if not last_updated:
            # Eğer önbellekte yoksa, şimdiki zamanı kullan ve güncelle
            last_updated = datetime.now().isoformat()
            cache.set('exchange_rates_last_updated', last_updated, 60 * 60 * 24)  # 24 saat
            
        return Response({"last_updated": last_updated})