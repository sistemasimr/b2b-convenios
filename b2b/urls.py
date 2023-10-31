from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/api/', include('apps.users.api.urls')),
    path('customers/api/', include('apps.customers.api.urls'))
]
