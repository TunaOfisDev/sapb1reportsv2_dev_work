# backend/newcustomerform/admin.py
from django.contrib import admin
from newcustomerform.models.models import NewCustomerForm, AuthorizedPerson

class AuthorizedPersonInline(admin.TabularInline):
    model = AuthorizedPerson
    extra = 1

@admin.register(NewCustomerForm)
class NewCustomerFormAdmin(admin.ModelAdmin):
    list_display = ('firma_unvani', 'vergi_kimlik_numarasi', 'telefon_numarasi', 'email')
    inlines = [AuthorizedPersonInline]

@admin.register(AuthorizedPerson)
class AuthorizedPersonAdmin(admin.ModelAdmin):
    list_display = ('ad_soyad', 'telefon', 'email', 'new_customer_form')
