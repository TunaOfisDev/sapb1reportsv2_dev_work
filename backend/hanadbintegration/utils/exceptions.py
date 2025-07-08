# backend/hanadbintegration/utils/exceptions.py

class HANADBIntegrationError(Exception):
    """
    HANA DB Entegrasyonu sırasında oluşabilecek genel hata sınıfı.
    """

    def __init__(self, message, status_code=None, response_data=None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)

    def __str__(self):
        error_msg = f"HANA DB Hatası: {self.message}"
        if self.status_code:
            error_msg += f" | Status Code: {self.status_code}"
        if self.response_data:
            error_msg += f" | Response: {self.response_data}"
        return error_msg


class HANADBAuthenticationError(HANADBIntegrationError):
    """
    HANA DB için kimlik doğrulama hatası.
    """
    def __init__(self, message="Kimlik doğrulama hatası! HANA DB oturumu açılamadı.", status_code=401):
        super().__init__(message, status_code)


class HANADBConnectionError(HANADBIntegrationError):
    """
    HANA DB bağlantı hatası.
    """
    def __init__(self, message="HANA DB'ye bağlantı kurulamadı!", status_code=500):
        super().__init__(message, status_code)


class HANADBTimeoutError(HANADBIntegrationError):
    """
    HANA DB zaman aşımı hatası.
    """
    def __init__(self, message="HANA DB isteği zaman aşımına uğradı!", status_code=408):
        super().__init__(message, status_code)


class HANADBDataValidationError(HANADBIntegrationError):
    """
    HANA DB'ye gönderilen veride doğrulama hatası.
    """
    def __init__(self, message="HANA DB'ye gönderilen veride hata var!", status_code=400, response_data=None):
        super().__init__(message, status_code, response_data)


class HANADBNotFoundError(HANADBIntegrationError):
    """
    HANA DB'de ilgili kaynak bulunamadığında fırlatılan hata.
    """
    def __init__(self, message="HANA DB içinde ilgili veri bulunamadı!", status_code=404):
        super().__init__(message, status_code)
