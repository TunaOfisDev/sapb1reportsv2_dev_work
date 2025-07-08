# backend/systemnotebook/models/system_note_model.py

from django.db import models
from systemnotebook.models.base import BaseModel


class SystemNote(BaseModel):
    """
    Sistem notlarını temsil eder.
    Kaynak: GitHub commit mesajı veya SystemAdmin el notu.
    """
    SOURCE_GITHUB = "github"
    SOURCE_ADMIN  = "admin"

    SOURCE_CHOICES = [
        (SOURCE_GITHUB, "GitHub"),
        (SOURCE_ADMIN,  "SystemAdmin"),
    ]

    title       = models.CharField(max_length=255)
    content     = models.TextField(blank=True)
    source      = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default=SOURCE_ADMIN,
    )

    # 🔹 Git commit’lerini benzersiz kıl
    commit_sha  = models.CharField(
        "Git commit SHA",
        max_length=40,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Sistem Notu"
        verbose_name_plural = "Sistem Notları"
        # Eğer hâlâ gerekli görüyorsan, ek kısıtları buraya ekle
        constraints = [
            # Tekil SHA zaten unique=True ile sağlandı, ekstra constraint istemez
        ]

    def __str__(self) -> str:                       # type: ignore[override]
        src = self.get_source_display()
        ts  = self.created_at.strftime("%Y-%m-%d")
        return f"[{src}] {self.title} - {ts}"
