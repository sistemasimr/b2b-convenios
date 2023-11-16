
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
    empty_columns = ['nombres', 'apellidos', 'tipo_documento', 'documento', 'genero', 'celular','cupo']
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
    validate_names_last_names = r"^[A-Za-zñÑáéíóúÁÉÍÓÚüÜ\s]+$"
    
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
    
def validate_customer_quota(quota):
    quota_str = str(quota)
    validate_quota = r'^\d{1,8}(\.\d{1,2})?$'

    if re.match(validate_quota, quota_str):
        return True
    else: 
        return False
    
def validate_customer_quota_range(quota):
    quota_str = str(quota)

    quota_float = float(quota_str)
    if quota_float > 1000000:
        return False

    return True
    
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
        folder_name = Path(f'{os.getcwd()}/commons/files/cargas/')
        file_name = f'CRECUP{fecha}.txt'

        full_path = os.path.join(folder_name, file_name)
        
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        cursor_b2b = connections['default'].cursor()
        query = 'SELECT * FROM vw_customers_customers_agreements'
        cursor_b2b.execute(query)
        results = cursor_b2b.fetchall()

        with open(full_path, 'w') as file:
            for row in results:
                document, quota = row
                quota = int(quota)
                # line_update = f'{document}|{quota}|{quota}|0\n' se comenta esta linea, ya que esta sera para la actualización de cupo
                line = f'{document}|{quota}\n'
                file.write(line)

        return True 
    except Exception as e:
        error_message = f'Error al generar y guardar el archivo TXT: {str(e)}'
        return {'message': error_message}
    
def upload_file_to_ftp():
    try:
        fecha = datetime.now().strftime("%Y%m%d")
        file_name = f'CRECUP{fecha}.txt'

        file_path = Path(os.path.join(os.getcwd(), f'commons/files/cargas/{file_name}'))

        ftp_comerssia = conexion_ftp()
        ftp_comerssia = conexion_ftp().obtener_ftp_salida()
        ftp_comerssia.encoding = 'utf-8'
        ftp_comerssia.sendcmd('OPTS UTF8 ON')

        with open(file_path, 'rb') as file:
            ftp_comerssia.storbinary(f"STOR {file_name}", file, 1024)

        ftp_comerssia.quit()

        print(f'¡Éxito! Archivo {file_name} cargado correctamente al servidor FTP.')
        return True

    except Exception as e:
        traceback.print_exc()
        error_message = f'{str(e)}'
        print(error_message)
        return False,error_message

    
def list_users():
    customers = Customer.objects.all().order_by('-is_active')
    serializer = CustomerSerializer(customers, many=True)
    return serializer.data

    



