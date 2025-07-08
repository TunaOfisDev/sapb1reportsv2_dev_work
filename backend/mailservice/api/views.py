# backend/mailservice/api/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from ..models.models import MailLog
from ..services.send_new_customer_form_mail import NewCustomerFormMailService
from .serializers import MailLogSerializer
from newcustomerform.models.models import NewCustomerForm

class MailLogViewSet(viewsets.ModelViewSet):
   """Mail logları için ViewSet"""
   queryset = MailLog.objects.all()
   serializer_class = MailLogSerializer
   permission_classes = [IsAuthenticated]
   
   def get_queryset(self):
       """Kullanıcıya göre filtrelenmiş queryset"""
       queryset = super().get_queryset()
       if not self.request.user.is_staff:
           queryset = queryset.filter(created_by=self.request.user)
       return queryset
   
   @action(detail=False, methods=['post'], url_path='resend-mail')
   def resend_mail(self, request):
       """Formu yeniden gönder"""
       try:
           form_id = request.data.get('related_object_id')
           if not form_id:
               return Response({
                   'message': 'Form ID gerekli',
                   'success': False
               }, status=status.HTTP_400_BAD_REQUEST)

           try:
               form = NewCustomerForm.objects.get(id=form_id)
           except NewCustomerForm.DoesNotExist:
               return Response({
                   'message': 'Form bulunamadı',
                   'success': False
               }, status=status.HTTP_404_NOT_FOUND)

           service = NewCustomerFormMailService()
           success = service.send_mail(customer_form=form, created_by=request.user)

           if success:
               return Response({
                   'message': 'Mail başarıyla gönderildi',
                   'success': True,
                   'form_id': form_id
               })
           else:
               return Response({
                   'message': 'Mail gönderilemedi',
                   'success': False
               }, status=status.HTTP_400_BAD_REQUEST)

       except Exception as e:
           return Response({
               'message': str(e),
               'success': False
           }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

   @action(detail=False, methods=['post'])
   def resend_failed(self, request):
       """Başarısız mailleri yeniden gönder"""
       failed_mails = MailLog.objects.filter(
           status='FAILED',
           created_by=request.user
       )
       
       success_count = 0
       for mail in failed_mails:
           if mail.mail_type == 'NEW_CUSTOMER_FORM':
               service = NewCustomerFormMailService()
               try:
                   form = NewCustomerForm.objects.get(id=mail.related_object_id)
                   success = service.send_mail(form, request.user)
                   if success:
                       mail.status = 'SENT'
                       mail.sent_at = timezone.now()
                       mail.error_message = None
                       mail.save()
                       success_count += 1
               except Exception as e:
                   mail.error_message = str(e)
                   mail.save()
       
       return Response({
           'message': f'{success_count} mail başarıyla yeniden gönderildi',
           'success_count': success_count,
           'total_count': failed_mails.count()
       })