from django.contrib import admin
from .models import Agreement

class AgreementAdmin(admin.ModelAdmin):
    list_display = ('name', 'quota', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'quota')
    date_hierarchy = 'created_at'
    filter_horizontal = ('company',)

admin.site.register(Agreement, AgreementAdmin)

