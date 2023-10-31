# -*- coding: utf-8 -*-
from django.utils import timezone
from django.contrib.auth.hashers import check_password
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from ..functions.functions import *
from ..authentication.authentication import CodeAuthentication
from ...models import *
from ..serializers.serializers import *

from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication

import hashlib
import re


class LoginViewUser(TokenObtainPairView):
    """
    Takes a set of user credentials and returns an access and refresh JSON web
    token pair to prove the authentication of those credentials.

    """

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        req = request.data
        document = req.get('document')
        password = req.get('password')

        if not document:
            data = {'message': 'El documento está vacío o no se proporcionó','data':'', 'code': 2}
            return Response(data,status=200)
        elif not password:
            data = {'message': 'La contraseña está vacía o no se proporcionó','data': '','code': 2}
            return Response(data,status=200)
  
        pattern = '[0-9]+'
        document = re.findall(pattern, document)
        document = document[0]
        
        try:
            user = User.objects.get(document=request.data.get('document'))
        except User.DoesNotExist:
            data = {'message': 'El usuario no existe','data':'', 'code': 2}
            return Response(data, status=200)
        
        if not check_password(password, user.password):
            data = {'message': 'La contraseña no es correcta', 'data': '', 'code': 2}
            return Response(data, status=200)
    
        user.last_login = timezone.now()
        user.save()

        if serializer.is_valid():
            response = super(LoginViewUser, self).post(request, *args, **kwargs)
            res = response.data
            token = res.get('access')
            request.user = user
            usuario = UserSerializer(user, context={'request': request}).data
            data = {'message': 'Inicio de sesión exitoso', 'data': token, 'code': 1, "user":usuario}
 
        return Response(data,status=200)
 
 
class SendCode(APIView):
    """
        Esta vista permite enviar un código de verificación a un usuario por correo electrónico.
        El código de verificación se genera aleatoriamente, se almacena en la base de datos junto con la 
        información del usuario y se envía al usuario por correo electrónico.

        Parámetros de entrada:
        - email: La dirección de correo electrónico del usuario al que se enviará el código de verificación.

        Respuestas:
        - 200 OK: El correo electrónico se envió con éxito.
        - 404 Not Found: El correo no se encuentra registrado en la base de datos.
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            emails = request.data.get('email')  

            if not is_valid_email(emails):
                data = {'message': "El correo electrónico no es válido.", "data": '', "code": 2}
                return Response(data, status=200) 
            
            user = User.objects.get(email=emails)
            last_reset_code = PasswordResetCode.objects.filter(user=user).order_by('-created_at').first()
            
            if last_reset_code:
                time_since_last_request = timezone.now() - last_reset_code.created_at
                
                if time_since_last_request < timezone.timedelta(minutes=1):
                    data = {'message': "Debes esperar un minuto para solicitar un nuevo código.","data": '', "code": 2}
                    return Response(data, status=200) 
                
                last_reset_code.is_active = False
                last_reset_code.save()

            code = get_random_code()
            code_hash = hashlib.sha256(code.encode()).hexdigest()
            expiration_date = timezone.now() + timezone.timedelta(minutes=3)

            reset_code = PasswordResetCode.objects.create(code=code_hash, user=user, 
                                                          expiration_date=expiration_date)

            send_verification_email(emails,code)

            data = {'message': f"Correo enviado con éxito a {emails}", "code": 1}
            return Response(data, status=200)
        
        except User.DoesNotExist:
            if emails == '':
                data = {'message': "El correo es obligatorio.", 'code': 2}
                return Response(data, status=200)
            
            data = {'message': f"Este correo no se encuentra registrado en nuestras bases de datos. Por favor valida o comunícate con el administrador.", 'code': 2}
            return Response(data,status=200)
        

class GetTokenCode (APIView):
    """
        Esta vista maneja la obtención de tokens de acceso a través de autenticación por código.
    """

    authentication_classes = [CodeAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            refresh = RefreshToken.for_user(user)

            access_token = str(refresh.access_token)

            data = {
                'access_token': access_token,
                'token_type': 'bearer',
                'code': 1
            }
            return Response(data, status=200)
        except Exception as e:
            data = {'message': f"Ha ocurrido un error: {str(e)}"}
            return Response(data, status=500)
        
        
class UpdatePassword (APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            new_password = request.data.get('new_password')
            confirm_password = request.data.get('confirm_password') 
            user = request.user

            if new_password != confirm_password:
                data = {'message': "Las contraseñas no coinciden","data": '', "code": 2}
                return Response(data, status=200)
            
            if not (re.search(r'[A-Z]', new_password) and
                    re.search(r'[a-z]', new_password) and
                    re.search(r'[0-9]', new_password) and
                    re.search(r'[@#$%^!¡&+=/*.-]', new_password)):
                
                data = {'message': 'La contraseña debe contener al menos una mayúscula, una minúscula, un número y un carácter especial',"data": '' ,"code": 2}
                return Response(data, status=200)
            
            user.set_password(new_password)
            user.save()
            
            data = {'message': "Contraseña actualizada con éxito", "data": '', "code": 1}
            return Response(data, status=200)

        except Exception as e:
            data = {'message': f"Ha ocurrido un error: {str(e)}"}
            return Response(data, status=500)
        
class CustomPasswordChangeView(PasswordChangeView):
    success_url = reverse_lazy('password_change_done')