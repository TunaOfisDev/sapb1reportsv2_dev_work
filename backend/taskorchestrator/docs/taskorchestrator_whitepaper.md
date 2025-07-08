# 🧠 Task Orchestrator Whitepaper
**Sürüm:** v1.0  
**Yazan:** TARZ  
**Tarih:** $(date '+%Y-%m-%d %H:%M')  
**Konum:** /backend/taskorchestrator/

---

## 🎯 Amaç

Bu modül, SAPB1ReportsV2 altyapısında zamanlanmış ve manuel tetiklenebilir görevlerin **merkezi olarak tanımlanması**, **admin panelden kontrol edilmesi** ve **Celery-CeleryBeat altyapısına düzgün şekilde entegre edilmesi** için tasarlanmıştır.

---

## 🧩 Temel Bileşenler

### 1. `TaskDefinition`
- Görev tipini temsil eder.
- Fonksiyon adı (`import path`), kısa açıklama ve sınıflandırma içerir.
- Yeni görev yazıldığında sadece bu modele kayıt yapılır.

### 2. `ScheduledTask`
- Belirli bir görev tipini belirli bir zaman planı (crontab) ve parametrelerle ilişkilendirir.
- Aktif/Pasif durumu kontrol edilebilir.

### 3. `beat_sync.py`
- `ScheduledTask` modellerinden `django-celery-beat`'in `PeriodicTask`'larını oluşturur/günceller.
- Böylece admin panelde yapılan değişiklikler `Celery Beat` tarafından otomatik tanınır.

### 4. `dispatcher.py`
- Queue’ya düşen `ScheduledTask` ID’sini alır ve ilgili fonksiyonu çağırır.
- Dinamik ve merkezi görev çağrısı içerir.

### 5. `tasks.py`
- Celery’ye tanıtılan @shared_task işleyicisi içerir.
- `dispatcher.run_task(id)` şeklinde görev tetikler.

---

## 🛡 Tasarım Prensipleri

- **Kodu değil veri modelini yönetiyoruz.** (Görev zamanlamaları DB tabanlı)
- **Kod parçası değil görev tanımı planlıyoruz.**
- **API üzerinden görev oluşturulabilir, ama asıl kontrol admin panelde.**
- **Her görev bir `TaskDefinition`, her çalışma bir `ScheduledTask`.**

---

## ⚙️ Teknik Detaylar

- Tüm görev fonksiyonları `import_string()` ile çağrılır.
- `ScheduledTask.enabled = False` olan kayıtlar hiçbir zaman tetiklenmez.
- `beat_sync()` fonksiyonu `settings.STARTUP_TASK_SYNC = True` ise uygulama başında çalıştırılabilir.
- Görev parametreleri `JSONField` olarak saklanır, işlevlere `**kwargs` ile geçirilir.

---

## 🧠 Neden Bu Yapı?

Geleneksel `@shared_task` + `celerybeat` yapısı zamanla karmaşıklaşır:
- Kodun içine dağılır.
- Takip zorlaşır.
- Yeni görev eklemek için deploy gerekir.

Bu modül ile:
- Görevler tanımlıdır.
- Parametreler veri tabanındadır.
- Zamanlama `django-celery-beat` tablosuyla senkronize edilir.
- Yönetim tamamen admin panelden yapılır.

---

## 🔮 Gelecek Geliştirmeler

- Görev geçmişi loglama
- Hata durumunda otomatik uyarı gönderimi (Slack, mail)
- Retry & priority yapılarının admin panelden düzenlenebilmesi
- Görev tetikleme UI arayüzü (dashboard)

---

## 👋 Not

> Bu yapı kurumsal operasyonel sürdürülebilirlik için tasarlanmıştır.  
> Yeni görev yazmadan önce mutlaka `TaskDefinition` üzerinden planlama yapılmalıdır.  
> **Hiçbir görev hardcoded `beat` yapılandırması ile çalıştırılmamalıdır.**  
> TARZ imzalı sistemde kuralsızlık olmaz.

---

