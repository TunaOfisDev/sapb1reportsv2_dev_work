# backend/systemnotebook/services/github_commit_importer.py

import requests
from django.conf import settings
from systemnotebook.models.system_note_model import SystemNote

GITHUB_API_URL = "https://api.github.com"
REPO_OWNER = "TunaOfisDev"
REPO_NAME = "sapb1reportsv2workLive"
PER_PAGE = 100  # GitHub API max 100 commit verir


def fetch_commits_from_github():
    url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/commits"
    headers = {
        "Authorization": f"token {settings.GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }

    page = 1
    while True:
        response = requests.get(url, headers=headers, params={"per_page": PER_PAGE, "page": page})
        if response.status_code != 200:
            raise Exception(f"GitHub API hatası: {response.status_code} - {response.text}")

        commits = response.json()
        if not commits:
            break

        for commit in commits:
            sha = commit.get('sha')
            commit_data = commit.get('commit', {})
            author_name = commit_data.get('author', {}).get('name', 'Unknown')
            full_message = commit_data.get('message', '').strip()
            commit_date = commit_data.get('author', {}).get('date')  # <-- Burada oluşma zamanı

            lines = full_message.split("\n", 1)
            summary = lines[0]
            description = lines[1].strip() if len(lines) > 1 else ''

            if SystemNote.objects.filter(commit_sha=sha).exists():
                continue


            title = f"Commit by {author_name} - {summary}"
            content = description

            SystemNote.objects.create(
                title=title,
                content=content,
                source='github',
                created_by=None,
                created_at=commit_date,
                commit_sha=sha  # 🔧 BU SATIR EKLENMELİ
            )

        page += 1

