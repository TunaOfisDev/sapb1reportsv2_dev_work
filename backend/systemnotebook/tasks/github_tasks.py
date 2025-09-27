# backend/systemnotebook/tasks/github_tasks.py

from celery import shared_task
from systemnotebook.services.github_commit_importer import fetch_commits_from_github

@shared_task
def import_github_commits_task():
    """
    GitHub commitlerini çekip SystemNote olarak kaydeder.
    Celery Beat ile günlük/haftalık çalıştırılabilir.
    """
    fetch_commits_from_github()
