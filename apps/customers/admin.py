from django.contrib import admin
from .models import Customer

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name','cellphone', 'is_active')
    list_filter = ('is_active', 'gender', 'document_type')
    search_fields = ('first_name', 'last_name', 'cellphone')

admin.site.register(Customer, CustomerAdmin)
