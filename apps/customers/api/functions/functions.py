
from datetime import datetime
from django.db import connections
from pathlib import Path
from rest_framework.response import Response

from apps.agreement.models import Agreement
from commons.classes import conexion_ftp
from ..serializers.serializers import *

import os
import re
import sys
import traceback

def validate_empty_columns_create_customers(df):
    empty_columns = ['nombres', 'apellidos', 'tipo_documento', 'documento', 'genero', 'celular']
    empty_rows = df[df[empty_columns].isnull().any(axis=1)]

    if not empty_rows.empty:
        return True

    return False

def validate_empty_columns_delete_customers(df):
    empty_columns = ['documento']
    empty_rows = df[df[empty_columns].isnull().any(axis=1)]

    if not empty_rows.empty:
        return True

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
    
def validate_customer_cellphone(cellphone):
    cellphone_str = str(cellphone)

    validate_cellphone = r"^[0-9]+$"
    
    if re.match(validate_cellphone, cellphone_str):
        return True
    else:
        return False
    
def validate_customer_cellphone_length(cellphone):
    if len(str(cellphone)) <= 10:
        return True
    else:
        return False
    

def disable_customer(df):
    does_not_exist = []

    for index, row in df.iterrows():
        document = row['documento']

        customer = Customer.objects.filter(document=document).first()
        
        if customer:
            Customer.objects.filter(document=document).update(is_active=False)
        else:
            does_not_exist.append(f'El usuario {document} no existe')

    return does_not_exist

def file_comerssia():
    try:
        fecha = datetime.now().strftime("%Y%m%d")
        folder_name = 'C:\\cargas'
        file_name = f'CRECUP{fecha}.txt'

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
                # line_update = f'{document}|{quota}|{quota}|0\n' se comenta esta linea, ya que esta sera para la actualización de cupo
                line = f'{document}|{quota}\n'
                file.write(line)

        # upload_file_to_ftp(file_name)
        # se comenta la linea del archivo ftp mientras se puede hacer pruebas

        return True 
    except Exception as e:
        error_message = f'Error al generar y guardar el archivo TXT: {str(e)}'
        return {'message': error_message}
    
def upload_file_to_ftp(file_name):
    try:
        file_path = Path(f'C:\\cargas') / file_name

        ftp_comerssia = conexion_ftp()
        ftp_comerssia = ftp_comerssia.getInstance()
        ftp_comerssia.cwd('Interfaces/Salida')
        ftp_comerssia.encoding='utf-8'
        ftp_comerssia.sendcmd('OPTS UTF8 ON')

        file = open(file_path,'rb')
        ftp_comerssia.storbinary("STOR "+ file_name, file, 1024)

        ftp_comerssia.quit()

    except Exception as e:
        traceback.print_exc()
        e = sys.exc_info()[1]
        data = {'message': str(e), 'code': 2, 'data': None}
        return Response(data, status=200)
    

def list_users():
    customers = Customer.objects.all().order_by('-is_active')
    serializer = CustomerSerializer(customers, many=True)
    return serializer.data

    



