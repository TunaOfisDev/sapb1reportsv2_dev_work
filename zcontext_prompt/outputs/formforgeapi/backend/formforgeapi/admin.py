# path: backend/formforgeapi/admin.py
from django.contrib import admin
from .models import Department, Form, FormField, FormSubmission, SubmissionValue

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'department', 'created_by', 'created_at')
    list_filter = ('department', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(FormField)
class FormFieldAdmin(admin.ModelAdmin):
    list_display = ('id', 'form', 'label', 'field_type', 'is_required', 'is_master', 'order')
    list_filter = ('form', 'field_type', 'is_required', 'is_master')
    search_fields = ('label',)

@admin.register(FormSubmission)
class FormSubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'form', 'created_by', 'created_at')
    list_filter = ('form', 'created_at')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(SubmissionValue)
class SubmissionValueAdmin(admin.ModelAdmin):
    list_display = ('id', 'submission', 'form_field', 'value')
    list_filter = ('submission', 'form_field')
    search_fields = ('value',)


