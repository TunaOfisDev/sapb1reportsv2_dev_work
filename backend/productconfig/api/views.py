# backend/productconfig/api/views.py
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.apps import apps
from rest_framework.exceptions import NotFound
from rest_framework.decorators import action
from ..models import Option, Variant
from .serializers import GenericModelSerializer, OptionSerializer
from ..services import VariantService, QuestionService
import logging

logger = logging.getLogger('productconfig')

class GenericModelViewSet(viewsets.ModelViewSet):
    """
    Tum modeller icin dinamik generic viewset.
    `model_name` parametresi uzerinden ilgili modeli yukler ve islemleri gerceklestirir.
    """
    serializer_class = GenericModelSerializer  # Generic Serializer
    
    def get_queryset(self):
        # URL uzerinden model adi alinir, orn: ?model_name=Brand
        model_name = self.request.query_params.get('model_name')
        if not model_name:
            raise NotFound("Lutfen 'model_name' parametresini belirtin.")
        
        # Modeli dinamik olarak alir
        model = apps.get_model('productconfig', model_name)
        if not model:
            raise NotFound(f"{model_name} modeli bulunamadi.")
        
        # Model bilgisi uzerinden queryset olusturur
        self.serializer_class.Meta.model = model  # Serializer'a modeli set eder
        return model.objects.all()

    def get_serializer(self, *args, **kwargs):
        """
        `model_name` parametresini alarak dinamik olarak serializer baslatir.
        """
        kwargs['model_name'] = self.request.query_params.get('model_name')
        return super().get_serializer(*args, **kwargs)


class ConfigurationViewSet(viewsets.ViewSet):
    """
    Konfigurasyon islemleri icin ozel viewset.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.question_service = QuestionService()
        self.variant_service = VariantService() 
    
    @action(detail=False, methods=['post'])
    def start_configuration(self, request):
        """Yeni bir konfigurasyon baslatir"""
        try:
            initial_question = self.question_service.get_initial_question()
            if not initial_question:
                return Response(
                    {'detail': 'İlk soru bulunamadi.'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            question_data = self.question_service.serialize_question(initial_question)
            return Response({
                "question": question_data,
                "message": "Konfigurasyon baslatildi."
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Konfigurasyon baslatma hatasi: {str(e)}")
            return Response(
                {'detail': f'Hata: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def get_next_question(self, request, pk=None):
        """Belirli bir varyant icin sonraki soruyu getirir"""
        try:
            variant = self.variant_service.get_variant(pk)
            next_question = self.question_service.get_next_question(variant)
            
            if not next_question:
                return Response(
                    {'detail': 'Siradaki soru bulunamadi.'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
                
            question_data = self.question_service.serialize_question(next_question)
            return Response({"question": question_data}, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Sonraki soru getirme hatasi: {str(e)}")
            return Response(
                {'detail': f'Hata: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def process_answer(self, request, pk=None):
        """Varyant icin cevabi isler"""
        try:
            variant = self.variant_service.get_variant(pk)
            answer = request.data.get('answer')
            question_id = request.data.get('question_id')

            if not answer or not question_id:
                return Response(
                    {'detail': 'Cevap ve soru ID gereklidir.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Cevabi isle
            result = self.variant_service.process_answer(variant, question_id, answer)
            return Response({"message": "Cevap islendi.", "result": result}, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Cevap isleme hatasi: {str(e)}")
            return Response(
                {'detail': f'Hata: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VariantViewSet(viewsets.ViewSet):
    """
    Varyant islemleri icin ViewSet.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.variant_service = VariantService()

    def list(self, request):
        try:
            filters = {}
            if request.query_params.get('brand_id'):
                filters['brand_id'] = request.query_params.get('brand_id')
            if request.query_params.get('category_id'):
                filters['category_id'] = request.query_params.get('category_id')
            if request.query_params.get('product_model_id'):
                filters['product_model_id'] = request.query_params.get('product_model_id')
            if request.query_params.get('status'):
                filters['status'] = request.query_params.get('status')

            variants = self.variant_service.get_variant_list(**filters)
            
            variant_list = []
            for variant in variants:
                variant_info = {
                    'id': variant.id,
                    'project_name': variant.project_name,
                    'variant_code': variant.variant_code,
                    'variant_description': variant.variant_description,
                    'total_price': str(variant.total_price),
                    'status': variant.status,
                    'created_at': variant.created_at.isoformat() if variant.created_at else None,
                    'old_component_codes': (
                        variant.old_component_codes
                        if isinstance(variant.old_component_codes, list)
                        else variant.old_component_codes.split(", ") if variant.old_component_codes else []
                    ),
                    # SAP HANA Alanlari
                    'sap_item_code': variant.sap_item_code,
                    'sap_item_description': variant.sap_item_description,
                    'sap_U_eski_bilesen_kod': variant.sap_U_eski_bilesen_kod,
                    'sap_price': str(variant.sap_price) if variant.sap_price else None,
                    'sap_currency': variant.sap_currency
                }
                variant_list.append(variant_info)

            
            return Response({
                'variants': variant_list,
                'total_count': len(variant_list)
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Varyant listesi getirme hatasi: {str(e)}")
            return Response(
                {'detail': f'Hata: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        

    @action(detail=True, methods=['get'])
    def details(self, request, pk=None):
        """Belirli bir varyantin detaylarini getirir"""
        try:
            # Variant detaylarını alın
            variant = self.variant_service.get_variant(pk)
            variant_info = self.variant_service.get_variant_info(variant)

            # Old component codes'u ekleyin
            variant_info['old_component_codes'] = (
                variant.old_component_codes
                if isinstance(variant.old_component_codes, list)
                else variant.old_component_codes.split(", ") if variant.old_component_codes else []
            )

            # SAP HANA Alanlari
            variant_info.update({
                'sap_item_code': variant.sap_item_code,
                'sap_item_description': variant.sap_item_description,
                'sap_U_eski_bilesen_kod': variant.sap_U_eski_bilesen_kod,
                'sap_price': str(variant.sap_price) if variant.sap_price else None,
                'sap_currency': variant.sap_currency
            })

            return Response(variant_info, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Varyant detay getirme hatasi: {str(e)}")
            return Response(
                {'detail': f'Hata: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



    @action(detail=True, methods=['post'], url_path='update-hana-data')
    def update_hana_data(self, request, pk=None):
        """
        Variant ID üzerinden HANA DB'den veri çeker ve kaydeder.
        """
        try:
            # Variant'ı al
            variant = Variant.objects.get(pk=pk)
            variant_code = variant.variant_code

            # Authorization token kontrolü
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            if not token:
                logger.error("Yetkilendirme tokeni eksik.")
                return Response(
                    {'detail': 'Yetkilendirme tokeni eksik.'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # HANA'dan veri güncelle
            success = self.variant_service.update_variant_with_hana_data(variant, token, variant_code)
            if success:
                logger.info(f"Varyant başarıyla güncellendi - ID: {variant.id}")
                return Response(
                    {'message': 'Varyant başarıyla güncellendi.', 'variant_id': pk},
                    status=status.HTTP_200_OK
                )
            else:
                logger.error(f"HANA verisi güncellenemedi - Variant ID: {variant.id}")
                return Response(
                    {'detail': 'HANA verisi güncellenemedi.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Variant.DoesNotExist:
            logger.error(f"Varyant bulunamadı - ID: {pk}")
            return Response(
                {'detail': f'Varyant bulunamadı. ID: {pk}'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"HANA veri güncelleme hatası - Variant ID: {pk}, Hata: {str(e)}")
            return Response(
                {'detail': f'Hata: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



   

class OptionViewSet(viewsets.ModelViewSet):
    """
    Option modeli icin ViewSet.
    Resim yukleme ve CRUD islemlerini yonetir.
    """
    queryset = Option.objects.all()
    serializer_class = OptionSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_serializer_context(self):
        """Serializer'a request context'ini ekle"""
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def create(self, request, *args, **kwargs):
        """Option olusturma islemi"""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        except Exception as e:
            logger.error(f"Option olusturma hatasi: {str(e)}")
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        """Option guncelleme islemi"""
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance,
                data=request.data,
                partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Option guncelleme hatasi: {str(e)}")
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        

class CompletedView(APIView):
    """
    Konfigürasyon tamamlandı bilgilerini dönen view.
    """

    def get(self, request):
        try:
            # Örnek olarak bir varyant ID ile detayları döndür
            variant_id = request.query_params.get('variant_id')
            if not variant_id:
                return Response(
                    {"detail": "Varyant ID gereklidir."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                variant = Variant.objects.get(id=variant_id)
            except Variant.DoesNotExist:
                return Response(
                    {"detail": f"Varyant bulunamadı. ID: {variant_id}"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Varyant bilgilerini döndür
            data = {
                "project_name": variant.project_name,
                "variant_id": variant.id,
                "variant_code": variant.variant_code,
                "description": variant.variant_description,
                "total_price": str(variant.total_price),
                "old_component_codes": (
                    variant.old_component_codes
                    if isinstance(variant.old_component_codes, list)
                    else variant.old_component_codes.split(", ") if variant.old_component_codes else []
                ),
            }
            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Completed endpoint hatası: {str(e)}")
            return Response(
                {"detail": f"Hata: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    
    