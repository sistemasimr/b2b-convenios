# En utils.py
from django.core.mail import EmailMessage
import re
import random

def send_verification_email(emails,code):
    menssage = f"Este es su código de verificación: {code} <br> <br> \n Recuerde que el código expira en 3 minutos"
    email = EmailMessage(
        subject="Código verificacion",
        body=menssage,
        from_email="Código de verificación <bigjohnsistemas@gmail.com>",
        to=[emails],
        headers={"X-MJ-TemplateLanguage": 1},
    )
    email.content_subtype = "html"
    email.send()


def get_random_code(length=6):
  """Genera un código aleatorio de longitud especificada que solo contiene números."""
  code = ''.join(random.choice('0123456789') for _ in range(length))
  code = re.sub(r'\D', '', code)
  return code

def is_valid_email(email):
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if re.match(email_pattern, email):
        return True
    else:
        return False
