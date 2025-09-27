# backend/stockcardintegration/utils/exceptions.py

class StockCardIntegrationError(Exception):
    """
    Stok Kartı Entegrasyonu sırasında oluşabilecek genel hata sınıfı.
    """
    def __init__(self, message, status_code=None, response_data=None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)

    def __str__(self):
        error_msg = f"Stock Card Entegrasyonu Hatası: {self.message}"
        if self.status_code:
            error_msg += f" | Status Code: {self.status_code}"
        if self.response_data:
            error_msg += f" | Response: {self.response_data}"
        return error_msg


class StockCardAuthenticationError(StockCardIntegrationError):
    """
    Stok Kartı API için kimlik doğrulama hatası.
    """
    def __init__(self, message="Kimlik doğrulama hatası! Stok Kart API erişimi başarısız.", status_code=401):
        super().__init__(message, status_code)


class StockCardConnectionError(StockCardIntegrationError):
    """
    Stok Kartı API bağlantı hatası.
    """
    def __init__(self, message="Stock Card API'ye bağlantı kurulamadı!", status_code=500):
        super().__init__(message, status_code)


class StockCardTimeoutError(StockCardIntegrationError):
    """
    Stok Kartı API zaman aşımı hatası.
    """
    def __init__(self, message="Stock Card API isteği zaman aşımına uğradı!", status_code=408):
        super().__init__(message, status_code)


class StockCardDataValidationError(StockCardIntegrationError):
    """
    Stok Kartı API'ye gönderilen veride doğrulama hatası.
    """
    def __init__(self, message="Stock Card API'ye gönderilen veride hata var!", status_code=400, response_data=None):
        super().__init__(message, status_code, response_data)


class StockCardNotFoundError(StockCardIntegrationError):
    """
    Stok Kartı API'de ilgili kaynak bulunamadığında fırlatılan hata.
    """
    def __init__(self, message="Stock Card API içinde ilgili veri bulunamadı!", status_code=404):
        super().__init__(message, status_code)
