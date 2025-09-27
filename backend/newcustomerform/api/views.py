# backend/newcustomerform/api/views.py
from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated  # Eklendi
import json
from newcustomerform.models.models import NewCustomerForm, AuthorizedPerson
from .serializers import NewCustomerFormSerializer, AuthorizedPersonSerializer
from mailservice.services.send_new_customer_form_mail import NewCustomerFormMailService  

class NewCustomerFormCreateAPIView(generics.CreateAPIView):
    queryset = NewCustomerForm.objects.all()
    serializer_class = NewCustomerFormSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            data = request.data.copy()
            
            # Yetkili kişileri işle
            yetkili_kisiler_data = data.get('yetkili_kisiler', '[]')
            if isinstance(yetkili_kisiler_data, str):
                try:
                    yetkili_kisiler_data = json.loads(yetkili_kisiler_data)
                except json.JSONDecodeError:
                    return Response(
                        {"error": "Yetkili kişiler verisi geçersiz format"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                instance = serializer.save(created_by=request.user)
                
                # Yetkili kişileri ekle
                for yetkili_data in yetkili_kisiler_data:
                    AuthorizedPerson.objects.create(
                        new_customer_form=instance,
                        **yetkili_data
                    )

                # Mail gönderme işlemi
                mail_service = NewCustomerFormMailService()
                mail_sent = mail_service.send_mail(customer_form=instance, created_by=request.user)
                
                # Alternatif olarak, mail log durumunu sorgulayarak kesin sonuç alabilirsiniz:
                from newcustomerform.models.models import NewCustomerForm  # veya ilgili import
                from mailservice.models.models import MailLog
                mail_log = MailLog.objects.filter(
                    related_object_type='NewCustomerForm',
                    related_object_id=instance.id
                ).order_by('-created_at').first()
                if mail_log and mail_log.status == 'SENT':
                    mail_sent = True
                else:
                    mail_sent = False

                response_data = {
                    **serializer.data,
                    'mail_status': {
                        'sent': mail_sent,
                        'message': 'Mail başarıyla gönderildi' if mail_sent else 'Mail gönderilemedi'
                    }
                }
                
                return Response(response_data, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response(
                {
                    "error": str(e),
                    "detail": "Form işlenirken bir hata oluştu"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

# ✅ Tüm müşteri formlarını listele (GET /api/v2/newcustomerform/list/)
class NewCustomerFormListAPIView(generics.ListAPIView):
    queryset = NewCustomerForm.objects.all()
    serializer_class = NewCustomerFormSerializer

    def get_queryset(self):
        """
        Müşteri formlarını yetkili kişilerle birlikte getir.
        """
        return NewCustomerForm.objects.prefetch_related('yetkili_kisiler').all()

# ✅ Belirli bir müşteri formunu getir (GET /api/v2/newcustomerform/{id}/)
class NewCustomerFormRetrieveAPIView(generics.RetrieveUpdateAPIView):  # RetrieveAPIView yerine RetrieveUpdateAPIView kullanmalıyız
    queryset = NewCustomerForm.objects.all()
    serializer_class = NewCustomerFormSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Tek bir müşteri formunu yetkili kişilerle birlikte getir.
        """
        return NewCustomerForm.objects.prefetch_related('yetkili_kisiler').all()

# ✅ Belirli bir müşteri formuna bağlı yetkili kişileri listele ve ekle
class AuthorizedPersonListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = AuthorizedPersonSerializer

    def get_queryset(self):
        """
        Belirli bir müşteri formuna ait yetkili kişileri getir.
        """
        new_customer_form_id = self.kwargs['pk']
        return AuthorizedPerson.objects.filter(new_customer_form_id=new_customer_form_id)

    def perform_create(self, serializer):
        """
        Belirli bir müşteri formuna yetkili kişi ekleme.
        """
        new_customer_form_id = self.kwargs['pk']
        new_customer_form = NewCustomerForm.objects.get(id=new_customer_form_id)
        serializer.save(new_customer_form=new_customer_form)



# Yeni: Oturum açmış kullanıcının oluşturduğu formları listeleyen dashboard view'i
class UserNewCustomerFormListAPIView(generics.ListAPIView):
    serializer_class = NewCustomerFormSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_queryset(self):
        # created_by alanının null olup olmadığını kontrol et
        return NewCustomerForm.objects.filter(
            created_by=self.request.user
        ).select_related('created_by').prefetch_related('yetkili_kisiler').order_by('-created_at')