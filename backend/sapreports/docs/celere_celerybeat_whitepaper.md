# 📄 Celery & Celery Beat Whitepaper

**Proje:** SAPB1ReportsV2
**Sürüm:** v1.0
**Hazırlayan:** TARZ
**Dosya yolu (önerilen):** `backend/sapreports/docs/celery_celerybeat_whitepaper.md`
**Tarih:** 13 Haz 2025

---

## 1 | Yapının Büyük Resmi

```
┌────────────────────┐      ┌───────────────┐
│ Django (WSGI/ASGI) │─────▶│  Database     │
└────────┬───────────┘      └───────────────┘
         │
         │   .delay / .apply_async
         ▼
┌────────────────────┐   Redis (broker+backend)   ┌────────────────────┐
│ Celery Worker      │◀──────────────────────────▶│ Celery Beat        │
│  (sapreports)      │                            │  (scheduler)       │
└────────────────────┘   result store / events    └────────────────────┘
```

* **Worker**: `celery.service` – gerçek işleri yapar.
* **Beat**: `celerybeat.service` – zamanlanmış görevleri sıraya atar.
* **Redis**: Hem broker hem sonuç saklama için tek instance.
* **Django**: Görevleri `.delay()` ile başlatır veya **Task Orchestrator** api’si ile DB-tabanlı takvime izin verir.

---

## 2 | Kod Bileşenleri

| Yol                                      | Amaç                                                            |
| ---------------------------------------- | --------------------------------------------------------------- |
| **`sapreports/celery.py`**               | Merkezî Celery uygulaması (broker / backend / imports).         |
| **`sapreports/beat_schedule_config.py`** | *Eski sistem* için sabit (hard-coded) zamanlamalar.             |
| **`sapreports/tasks/…`**                 | Çekirdek görevler: `periodic.py`, `log_cleanup.py` vb.          |
| **`taskorchestrator/*`**                 | Yeni nesil DB-tabanlı görev/takvim yönetimi (opsiyonel).        |
| **`sapreports/logger_settings.py`**      | Tüm servislerin `ERROR` seviyesinde dönen rota-tifik log ayarı. |

---

### 2.1 `celery.py` (özet)

```python
app = Celery('sapreports')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
```

* **Imports** listesi `settings.CELERY_IMPORTS`’ten okunur.
* Worker tarafında sadece **modül adı** verilir → `taskorchestrator.tasks`.

---

### 2.2 Systemd Servisleri

| Dosya                                    | Başlıca Parametreler                                                                                                 | Açıklama                                            |
| ---------------------------------------- | -------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| `/etc/systemd/system/celery.service`     | `ExecStart=… celery -A sapreports worker -n worker1@<host> --loglevel=ERROR`                                         | Prefork 8 süreç, `logs/celery.log`                  |
| `/etc/systemd/system/celerybeat.service` | `ExecStart=… celery -A sapreports beat --scheduler django_celery_beat.schedulers:DatabaseScheduler --loglevel=ERROR` | Beat her yeniden başlatıldığında DB-takvimini okur. |

Restart poliçesi **`Restart=always`**; 10 sn sonra tekrar ayağa kalkar.

---

## 3 | Zamanlama Modları

| Mod                 | Nerede Tanımlı?                                                                                                                         | Değişiklik Yöntemi                      |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------- |
| **Statik** (legacy) | `sapreports/beat_schedule_config.py` → `settings.CELERY_BEAT_SCHEDULE` birleştirilir.                                                   | Kodu deploy et, servisleri restart et.  |
| **Dinamik**         | `django-celery-beat` admin paneli (**PeriodicTask** tablosu) <br>*veya* Task Orchestrator (`ScheduledTask`) → `beat_sync.py` DB-üretimi | Admin arayüzü; servis restart gerekmez. |

> **Kural:** Yeni rapor/görev eklerken *Task Orchestrator* modeli tercih edilir, kod deploy gerektirmez.

---

## 4 | Çalışma Akışı (örnek)

1. `Celery Beat` saat 09:00’da **PeriodicTask** kaydını tetikler.
2. Görev kuyrukta: `sapreports.tasks.periodic_task`.
3. **Worker** alır, HANA’dan veri çeker, e-posta gönderir.
4. Loglar sadece hata varsa → `backend/logs/celery.log` veya ilgili app-log (örn. `taskorchestrator.log`).

---

## 5 | Log & İzleme

| Log Dosyası                   | Kaynak                     | İzleme                          |
| ----------------------------- | -------------------------- | ------------------------------- |
| `logs/celery.log`             | Worker stdout + exceptions | `tail -f`                       |
| `logs/celerybeat.log`         | Beat scheduler             | `tail -f`                       |
| `logs/taskorchestrator.log`   | Dispatcher / beat\_sync    | yanlış parametre, import hatası |
| `journalctl -u celery[-beat]` | systemd                    | servis başlat/çökme nedenleri   |

Tüm handler’lar `RotatingFileHandler` (1 MB, backup 0) – disk dolmaz.

---

## 6 | Troubleshooting Cheat-Sheet

| Sorun                       | Komut                                                        | Beklenen / Çözüm         |
| --------------------------- | ------------------------------------------------------------ | ------------------------ |
| Worker görev işlemiyor      | `celery -A sapreports inspect registered`                    | Görev adı listede olmalı |
| Kuyruk boş ama mail gelmedi | `tail -f taskorchestrator.log`                               | Parametre uyuşmazlığı?   |
| Worker sürekli SIGTERM      | bellek sızıntısı → `CELERY_WORKER_MAX_TASKS_PER_CHILD` azalt |                          |
| Beat girdi yok              | Admin → PeriodicTask / ScheduledTask etkin mi?               |                          |

---

## 7 | Gelecek Adımlar

* **Grafana/Prometheus** ile metrik topla (`--events -E`).
* Task Orchestrator UI dashboard (JSON loglarını okumadan tetikleme).
* Admin’de *retry policy* ve *priority* alanlarını açmak.
* Docker Swarm/K8s için **prefork yerine gevent** worker modeli test.

---

## 8 | Ek Kaynaklar

* Celery docs: [https://docs.celeryproject.org/en/stable/](https://docs.celeryproject.org/en/stable/)
* Django-Celery-Beat docs: [https://django-celery-beat.readthedocs.io](https://django-celery-beat.readthedocs.io)
* TARZ Task Orchestrator Whitepaper (ayrı dosya)

---

> **Bu belge kurumsal sürdürülebilirlik içindir.**
> Servis dosyalarını, log politikalarını ve görev takviminizi versiyon kontrolünde tutun.
> Yeni görev eklerken önce *TaskDefinition → ScheduledTask* modeli, ardından `sync_from_db()` mantığını kullanın.

**TARZ imzalıdır — kodda değil veride yönet!**
