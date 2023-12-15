
from datetime import datetime
from django.db import connections
from pathlib import Path
from rest_framework.response import Response
from django.core.mail import EmailMessage


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

def validate_empty_columns_update_customers(df):
    empty_columns = ['documento','cupo']
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
    
def validate_customer_quota_negative(quota):
    quota_str = str(quota)
    validate_quota = r'^-?\d{1,8}(\.\d{1,2})?$'

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


def send_delete_customer_email(email,documents):
    documents_formatted = ",<br>".join(map(str, documents))

    menssage = f"Estos son los clientes que han sido eliminados: <br> <br> {documents_formatted} <br> <br> \n"
    email = EmailMessage(
        subject="Clientes eliminados de venta credito en b2b",
        body=menssage,
        from_email="Clientes eliminados de venta credito en b2b <bigjohnsistemas@gmail.com>",
        to=email,
        headers={"X-MJ-TemplateLanguage": 1},
    )
    email.content_subtype = "html"
    email.send()

def send_activate_customer_email(email,documents):
    documents_formatted = ", ".join(str(doc) for doc in documents)

    menssage = f"Estos son los clientes que han sido activados: <br> <br> {documents_formatted} <br> <br> \n"
    email = EmailMessage(
        subject="Clientes activados de venta credito en b2b",
        body=menssage,
        from_email="Clientes activados de venta credito en b2b <bigjohnsistemas@gmail.com>",
        to=email,
        headers={"X-MJ-TemplateLanguage": 1},
    )
    email.content_subtype = "html"
    email.send()

def file_comerssia(lines):
    try:
        fecha = datetime.now().strftime("%Y%m%d")
        folder_name = Path(f'{os.getcwd()}/commons/files/cargas/')
        file_name = f'CRECRE{fecha}.txt'

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        full_path = os.path.join(folder_name, file_name)

        with open(full_path, 'w') as file:
            for line in lines:
                file.write(line)

        return True
    
    except Exception as e:
        error_message = f'Error al generar y guardar el archivo TXT: {str(e)}'
        return {'message': error_message}


def upload_file_to_ftp():
    try:
        fecha = datetime.now().strftime("%Y%m%d")
        file_name = f'CRECRE{fecha}.txt'

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
    
def file_comerssia_update_discre(lines):
    try:
        fecha = datetime.now().strftime("%Y%m%d")
        folder_name = Path(f'{os.getcwd()}/commons/files/cargas/')
        file_name = f'DISCRE{fecha}.txt'

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        full_path = os.path.join(folder_name, file_name)

        with open(full_path, 'w') as file:
            for line in lines:
                file.write(line)

        return True

    except Exception as e:
        error_message = f'Error al generar y guardar el archivo TXT: {str(e)}'
        return {'message': error_message}
    
def upload_file_to_ftp_discre():
    try:
        fecha = datetime.now().strftime("%Y%m%d")
        file_name = f'DISCRE{fecha}.txt'

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

def file_comerssia_update_aumcre(lines):
    try:
        fecha = datetime.now().strftime("%Y%m%d")
        folder_name = Path(f'{os.getcwd()}/commons/files/cargas/')
        file_name = f'AUMCRE{fecha}.txt'

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        full_path = os.path.join(folder_name, file_name)

        with open(full_path, 'w') as file:
            for line in lines:
                file.write(line)

        return True

    except Exception as e:
        error_message = f'Error al generar y guardar el archivo TXT: {str(e)}'
        return {'message': error_message}


def upload_file_to_ftp_aumcre():
    try:
        fecha = datetime.now().strftime("%Y%m%d")
        file_name = f'AUMCRE{fecha}.txt'

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

    
def validate_quota_comerssia(documents):
    cursor_b2b = connections['bigjohndb'].cursor()

    document_str = ', '.join(str(doc) for doc in documents)

    query = f"""SELECT
                    clicodigo,
                    cfnvalor2 
                FROM
                    BIGJOHN.dbo.CodigosFinancieros 
                WHERE
                    TCFcodigo = 06 
                    AND cfnvalor3 <> 0 
                    AND cfnvalor2 <> 0
                    AND clicodigo in ({document_str})
            """
    
    cursor_b2b.execute(query)
    results = cursor_b2b.fetchall()
    
    return results


def list_users():
    customers = Customer.objects.filter(is_active=True).order_by('-id')
    serializer = CustomerSerializer(customers, many=True)
    return serializer.data

    
