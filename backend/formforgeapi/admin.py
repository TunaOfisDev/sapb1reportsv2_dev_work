# path: backend/formforgeapi/admin.py

from django.contrib import admin
from .models import Department, Form, FormField, FormSubmission, SubmissionValue
from django.utils.translation import gettext_lazy as _

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    list_filter = ('name',)
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'created_by', 'created_at', 'updated_at')
    list_filter = ('department', 'created_by')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(FormField)
class FormFieldAdmin(admin.ModelAdmin):
    list_display = ('form', 'label', 'field_type', 'is_required', 'is_master', 'order', 'created_at', 'updated_at')
    list_filter = ('form', 'field_type', 'is_required', 'is_master')
    search_fields = ('label',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(FormSubmission)
class FormSubmissionAdmin(admin.ModelAdmin):
    list_display = ('form', 'created_by', 'created_at', 'updated_at')
    list_filter = ('form', 'created_by')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(SubmissionValue)
class SubmissionValueAdmin(admin.ModelAdmin):
    list_display = ('submission', 'form_field', 'value', 'created_at', 'updated_at')
    list_filter = ('submission', 'form_field')
    search_fields = ('value',)
    readonly_fields = ('created_at', 'updated_at')


