
from datetime import datetime
from django.db import connections
from rest_framework.response import Response

from apps.agreement.models import Agreement
from ..serializers.serializers import *

import os
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
    

def file_comerssia():
    try:
        fecha = datetime.now().strftime("%Y%m%d")
        folder_name = 'C:\\cargas'
        file_name = f'B2B{fecha}.txt'

        if not os.path.exists(folder_name):
            os.mkdir(folder_name)

        cursor_b2b = connections['default'].cursor()
        query = 'SELECT * FROM vw_customers_customers_agreements'
        cursor_b2b.execute(query)
        results = cursor_b2b.fetchall()

        with open(os.path.join(folder_name, file_name), 'w') as file:
            for row in results:
                document, quota = row

                quota = int(quota)

                line = f'{document}|{quota}|{quota}|0\n'
                file.write(line)

        return True 
    except Exception as e:
        error_message = f'Error al generar y guardar el archivo TXT: {str(e)}'
        return {'message': error_message}
    

def list_users():
    customers = Customer.objects.all()
    serializer = CustomerSerializer(customers, many=True)
    return serializer.data

    



