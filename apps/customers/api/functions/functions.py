from apps.agreement.models import Agreement
from rest_framework.response import Response

from django.db import connections
from ..serializers.serializers import *


import re

def create_client_agreement(id_agreement, customer):
    try:
        agreement_instance = Agreement.objects.get(id=id_agreement)
        customer.agreements.add(agreement_instance)
        return True 
    except Agreement.DoesNotExist:
        return False
    

def validate_customer_names_last_names(first_name,last_name):
    validate_names_last_names = r"^[A-Za-z ]+$"

    if re.match(validate_names_last_names, first_name) and re.match(validate_names_last_names, last_name):
        return True
    else:
        return False
    
    
def validate_customer_document_type(document_type):
    validate_document_type = r"^[A-Za-z ]+$"

    if re.match(validate_document_type, document_type):
        return True
    else:
        return False
    

def validate_customer_gender(gender):
    validate_gender = r"^[A-Za-z ]+$"
    
    if re.match(validate_gender, gender):
        return True
    else:
        return False
    

def validate_user_comerssia():
    try:
        cursor_comerssia = connections['bigjohndb'].cursor()
        query = 'SELECT CLICodigo FROM [BIGJOHN_BA].dbo.VW_CLIENTES'
        cursor_comerssia.execute(query)
        results = cursor_comerssia.fetchall()

        
        return True 
    except Exception as e:
        print(f"Error en la consulta: {str(e)}")
        return False
    

def list_users():
    customers = Customer.objects.all()
    serializer = CustomerSerializer(customers, many=True)
    return serializer.data

    



