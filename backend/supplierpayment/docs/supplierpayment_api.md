burada işlem basit aslında algoritma dinamik olarak cari_kod bazında hareket listesi belge_tarihi ne göre a-z sırası yaptıkdan sonra alacak kapama işlemi yapmalı aslında bunu hareket satıyı gözetmeksizin yapan dinamik bir algoritma olmalı biraz olaya muhasebe mantığı ile bakiye kapama işlem mantığı ile yaklaş. tedarikçin bizden olan alacağını yaşlandırma işlemi ni oncesi ve son 4 ay için yapıyoruz

***************
Tedarikçi ödeme listesi oluşturma algoritması son beş ay için dinamik hesaplama yaparak
tedarikçin alacak hesabının hangi aydan geldiğini göstermek amacı güder. örneğin mart ayında isek
"cari_kod bazında bakiye, mart, şubat, ocak, aralık, öncesi" şeklide tedarikcinin bakiyesi ve aylardan gelen
alacaklarını kapama yaparak gösterir
*************
### SupplierPaymentSimulation Sınıfı Algoritması:

#### 1. Başlatma:
   - `self.data` adlı bir defaultdict yapısı başlatılır. Bu yapı, cari hesap kodlarına göre borç ve alacak bilgilerini saklar.
   - `self.single_transaction_months` adlı bir defaultdict yapısı başlatılır. Bu yapı, cari hesap kodlarına göre tek işlem yapılan ayları saklar.
   - `self.document_transactions` adlı bir defaultdict yapısı başlatılır. Bu yapı, cari hesap kodlarına göre belge numaralarını saklar.

#### 2. İşlemleri İşleme:
   - `process_transactions` fonksiyonu, tüm `SupplierPayment` nesnelerini döngüye alır.
   - Her ödeme için, belge tarihi alınır ve `year_month` formatında (YYYY-MM) bir anahtar oluşturulur.
   - `self.data` sözlüğünde, ilgili cari hesap koduna ve `year_month` anahtarına göre borç ve alacak bilgileri güncellenir. Alacaklar negatif olarak eklenir.
   - Her ödeme için `self.single_transaction_months` ve `self.document_transactions` sözlükleri güncellenir.

#### 3. Ödeme Listesi Oluşturma:
   - `generate_payment_list` fonksiyonu, ödeme listesini oluşturur.
   - Şu anki tarih alınır ve son dört ay hesaplanır.
   - `last_4_months_keys`, son dört ayı en eski aydan başlayarak sıralar.
   - Her bir cari hesap kodu için:
     - Tüm aylar sıralanır (`all_months_sorted`).
     - Tüm borçların toplamı (`total_debt`) hesaplanır.
     - Tüm alacakların toplamı (`total_credit`) hesaplanır.
     - `current_balance`, tüm borçlar ve alacakların toplamı olarak hesaplanır.
     - `monthly_balances` adlı bir sözlük başlatılır ve son dört ay için sıfır değerlerle doldurulur.
     - `carry_over` değişkeni sıfır olarak başlatılır.
     - Her bir ay için:
       - Ayın alacak toplamı (`month_credit`) alınır.
       - İlk ay için:
         - `first_month_balance`, `total_debt` ve `month_credit` toplamı olarak hesaplanır.
         - Eğer `first_month_balance` pozitifse, `carry_over` bu değere ayarlanır. Aksi halde `carry_over` sıfır olarak ayarlanır.
       - Diğer aylar için:
         - `carry_over`, `month_credit` eklenerek güncellenir.
         - Eğer `carry_over` pozitifse, ilgili ay için `monthly_balances` sıfır olarak ayarlanır. Aksi halde `monthly_balances` `carry_over` değeri olarak ayarlanır ve `carry_over` sıfırlanır.
     - Son beş ayın `monthly_balances` toplamı (`monthly_balance_sum`) hesaplanır.
     - `oncesi_balance`, `current_balance` ve `monthly_balance_sum` farkı olarak hesaplanır.
     - Cari hesap bilgileri ve bakiyeler `payment_list` listesine eklenir.

#### 4. Anomalileri Ele Alma:
   - `handle_anomalies` fonksiyonu, anormal durumları ele alır.
   - Tek işlem yapılan aylar için:
     - Eğer sadece bir işlem varsa ve sadece bir belge numarası içeriyorsa, bu işlemin alacak miktarı `monthly_balance` olarak kaydedilir.
   - Aynı ay içinde hem borç hem de alacak işlemleri olan durumlar için:
     - Eğer aynı ay içinde hem borç hem de alacak işlemleri varsa, bu işlemler birleştirilerek `monthly_balance` olarak kaydedilir.
   - Aynı ay içinde aynı belge numarasına sahip işlemler için:
     - Eğer aynı ay içinde aynı belge numarasına sahip işlemler varsa, bu işlemler birleştirilerek `monthly_balance` olarak kaydedilir.

#### 5. Sonuçları Döndürme:
   - `payment_list` listesi, ödeme listesi olarak döndürülür ve gerekli yerlerde güncellemeler yapılır.

### Python Kod:

```python
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

    def process_transactions(self):
        for payment in SupplierPayment.objects.all():
            date = datetime.strptime(payment.belge_tarih, "%Y-%m-%d").date()
            year_month = f"{date.year}-{str(date.month).zfill(2)}"
            self.data[payment.cari_kod][year_month]['debt'] += payment.borc
            self.data[payment.cari_kod][year_month]['credit'] += payment.alacak * -1
            self.single_transaction_months[payment.cari_kod][year_month] += 1
            self.document_transactions[payment.cari_kod][year_month].append(payment.belge_no)

    def generate_payment_list(self):
        payment_list = []
        current_date = datetime.now()
        last_4_months = [current_date - timedelta(days=30 * x) for x in range(4)]
        last_4_months_keys = [date.strftime("%Y-%m") for date in last_4_months]
        last_4_months_keys.reverse()  # Sort from oldest to newest month

        for cari_kod, months in self.data.items():
            # Add default zero balances for each month in the year
            for month in range(1, 13):
                year_month = f"2024-{str(month).zfill(2)}"
                if year_month not in months:
                    months[year_month] = {'debt': Decimal('0.00'), 'credit': Decimal('0.00')}
                    
            all_months_sorted = sorted(months.keys())
            total_debt = sum(months[month]['debt'] for month in months)
            total_credit = sum(months[month]['credit'] for month in months)
            current_balance = Decimal(total_debt + total_credit)

            monthly_balances = {month: Decimal('0.00') for month in last_4_months_keys}
            carry_over = Decimal('0.00')

            for i, month in enumerate(all_months_sorted):
                month_credit = months[month]['credit']

                if i == 0:  # First month calculation
                    first_month_balance = total_debt + month_credit
                    if first_month_balance > 0:
                        carry_over = first_month_balance
                    else:
                        carry_over = Decimal('0.00')
                else:
                    carry_over += month_credit

                if month in last_4_months_keys:
                    if carry_over > 0:
                        monthly_balances[month] = Decimal('0.00')
                    else:
                        monthly_balances[month] = carry_over
                        carry_over = Decimal('0.00')

            supplier_payment = SupplierPayment.objects.filter(cari_kod=cari_kod).first()
            cari_ad = supplier_payment.cari_ad if supplier_payment else 'Unknown'

            monthly_balance_sum = sum(monthly_balances.values())
            oncesi_balance = current_balance - monthly_balance_sum

            payment_list.append({
                'cari_kod': cari_kod,
                'cari_ad': cari_ad,
                'current_balance': current_balance,
                'monthly_balances': {'oncesi': float(oncesi_balance), **{k: float(v) for

 k, v in monthly_balances.items()}}
            })

        self.handle_anomalies()  # Handle anomalies after generating the initial payment list
        return payment_list

    def handle_anomalies(self):
        # Handle single transactions
        for cari_kod, months in self.single_transaction_months.items():
            for month, count in months.items():
                if count == 1:  # Only one transaction in this month
                    document_numbers = self.document_transactions[cari_kod][month]
                    if len(document_numbers) == 1:  # Only one document number in this month
                        doc_number = document_numbers[0]
                        doc_transaction = SupplierPayment.objects.filter(cari_kod=cari_kod, belge_no=doc_number).first()
                        if doc_transaction:
                            total_credit = doc_transaction.alacak
                            if total_credit != 0:  # Only handle credit transactions
                                self.data[cari_kod][month]['monthly_balance'] = total_credit

        # Handle same month transactions with both debt and credit
        for cari_kod, months in self.data.items():
            for month, values in months.items():
                if values['debt'] != 0 and values['credit'] != 0:
                    combined_balance = values['debt'] + values['credit']
                    self.data[cari_kod][month]['monthly_balance'] = combined_balance
                    self.data[cari_kod][month]['debt'] = Decimal('0.00')
                    self.data[cari_kod][month]['credit'] = Decimal('0.00')

        # Handle transactions with the same document number within the same month
        for cari_kod, months in self.document_transactions.items():
            for month, documents in months.items():
                if len(documents) == 1:  # Only one document number in this month
                    doc_number = documents[0]
                    doc_transactions = SupplierPayment.objects.filter(cari_kod=cari_kod, belge_no=doc_number)
                    total_debt = sum(transaction.borc for transaction in doc_transactions)
                    total_credit = sum(transaction.alacak for transaction in doc_transactions) * -1
                    combined_balance = total_debt + total_credit
                    if combined_balance != 0:
                        self.data[cari_kod][month]['monthly_balance'] = combined_balance

class SupplierPaymentSimulationView(APIView):
    def get(self, request, *args, **kwargs):
        simulation = SupplierPaymentSimulation()
        simulation.process_transactions()
        payment_list = simulation.generate_payment_list()

        if payment_list:
            with db_transaction.atomic():
                updated_payment_list = []
                for item in payment_list:
                    closing_invoice, created = ClosingInvoice.objects.update_or_create(
                        cari_kod=item['cari_kod'],
                        defaults={
                            'current_balance': item['current_balance'],
                            'monthly_balances': item['monthly_balances'],
                        }
                    )
                    updated_payment_list.append({
                        'cari_kod': closing_invoice.cari_kod,
                        'cari_ad': closing_invoice.cari_ad,
                        'current_balance': closing_invoice.current_balance,
                        'monthly_balances': closing_invoice.monthly_balances,
                        'iban': closing_invoice.iban,
                        'odemekosulu': closing_invoice.odemekosulu,
                    })
            return JsonResponse(updated_payment_list, safe=False)
        else:
            return Response({'message': 'Veri bulunamadı.'}, status=status.HTTP_404_NOT_FOUND)
```

Bu algoritma, belirli bir dönemsellik ilkesi ile her cari hesap için sanal bir başlangıç oluşturur ve tüm cari hareketleri bu doğrultuda değerlendirir. Anomalik durumlar da bu algoritma ile ele alınır.























************************
İşte bu algoritmanın text olarak yazılmış hali:

### SupplierPaymentSimulation Sınıfı Algoritması:

#### 1. Başlatma:
   - `self.data` adlı bir defaultdict yapısı başlatılır. Bu yapı, cari hesap kodlarına göre borç ve alacak bilgilerini saklar.

#### 2. İşlemleri İşleme:
   - `process_transactions` fonksiyonu, tüm `SupplierPayment` nesnelerini döngüye alır.
   - Her ödeme için, belge tarihi alınır ve `year_month` formatında (YYYY-MM) bir anahtar oluşturulur.
   - `self.data` sözlüğünde, ilgili cari hesap koduna ve `year_month` anahtarına göre borç ve alacak bilgileri güncellenir. Alacaklar negatif olarak eklenir.

#### 3. Ödeme Listesi Oluşturma:
   - `generate_payment_list` fonksiyonu, ödeme listesini oluşturur.
   - Şu anki tarih alınır ve son dort ay hesaplanır.
   - `last_5_months_keys`, son dort ayı en eski aydan başlayarak sıralar.
   - Her bir cari hesap kodu için:
     - Tüm aylar sıralanır (`all_months_sorted`).
     - Tüm borçların toplamı (`total_debt`) hesaplanır.
     - `monthly_balances` adlı bir sözlük başlatılır ve son dort ay için sıfır değerlerle doldurulur.
     - `carry_over` değişkeni sıfır olarak başlatılır.
     - Her bir ay için:
       - Ayın alacak toplamı (`month_credit`) alınır.
       - İlk ay için:
         - `first_month_balance`, `total_debt` ve `month_credit` toplamı olarak hesaplanır.
         - Eğer `first_month_balance` pozitifse, `carry_over` bu değere ayarlanır. Aksi halde `carry_over` sıfır olarak ayarlanır.
       - Diğer aylar için:
         - `carry_over`, `month_credit` eklenerek güncellenir.
         - Eğer `carry_over` pozitifse, ilgili ay için `monthly_balances` sıfır olarak ayarlanır. Aksi halde `monthly_balances` `carry_over` değeri olarak ayarlanır ve `carry_over` sıfırlanır.
     - `current_balance`, tüm borçlar ve alacakların toplamı olarak hesaplanır.
     - Son beş ayın `monthly_balances` toplamı (`monthly_balance_sum`) hesaplanır.
     - `oncesi_balance`, `current_balance` ve `monthly_balance_sum` farkı olarak hesaplanır.
     - Cari hesap bilgileri ve bakiyeler `payment_list` listesine eklenir.

#### 4. Sonuçları Döndürme:
   - `payment_list` listesi, ödeme listesi olarak döndürülür ve gerekli yerlerde güncellemeler yapılır.


### Örnek Kullanım:
```python
class SupplierPaymentSimulation:
    def __init__(self):
        self.data = defaultdict(lambda: defaultdict(lambda: {'debt': Decimal('0.00'), 'credit': Decimal('0.00')}))

    def process_transactions(self):
        for payment in SupplierPayment.objects.all():
            date = datetime.strptime(payment.belge_tarih, "%Y-%m-%d").date()
            year_month = f"{date.year}-{str(date.month).zfill(2)}"
            self.data[payment.cari_kod][year_month]['debt'] += payment.borc
            self.data[payment.cari_kod][year_month]['credit'] += payment.alacak * -1

    def generate_payment_list(self):
        payment_list = []
        current_date = datetime.now()
        last_5_months = [current_date - timedelta(days=30 * x) for x in range(5)]
        last_5_months_keys = [date.strftime("%Y-%m") for date in last_5_months]
        last_5_months_keys.reverse()  # En eski aydan başlamak üzere sırala

        for cari_kod, months in self.data.items():
            all_months_sorted = sorted(months.keys())
            total_debt = sum(months[month]['debt'] for month in months)

            monthly_balances = {month: Decimal('0.00') for month in last_5_months_keys}
            carry_over = Decimal('0.00')

            for i, month in enumerate(all_months_sorted):
                month_credit = months[month]['credit']
                
                if i == 0:  # İlk ay için hesaplama
                    first_month_balance = total_debt + month_credit
                    if first_month_balance > 0:
                        carry_over = first_month_balance
                    else:
                        carry_over = Decimal('0.00')
                else:
                    carry_over += month_credit

                if i > 0:
                    if month in last_5_months_keys:
                        if carry_over > 0:
                            monthly_balances[month] = Decimal('0.00')
                        else:
                            monthly_balances[month] = carry_over
                            carry_over = Decimal('0.00')

            supplier_payment = SupplierPayment.objects.filter(cari_kod=cari_kod).first()
            cari_ad = supplier_payment.cari_ad if supplier_payment else 'Unknown'

            current_balance = float(total_debt + sum(months[month]['credit'] for month in months))
            monthly_balance_sum = sum(monthly_balances.values())
            oncesi_balance = current_balance - float(monthly_balance_sum)

            payment_list.append({
                'cari_kod': cari_kod,
                'cari_ad': cari_ad,
                'current_balance': current_balance,
                'monthly_balances': {'oncesi': oncesi_balance, **{k: float(v) for k, v in monthly_balances.items()}}
            })

        return payment_list
```

Bu algoritma, cari hesap hareketlerini doğru bir şekilde işleyerek `monthly_balances` ve `oncesi` değerlerini hesaplar.






















****************************
Anladım, algoritmayı gözden geçirelim ve sonraki aylar için bakiyeleri hesaplarken önceki aydan devreden pozitif değeri ve o ayın kredi değerini dikkate alarak güncelleyelim. İşte adım adım güncellenmiş algoritma:

1. İlk ayın bakiyesini hesaplayın: tüm borçların toplamından ilk ayın alacağını çıkarın.
2. İlk ayın bakiyesi pozitifse, sonraki aya devir edin.
3. Her bir sonraki ay için:
   - Ayın bakiyesini hesaplamak üzere önceki aydan devreden bakiyeyi kullanın.
   - Ay içindeki borçlar 0 olarak kabul edilir, çünkü ilk ayda tüm borçlar kullanıldı.
   - Ayın bakiyesi = Önceki aydan devreden bakiye - o ayın alacakları.
   - Eğer bu bakiye pozitifse, bakiyeyi sonraki aya devredin ve o ay için bakiyeyi sıfıra ayarlayın.
   - Eğer bakiye negatifse, bakiyeyi o ay için kaydedin.

İşte bu mantığı uygulayan güncellenmiş kod:

1. İlk Ay Hesaplaması:
   a. Tüm borçları topla.
   b. İlk ayın alacaklarını topla.
   c. İlk ayın bakiyesini hesapla = Toplam Borçlar - İlk Ay Alacakları.
   d. Eğer ilk ay bakiyesi pozitifse:
      - carry-over = İlk Ay Bakiyesi
      - İlk Ay Bakiyesi = 0
   e. Eğer ilk ay bakiyesi negatif veya sıfır ise:
      - İlk Ay Bakiyesi = İlk Ay Bakiyesi
      - carry-over = 0

2. Sonraki Aylar Hesaplaması:
   a. Her ay için:
      i. Ayın alacaklarını topla.
      ii. Eğer carry-over pozitifse:
         - carry-over = carry-over + Ayın Alacakları
         - Eğer carry-over pozitifse:
            - Ayın Bakiyesi = 0
         - Eğer carry-over negatifse:
            - Ayın Bakiyesi = carry-over
            - carry-over = 0
      iii. Eğer carry-over negatif veya sıfır ise:
         - Ayın Bakiyesi = carry-over
         - carry-over = 0

3. Sonuçları Topla ve Döndür:
   a. Her ay için hesaplanan bakiyeleri bir dictionary içine yerleştir.
   b. Sonuçları JSON formatında döndür.


```python
class SupplierPaymentSimulation:
    def __init__(self):
        self.data = defaultdict(lambda: defaultdict(lambda: {'debt': Decimal(0), 'credit': Decimal(0)}))

    def process_transactions(self):
        for payment in SupplierPayment.objects.all():
            month = payment.belge_tarih.split('.')[1] if payment.belge_tarih else '00'
            self.data[payment.cari_kod][month]['debt'] += Decimal(payment.borc)
            self.data[payment.cari_kod][month]['credit'] += Decimal(payment.alacak)

    def generate_payment_list(self):
        payment_list = []
        current_month = datetime.datetime.now().strftime('%m')

        for cari_kod, months in self.data.items():
            total_debt = sum(data['debt'] for data in months.values())
            first_month_credit = months['01']['credit'] if '01' in months else Decimal(0)

            first_month_balance = total_debt - first_month_credit
            carry_over = Decimal(0) if first_month_balance <= 0 else first_month_balance

            monthly_balances = {'01': float(first_month_balance if first_month_balance <= 0 else 0)}

            for i in range(1, 12):  # Sonraki aylar için
                month = str(i+1).zfill(2)
                if month in months:
                    month_credit = months[month]['credit']
                    month_balance = carry_over - month_credit
                    carry_over = Decimal(0) if month_balance <= 0 else month_balance
                    monthly_balances[month] = float(month_balance if month_balance <= 0 else 0)

            overall_balance = sum(monthly_balances.values())
            payment_list.append({
                'cari_kod': cari_kod,
                'cari_ad': 'Örnek Cari Ad',
                'current_balance': float(overall_balance),
                'monthly_balances': monthly_balances
            })

        return payment_list
```

Bu kod bloğu, ilk ay için borçları toplar, ilk ayın alacağını çıkarır ve sonraki aylar için alacakları kullanarak bakiyeleri hesaplar. Eğer bir ayın bakiyesi pozitifse, bu değeri sonraki aya devreder ve o ayın bakiyesini sıfıra ayarlar. Eğer bakiye negatifse, bu değeri o ayın bakiyesi olarak kaydeder. Bu şekilde, her ayın bakiyesi doğru bir şekilde hesaplanır.

### 1. Bakiye Nasıl Hesaplanmalı
- Her `cari_kod` için, tüm ayların borç ve alacak miktarlarını toplayarak genel bakiye hesaplanır.
- Bakiye hesaplama: `Genel Bakiye = Toplam Alacak - Toplam Borç`

### 2. İlk Ay Hesabı Nasıl Yapılmalı
- İlk ay (genellikle Ocak) için, `cari_kod` bazında tüm ayların borç toplamı hesaplanır.
- Yalnızca ilk ay için `cari_kod`un alacak toplamı hesaplanır.
- İlk ay bakiyesi: `İlk Ay Bakiye = Tüm Ayların Borç Toplamı - İlk Ayın Alacak Toplamı`
- Eğer ilk ay bakiyesi pozitifse, bu değer sonraki aya devredilir ve ilk ay için bakiye sıfır olarak kaydedilir.
- Eğer ilk ay bakiyesi negatifse veya sıfır ise, bu değer ilk ayın bakiyesi olarak kaydedilir.

### 3. Sonraki Aylar Nasıl Hesaplanmalı
- Önceki aydan devreden bakiye (varsa) ile başlanır.
- Her ay için, `cari_kod` bazında o ayın borç ve alacak toplamı hesaplanır.
- Ayın bakiyesi: `Ayın Bakiyesi = Önceki Aydan Devreden Bakiye + O Ayın Borç Toplamı - O Ayın Alacak Toplamı`
- Eğer ayın bakiyesi pozitifse, bu değer sonraki aya devredilir ve o ay için bakiye sıfır olarak kaydedilir.
- Eğer ayın bakiyesi negatif veya sıfır ise, bu değer o ayın bakiyesi olarak kaydedilir.


Bu algoritma, belirli bir tarih aralığındaki (örneğin, son beş ay) tedarikçi bakiyesi ve alacakların hangi aylardan geldiğini anlamaya yardımcı olur. Her ay için bakiye hesaplamaları yaparak, tedarikçinin finansal durumunun zaman içindeki değişimini izlememizi sağlar.