# backend/tunainssupplierpayment/api/closinginvoice_view.py
from datetime import datetime, timedelta
from collections import defaultdict
from decimal import Decimal
from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from rest_framework import status
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction as db_transaction
from ..models.models import SupplierPayment
from ..models.closinginvoice import ClosingInvoice
from loguru import logger

logger.add("logs/backend.log", rotation="1 MB")

@receiver(post_save, sender=SupplierPayment)
@receiver(post_delete, sender=SupplierPayment)
def update_closing_invoice_balance(sender, instance, **kwargs):
    cari_kod = instance.cari_kod
    total_debt = SupplierPayment.objects.filter(cari_kod=cari_kod).aggregate(Sum('borc'))['borc__sum'] or Decimal('0.00')
    total_credit = SupplierPayment.objects.filter(cari_kod=cari_kod).aggregate(Sum('alacak'))['alacak__sum'] or Decimal('0.00')
    total_credit *= -1  # Convert credits to negative
    balance = total_debt + total_credit

    # Eğer bakiye 0 ise, mevcut kaydı sil ve yeni kayıt oluşturma
    if balance == 0:
        ClosingInvoice.objects.filter(cari_kod=cari_kod).delete()
        return  # Info logu kaldırıldı, sadece işlem gerçekleşiyor


    supplier_payment = SupplierPayment.objects.filter(cari_kod=cari_kod).first()
    if supplier_payment:
        cari_ad = supplier_payment.cari_ad
        iban = supplier_payment.iban
        odemekosulu = supplier_payment.odemekosulu
    else:
        cari_ad = 'Unknown'
        iban = None
        odemekosulu = None

    ClosingInvoice.objects.update_or_create(
        cari_kod=cari_kod,
        defaults={
            'current_balance': balance,
            'cari_ad': cari_ad,
            'iban': iban,
            'odemekosulu': odemekosulu
        }
    )

class SupplierPaymentSimulation:
    def __init__(self):
        self.data = defaultdict(lambda: defaultdict(lambda: {'debt': Decimal('0.00'), 'credit': Decimal('0.00')}))
        self.single_transaction_months = defaultdict(lambda: defaultdict(int))
        self.document_transactions = defaultdict(lambda: defaultdict(list))
        self.current_year = str(datetime.now().year)

    def process_transactions(self):
        try:
            # Tüm verileri tek seferde işle, buffer durumunu kontrol et
            all_payments = SupplierPayment.objects.iterator()
            
            for payment in all_payments:
                # Her işlem için yılı kontrol et
                payment_year = datetime.strptime(payment.belge_tarih, "%Y-%m-%d").year
                
                # Eğer işlem güncel yıla ait değilse ve buffer değilse atla
                if str(payment_year) != self.current_year and not payment.is_buffer:
                    continue
                
                self._process_single_transaction(payment)
                
        except Exception as e:
            logger.error(f"Error in process_transactions: {str(e)}")
            raise

    def _process_single_transaction(self, payment):
        try:
            date = datetime.strptime(payment.belge_tarih, "%Y-%m-%d").date()
            year_month = f"{date.year}-{str(date.month).zfill(2)}"
            
            self.data[payment.cari_kod][year_month]['debt'] += payment.borc
            self.data[payment.cari_kod][year_month]['credit'] += payment.alacak * -1
            self.single_transaction_months[payment.cari_kod][year_month] += 1
            self.document_transactions[payment.cari_kod][year_month].append(payment.belge_no)
            
        except Exception as e:
            logger.error(f"Error processing transaction for {payment.cari_kod}: {str(e)}")
            raise

    def generate_payment_list(self):
        try:
            payment_list = []
            current_date = datetime.now()
            
            # Son 4 ayı hesapla
            last_4_months = []
            temp_date = current_date
            
            for _ in range(4):
                last_4_months.append(temp_date.replace(day=1))
                if temp_date.month == 1:
                    temp_date = temp_date.replace(year=temp_date.year-1, month=12, day=1)
                else:
                    temp_date = temp_date.replace(month=temp_date.month-1, day=1)

            last_4_months_keys = [date.strftime("%Y-%m") for date in last_4_months]
            last_4_months_keys.reverse()

            for cari_kod, months in self.data.items():
                try:
                    # Buffer ve güncel verileri birleştirerek işle
                    all_months_sorted = sorted(months.keys())
                    total_credits = []
                    total_debt = Decimal('0.00')

                    for month in all_months_sorted:
                        credit = months[month]['credit']
                        if credit < 0:
                            total_credits.append((month, credit))
                        total_debt += months[month]['debt']

                    monthly_balances = {month: Decimal('0.00') for month in last_4_months_keys}
                    remaining_debt = total_debt
                    oncesi_balance = Decimal('0.00')
                    
                    for month, credit in total_credits:
                        credit_amount = abs(credit)
                        if remaining_debt >= credit_amount:
                            remaining_debt -= credit_amount
                        else:
                            remaining_credit = credit_amount - remaining_debt
                            remaining_debt = Decimal('0.00')
                            if month in last_4_months_keys:
                                monthly_balances[month] = Decimal(-remaining_credit)
                            else:
                                oncesi_balance -= remaining_credit

                    current_balance = oncesi_balance + sum(monthly_balances.values())

                    if current_balance == 0:
                        continue  # Info logu kaldırıldı, işlem aynen devam ediyor


                    # En güncel supplier payment kaydını al (buffer veya değil)
                    supplier_payment = SupplierPayment.objects.filter(
                        cari_kod=cari_kod
                    ).order_by('-belge_tarih').first()

                    if not supplier_payment:
                        logger.warning(f"Cari kod {cari_kod} için SupplierPayment bulunamadı.")
                        continue

                    payment_list.append({
                        'cari_kod': cari_kod,
                        'cari_ad': supplier_payment.cari_ad,
                        'current_balance': float(current_balance),
                        'monthly_balances': {
                            'oncesi': float(oncesi_balance),
                            **{k: float(v) for k, v in monthly_balances.items()}
                        }
                    })

                except Exception as e:
                    logger.error(f"Error processing cari_kod {cari_kod}: {str(e)}")
                    continue

            return payment_list

        except Exception as e:
            logger.error(f"Error in generate_payment_list: {str(e)}")
            raise

    def handle_anomalies(self):
        try:
            # Buffer ve güncel verileri birlikte değerlendir
            for cari_kod, months in self.single_transaction_months.items():
                for month, count in months.items():
                    if count == 1:
                        document_numbers = self.document_transactions[cari_kod][month]
                        if len(document_numbers) == 1:
                            doc_number = document_numbers[0]
                            # Buffer ve güncel verilerden kontrol et
                            doc_transaction = SupplierPayment.objects.filter(
                                cari_kod=cari_kod,
                                belge_no=doc_number
                            ).first()
                            
                            if doc_transaction:
                                total_credit = doc_transaction.alacak
                                if total_credit != 0:
                                    self.data[cari_kod][month]['monthly_balance'] = total_credit

            for cari_kod, months in self.data.items():
                for month, values in months.items():
                    if values['debt'] != 0 and values['credit'] != 0:
                        combined_balance = values['debt'] + values['credit']
                        self.data[cari_kod][month]['monthly_balance'] = combined_balance
                        self.data[cari_kod][month]['debt'] = Decimal('0.00')
                        self.data[cari_kod][month]['credit'] = Decimal('0.00')

            for cari_kod, months in self.document_transactions.items():
                for month, documents in months.items():
                    if len(documents) == 1:
                        doc_number = documents[0]
                        # Buffer ve güncel verilerden kontrol et
                        doc_transactions = SupplierPayment.objects.filter(
                            cari_kod=cari_kod,
                            belge_no=doc_number
                        )
                        
                        total_debt = sum(transaction.borc for transaction in doc_transactions)
                        total_credit = sum(transaction.alacak for transaction in doc_transactions) * -1
                        combined_balance = total_debt + total_credit
                        if combined_balance != 0:
                            self.data[cari_kod][month]['monthly_balance'] = combined_balance

        except Exception as e:
            logger.error(f"Error in handle_anomalies: {str(e)}")
            raise

class SupplierPaymentSimulationView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            simulation = SupplierPaymentSimulation()
            simulation.process_transactions()
            payment_list = simulation.generate_payment_list()

            if payment_list:
                with db_transaction.atomic():
                    ClosingInvoice.objects.all().delete()
                    updated_payment_list = []

                    for item in payment_list:
                        try:
                            if float(item['current_balance']) == 0:
                                continue

                            closing_invoice = ClosingInvoice.objects.create(
                                cari_kod=item['cari_kod'],
                                current_balance=item['current_balance'],
                                monthly_balances=item['monthly_balances']
                            )
                            
                            supplier_payment = SupplierPayment.objects.filter(
                                cari_kod=item['cari_kod']
                            ).order_by('-belge_tarih').first()
                            
                            if supplier_payment:
                                closing_invoice.cari_ad = supplier_payment.cari_ad
                                closing_invoice.iban = supplier_payment.iban
                                closing_invoice.odemekosulu = supplier_payment.odemekosulu
                                closing_invoice.save()

                            updated_payment_list.append({
                                'cari_kod': closing_invoice.cari_kod,
                                'cari_ad': closing_invoice.cari_ad,
                                'current_balance': float(closing_invoice.current_balance),
                                'monthly_balances': closing_invoice.monthly_balances,
                                'iban': closing_invoice.iban,
                                'odemekosulu': closing_invoice.odemekosulu,
                            })

                        except Exception as e:
                            logger.error(f"Error processing item {item['cari_kod']}: {str(e)}")
                            continue

                    if not updated_payment_list:
                        return Response({'message': 'İşlenecek veri bulunamadı.'}, 
                                     status=status.HTTP_404_NOT_FOUND)

                    return JsonResponse(updated_payment_list, safe=False)
            else:
                return Response({'message': 'Veri bulunamadı.'}, 
                             status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            logger.error(f"Error in SupplierPaymentSimulationView: {str(e)}")
            return Response({
                'error': 'İşlem sırasında bir hata oluştu.',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)