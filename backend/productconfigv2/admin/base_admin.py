# productconfigv2/admin/base_admin.py

from import_export.admin import ImportExportModelAdmin
from django.utils.translation import gettext_lazy as _


class BaseAdmin(ImportExportModelAdmin):
    """
    Tüm admin sınıflarının kalıtım alabileceği sade ve temiz admin base sınıfı.
    """
    list_filter = ("is_active",)
    search_fields = ("id",)
    list_display = ("id", "is_active")
    save_on_top = True
    actions = ["make_active", "make_inactive"]

    # created_by / updated_by alanlarını formdan çıkar
    exclude = ("created_by", "updated_by")

    def make_active(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} kayıt aktif hale getirildi.")
    make_active.short_description = _("Seçili kayıtları aktif yap")

    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} kayıt pasif hale getirildi.")
    make_inactive.short_description = _("Seçili kayıtları pasif yap")
