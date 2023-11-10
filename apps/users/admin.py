from django import forms
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.forms.widgets import TextInput
from django.utils.safestring import mark_safe

from django.urls import reverse
from .models import User, PasswordResetCode
from ..users.api.urls import *


class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'is_active', 'is_admin']
    list_filter = ['is_active', 'is_admin']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['email']

    fieldsets = (
        ('Información Personal', {'fields': ('first_name', 'last_name', 'email', 'cellphone', 'password')}),
        ('Documentación', {'fields': ('document_type', 'document')}),
        ('Permisos', {'fields': ('is_active', 'is_admin')}),
    )


class PasswordResetCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'expiration_date', 'is_active')
    list_filter = ('user', 'is_active')
    search_fields = ( 'created_at', 'expiration_date')
    date_hierarchy = 'created_at'
    readonly_fields = ('code', 'user', 'created_at', 'expiration_date', 'is_active')

admin.site.register(PasswordResetCode, PasswordResetCodeAdmin)


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        exclude = ['password']

    def clean_password(self):
        return self.instance.password


class PartiallyHiddenPasswordInput(TextInput):
    input_type = 'password'

    def render(self, name, value, attrs=None, renderer=None):
        if value:
            displayed_value = value[:6] + '*' * (len(value) - 6)
            final_attrs = self.build_attrs(attrs)
            return super().render(name, displayed_value, final_attrs, renderer)
        else:
            return super().render(name, value, attrs, renderer)


class UserAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(UserAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['password'].widget = PartiallyHiddenPasswordInput(attrs={'readonly': 'readonly'})
            change_password_url = reverse('change_password_view_name')
            message_html = f'<p>Las contraseñas no se almacenan en bruto, así que no hay manera de ver la contraseña del usuario, pero se puede cambiar la contraseña mediante <a href="{change_password_url}">este formulario</a>.</p>'
            self.fields['password'].help_text = mark_safe(message_html)


class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'is_active', 'is_admin']
    list_filter = ['is_active', 'is_admin']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['email']

    fieldsets = (
        ('Información Personal', {'fields': ('first_name', 'last_name', 'email', 'cellphone', 'password')}),
        ('Documentación', {'fields': ('document_type', 'document')}),
        ('Permisos', {'fields': ('is_active', 'is_admin')}),
    )

    form = UserAdminForm

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'password':
            kwargs['widget'] = forms.PasswordInput(render_value=True)
        return super().formfield_for_dbfield(db_field, **kwargs)

    def save_model(self, request, obj, form, change):
        if 'password' in form.changed_data:
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)


admin.site.register(User, CustomUserAdmin)
