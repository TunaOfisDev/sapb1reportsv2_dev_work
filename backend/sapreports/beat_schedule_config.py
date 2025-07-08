# backend/sapreports/beat_schedule_config.py

from celery.schedules import crontab

BEAT_SCHEDULE = {
    'run-every-10-minutes': {
        'task': 'sapreports.tasks.periodic.periodic_task',
        'schedule': 600.0,
    },
    'scan-and-save-files-every-night': {
        'task': 'filesharehub.tasks.scan_and_save_files',
        'schedule': crontab(minute=0, hour=0),
    },
    'fix-thumbnails-daily': {
        'task': 'filesharehub_v2.tasks.fix_thumbnails_task.run_fix_thumbnails',
        'schedule': crontab(hour=4, minute=0),
    },
    'clean-logs-every-2h': {                       # 👈 isim de güncellendi
        'task': 'sapreports.tasks.log_cleanup.clean_log_files',
        'schedule': crontab(minute=0, hour='*/2'), # ⏲️ her 2 saatte bir
    },
}
