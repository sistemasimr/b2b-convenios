from django.urls import path
from .views.views import * 

urlpatterns = [
    path('token/', LoginViewUser.as_view() , name='token'),
    path('send_code/', SendCode.as_view() ,name='send_code'),
    path('get_token_code/' , GetTokenCode.as_view(), name='get_token_code'),
    path('update_password/', UpdatePassword.as_view(), name='get_token_code'),
    path('change_password/', CustomPasswordChangeView.as_view(), name='change_password_view_name'),

]