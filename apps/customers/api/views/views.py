import pandas as pd
# import openpyxl
# import random

from rest_framework.views import APIView
from rest_framework.response import Response

from ...models import * 
from ..functions.functions import *


class CustomersLoad(APIView):
    def post(self, request,type):
        
        if 'clientes' not in request.FILES:
            data = {'message': 'No se ha proporcionado un archivo Excel', 'data': None}
            return Response(data, status=400)
    
        archive = request.FILES['clientes']
        allowed_extensions = ['.xlsx', '.xls']
    
        if not any(archive.name.endswith(ext) for ext in allowed_extensions):
            data = {'message': 'No es un archivo válido. Recuerde que solo se permiten archivos con formato .xlsx o .xls', 'data': None}
            return Response(data, status=400)

        try:
            if type == 'create':
                document_type_mapping = {
                    'cc': 1,
                    'ti': 2,
                    'ce': 3,
                }

                df = pd.read_excel(archive)

                required_columns = ['nombres', 'apellidos', 'tipo_documento', 'documento', 'genero', 'celular']

                if not all(col in df.columns for col in required_columns):
                    missing_columns = [col for col in required_columns if col not in df.columns]
                    data = {'message': f'Faltan los siguientes encabezados en el archivo Excel: {", ".join(missing_columns)}', 'data': None}
                    return Response(data, status=400)
                
                if df.isnull().values.any():
                    is_empty = df.isnull()

                    empty_fields = is_empty.any()
                    empty_columns = empty_fields[empty_fields].index.tolist()
                    empty_columns = [col for col in empty_columns if 'Unnamed' not in col]

                    data = {'message': f'El archivo Excel contiene campos vacíos{empty_columns}', 'data': None}
                    return Response(data, status=400)

                id_agreement = 1

                for index, row in df.iterrows():
                    document_type_excel = row['tipo_documento']

                    if isinstance(document_type_excel, str):
                        document_type_excel = document_type_excel.lower()
                    else:
                        data = {'message': 'Recuerda que los tipos de documento válidos son: cc, ti, ce', 'data': None}
                        return Response(data, status=400)

                    document_number = row['documento']

                    if document_type_excel in document_type_mapping:
                        document_type_model = document_type_mapping[document_type_excel]

                    if Customer.objects.filter(document=document_number).exists():
                        data = {'message': f'El documento {document_number} ya existe en la base de datos', 'data': None}
                        return Response(data, status=409)

                    if not Agreement.objects.filter(id=id_agreement).exists():
                        data = {'message': f"El convenio con id: {id_agreement} no existe en la base de datos", 'data': None}
                        return Response(data, status=404)

                    if not validate_customer_names_last_names(row['nombres'], row['apellidos']):
                        data = {'message': 'Los nombres y apellidos deben contener solo letras', 'data': None}
                        return Response(data, status=400)

                    if not validate_customer_document_type(row['tipo_documento']):
                        data = {'message': 'El tipo de documento debe contener solo letras', 'data': None}
                        return Response(data, status=400)

                    if not validate_customer_gender(row['genero']):
                        data = {'message': 'El género debe contener solo letras', 'data': None}
                        return Response(data, status=400)

                    customer = Customer(
                        first_name=row['nombres'],
                        last_name=row['apellidos'],
                        document_type=document_type_model,
                        document=document_number,
                        gender=row['genero'],
                        cellphone=row['celular'],
                    )

                    customer.save()
                    create_client_agreement(id_agreement, customer)

                    list_customer= list_users()
                    archive_comerssia = file_comerssia()

                    if not isinstance(archive_comerssia,bool) and archive_comerssia:
                        data = {'message': 'Ha ocurrido un error al guardar la informacion en comerssia'}
                        return Response(data, status=500)
                      
                data = {'message': 'Archivo Excel cargado y procesado con éxito', 'data': list_customer}
                return Response(data, status=200)

            
            elif type == 'delete':

                df = pd.read_excel(archive)
                required_columns = ['documento']
                
                if not all(col in df.columns for col in required_columns):
                    missing_columns = [col for col in required_columns if col not in df.columns]
                    data = {'message': f'Faltan el siguiente encabezado en el archivo Excel: {", ".join(missing_columns)}', 'data': None}
                    return Response(data, status=400)
                
                      
                if df.isnull().values.any():
                    is_empty = df.isnull()

                    empty_fields = is_empty.any()
                    empty_columns = empty_fields[empty_fields].index.tolist()
                    empty_columns = [col for col in empty_columns if 'Unnamed' not in col]

                    data = {'message': f'El archivo Excel contiene campos vacíos{empty_columns}', 'data': None}
                    return Response(data, status=400)
                
                for index, row in df.iterrows():
                    document = row['documento']

                    try:
                        customer = Customer.objects.get(document=document)
                        customer.is_active = False 
                        customer.save()
                    except Customer.DoesNotExist:
                        data = {'message': f'El usuario {document} no existe ', 'data': None}
                        return Response(data, status=400)
                    
                list_customer = list_users()
                      
                data = {'message': 'Usuarios eliminados con éxito', 'data': list_customer}
                return Response(data, status=200)

        except Exception as e:
            data = {'message': 'Error al procesar el archivo Excel', 'data': str(e)}
            return Response(data, status=500)
        
class ListCustomers(APIView):
    def get(self, request):
        try:
            list_customer = list_users()  
            data = {'message': 'Listado de clientes', 'data': list_customer}
            return Response(data, status=200)
        
        except Exception as e:
            data = {'message': 'Error al listar clientes', 'data': str(e)}
            return Response(data, status=500)
        
# class ListCustomers(APIView):
#     def get(self, request):

#             # Definir listas de valores posibles para cada columna
#             nombres = ["Ange", "Elena", "Luis", "Maria", "Pedro"]
#             apellidos = ["Gomez", "Lopez", "Rodriguez", "Martinez", "Santos"]
#             tipos_documento = ["CC", "CE", "TI"]
#             generos = ["M", "F"]
#             celulares = ["12345", "67890", "55555", "99999"]

#             # Función para generar un número de documento único
#             def generar_documento_unico(documentos_existentes):
#                 while True:
#                     documento = str(random.randint(100000, 999999))
#                     if documento not in documentos_existentes:
#                         documentos_existentes.add(documento)
#                         return documento

#             # Crear un nuevo archivo de Excel
#             archivo_excel = openpyxl.Workbook()
#             hoja = archivo_excel.active

#             # Definir los encabezados de las columnas
#             hoja.append(["Nombres", "Apellidos", "Tipo de Documento", "Documento", "Género", "Celular"])

#             # Llevar un registro de los documentos generados
#             documentos_existentes = set()

#             # Generar datos aleatorios y escribirlos en el archivo Excel
#             for _ in range(5000):  # Cambia el número 10 a la cantidad deseada de filas de datos
#                 nombre = random.choice(nombres)
#                 apellido = random.choice(apellidos)
#                 tipo_documento = random.choice(tipos_documento)
#                 documento = generar_documento_unico(documentos_existentes)
#                 genero = random.choice(generos)
#                 celular = random.choice(celulares)

#                 hoja.append([nombre, apellido, tipo_documento, documento, genero, celular])

#             # Guardar el archivo Excel
#             archivo_excel.save("datos.xlsx")

#             print("Datos generados y guardados en datos.xlsx")
                   
#             data = {'message': 'Usuarios eliminados con éxito', 'data': ''}
#             return Response(data, status=200)




