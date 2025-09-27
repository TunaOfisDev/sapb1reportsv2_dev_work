# backend/orderarchive/paginatio/order_archive_pagination.py
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class OrderArchivePagination(PageNumberPagination):
    """
    OrderArchive için optimize edilmiş sayfalama sınıfı.
    Büyük veri setlerini yönetmek için tasarlanmıştır.
    """

    # Varsayılan sayfa boyutu
    page_size = 100

    # Kullanıcının API'den istekte bulunarak belirleyebileceği maksimum sayfa boyutu
    max_page_size = 1000

    # Sayfa boyutunu dinamik olarak belirlemek için kullanılacak query parametresi
    page_size_query_param = 'page_size'

    # API yanıtını özelleştirmek için sayfalama verisini döner
    def get_paginated_response(self, data):
        return Response({
            'total_items': self.page.paginator.count,  # Toplam veri sayısı
            'total_pages': self.page.paginator.num_pages,  # Toplam sayfa sayısı
            'current_page': self.page.number,  # Şu anki sayfa numarası
            'page_size': self.get_page_size(self.request),  # Sayfa başına kayıt sayısı
            'results': data,  # Sayfadaki veriler
        })
