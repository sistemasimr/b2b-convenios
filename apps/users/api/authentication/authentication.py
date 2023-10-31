from rest_framework import authentication
from ...models import PasswordResetCode
import hashlib
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed

class CodeAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        code = request.data.get('code')
        if not code:
            raise AuthenticationFailed(detail={"message": "El código es obligatorio.", "code": 2})

        code_hash = hashlib.sha256(code.encode()).hexdigest()
        reset_code = PasswordResetCode.objects.filter(code=code_hash, is_active=True).first()

        if reset_code:
            if reset_code.expiration_date > timezone.now():
                reset_code.is_active = False
                reset_code.save()
                refresh = RefreshToken.for_user(reset_code.user)
                return (reset_code.user, refresh)
            else:
                raise AuthenticationFailed(detail={"message": "El código ha expirado. Debes solicitar uno nuevo.", "code": 2})

        else:
            raise AuthenticationFailed(detail={"message": "Código no válido. Por favor, verifica el código ingresado.", "code": 2})
