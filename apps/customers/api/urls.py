from django.urls import path
from .views.views import * 

urlpatterns = [
    path('customers_load/<str:type>/', CustomersLoad.as_view() , name='customers_load'),
    path('list_customers/', ListCustomers.as_view() , name='list_customers'),

]