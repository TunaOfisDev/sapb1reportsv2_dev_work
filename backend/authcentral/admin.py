# backend/authcentral/admin.py
from django.contrib import admin
from .models import CustomUser, Department, Position
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django.contrib.auth.models import Group
from django.contrib.auth.hashers import make_password, identify_hasher

class CustomUserResource(resources.ModelResource):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'password', 'is_active', 'is_staff', 'is_superuser', 'departments', 'positions')
        export_order = ('id', 'email', 'password', 'is_active', 'is_staff', 'is_superuser', 'departments', 'positions')

    def before_import_row(self, row, **kwargs):
        password = row.get('password')
        # Şifre hashlenmemişse, hashleyin
        if password and not password.startswith('pbkdf2_sha256$'):
            row['password'] = make_password(password)

    def get_instance(self, instance_loader, row):
        # Email adresine göre mevcut kullanıcıyı bul ve güncelle
        return self._meta.model.objects.filter(email=row['email']).first()

    def before_save_instance(self, instance, using_transactions, dry_run):
        password = instance.password
        try:
            # Şifrenin hashlenmiş olup olmadığını kontrol edin
            identify_hasher(password)
        except ValueError:
            # Hashlenmemiş şifreyi hashleyin
            instance.set_password(password)

    def after_save_instance(self, instance, using_transactions, dry_run):
        # Kayıttan sonra kullanıcıyı kaydet
        instance.save()

class CustomUserAdmin(ImportExportModelAdmin, BaseUserAdmin):
    resource_class = CustomUserResource
    list_display = ('id','email', 'is_active', 'is_staff', 'departments_list', 'positions_list')
    list_filter = ('is_active', 'is_staff', 'departments', 'positions')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
        ('Additional Info', {'fields': ('departments', 'positions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('departments', 'positions', 'groups', 'user_permissions',)

    def departments_list(self, obj):
        return ", ".join([d.name for d in obj.departments.all()])
    departments_list.short_description = 'Departments'

    def positions_list(self, obj):
        return ", ".join([p.name for p in obj.positions.all()])
    positions_list.short_description = 'Positions'


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id','name',)
    search_fields = ('name',)


class PositionAdmin(admin.ModelAdmin):
    list_display = ['id','name', 'department']
    list_filter = ['department']
    search_fields = ['name']


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.unregister(Group)
