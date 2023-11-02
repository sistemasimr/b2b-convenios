from django.urls import path
from .views.views import * 

urlpatterns = [
    path('customers_load/<str:type>/', CustomersLoad.as_view() , name='customers_load'),

]