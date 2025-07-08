

# 📘 Report Orchestrator Whitepaper

## 1. 🎯 Amaç ve Genel Tanım

Report Orchestrator, SAP Business One HANA veritabanından alınan verilerle gelişmiş raporların oluşturulması, işlenmesi ve ilgili kullanıcılara e-posta ile gönderilmesini yöneten bir Django tabanlı modüldür. Bu yapı, zamana bağlı görevler ile otomatik çalışır ve rule-engine tabanlı filtreleme, özetleme gibi dinamik işlemler gerçekleştirir.

---

## 2. 🧱 Modüler Yapı ve Katmanlar

Bu modül yüksek derecede modüler bir yapıya sahiptir:

- `models/`: Rapor tanımı (`APIReportModel`) ve çalıştırma geçmişi (`APIExecutionLog`) modellerini barındırır.
- `tasks/`: Zamanlanabilir görevler (`run_report`, `run_all_reports`) burada tanımlıdır.
- `services/`: Raporu işleyen, sonucu kaydeden ve hata yakalayan mantıksal servis katmanıdır.
- `rules/`: `rule_engine` ve `validators` ile veri doğruluğunu kontrol eder ve kural bazlı filtreleme yapar.
- `fetchers/`: Aktif ve pasif modlara göre veri çekimini soyutlayan katmandır.
- `exporters/`: Excel ve PDF çıktılarının üretiminden sorumludur.
- `utils/`: Yardımcı zaman ve JSON araçları.

---

## 3. 📈 Rapor Üretim Akışı

Rapor çalıştırma süreci şu adımlarla ilerler:

1. `APIReportModel` nesnesi `api_name` ile alınır.
2. Aktif modda varsa `trigger_url` tetiklenir ve yanıt beklenir.
3. `data_pull_url` ile JSON veri çekilir.
4. Aktif modda veri doğrudan saklanır, pasif modda `rule_engine` ile işlenir.
5. Sonuç `result_json` alanına kaydedilir.
6. `APIExecutionLog` kayıt altına alınır.
7. Uygun ise otomatik e-posta servisi tetiklenir.

---

## 4. ⏱ Celery Görev Planlama

Görevler `run_report.py` içinde aşağıdaki gibi tanımlıdır:

```python
@shared_task(name="report_orchestrator.tasks.run_report")
def run_report(api_name: str):
    ...
```

Modülün kendi `celery_settings.py` dosyası vardır:

```python
# config/celery_settings.py
CELERY_BEAT_SCHEDULE = {
    "daily_top20_customer_balance_mail": {
        "task": "report_orchestrator.tasks.run_report",
        "schedule": crontab(minute=56, hour=11, day_of_week='1-5'),
        "args": ("custumer_balance_top20",)
    }
}
```

Kök `settings.py` dosyasında:
```python
from report_orchestrator.config.celery_settings import CELERY_BEAT_SCHEDULE as REPORT_ORCHESTRATOR_SCHEDULE

CELERY_BEAT_SCHEDULE = {
    **REPORT_ORCHESTRATOR_SCHEDULE,
}
```

---

## 5. 📬 Mailservice ile Entegre Çalışma

Report Orchestrator, `mailservice` modülü ile doğrudan entegredir. Rapor tamamlandıktan sonra:

- `load_mail_service_for_report(api_name)` fonksiyonu ile uygun sınıf yüklenir.
- Bu sınıf `send_mail(context)` metodunu uygular.
- Örnek: `mailservice.services.send_custumer_balance_top20_email_task` e-posta şablonunu ve verisini işler.

Bu yapı sayesinde yeni bir rapor eklendiğinde, sadece yeni bir MailServiceClass tanımlanması yeterlidir.

---

## 6. 🚀 Genişletilebilirlik & En İyi Uygulamalar

- Her yeni rapor için `APIReportModel`, `Celery Beat`, `MailServiceClass` ve (varsa) yeni bir `rule_engine` şablonu oluşturulmalıdır.
- İleride kullanıcıya özel filtreleme UI’si ile parametreli raporlar desteklenebilir.
- Task retry/backoff mekanizmaları ile hata toleransı artırılabilir.
- Worker ve Beat süreçleri mutlaka ayrı process olarak yönetilmelidir.

---

Bu yapı ile Report Orchestrator modülü yüksek performanslı, özelleştirilebilir ve diğer modüllerle uyumlu bir şekilde büyüyebilir.