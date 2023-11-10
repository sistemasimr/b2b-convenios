import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response

from ...models import * 
from ..functions.functions import *
from django.db import transaction



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
                
                if df.empty:
                    data = {'message': 'El archivo Excel está vacío.', 'data': None}
                    return Response(data, status=400)
                
                validate_create = validate_empty_columns_create_customers(df)

                if validate_create:
                    data = {'message': 'No pueden ir columnas vacías'}
                    return Response(data, status=500)

                id_agreement = 1
                customers_to_create = []

                for index, row in df.iterrows():
                    document_type_excel = row['tipo_documento']

                    if isinstance(document_type_excel, str):
                        document_type_excel = document_type_excel.lower()
                    else:
                        data = {'message': 'Recuerda que los tipos de documento válidos son (cc, ti, ce)', 'data': None}
                        return Response(data, status=400)

                    document_number = row['documento']
                    gender = row['genero'].upper()

                    if gender not in ('M', 'F','O'):
                        data = {'message': f'Valor de género no válido: {gender}, recuerda que los permitidos son (M, F, O)', 'data': None}
                        return Response(data, status=400)

                    if document_type_excel in document_type_mapping:
                        document_type_model = document_type_mapping[document_type_excel]
                    else:
                        data = {'message': f'Tipo de documento: {document_type_excel} no válido, recuerda que los permitidos son (cc,ti o ce)', 'data': None}
                        return Response(data, status=400) 
                    
                    if Customer.objects.filter(document=document_number,is_active=True).exists():
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
                    
                    if not validate_customer_cellphone(row['celular']):
                        data = {'message': 'El número de celular debe contener solo números', 'data': None}
                        return Response(data, status=400)
                    
                    if not validate_customer_cellphone_length(row['celular']):
                        data = {'message': 'El número de celular es demasiado largo. Solo se permite 10 digitos', 'data': None}
                        return Response(data, status=400)
                    
                    if Customer.objects.filter(document=document_number, is_active=False).exists():
                        existing_customer = Customer.objects.get(document=document_number, is_active=False)
                        existing_customer.is_active = True
                        existing_customer.save()
                        
                        continue
                    
                    customer = Customer(
                        first_name=row['nombres'],
                        last_name=row['apellidos'],
                        document_type=document_type_model,
                        document=document_number,
                        gender=gender,
                        cellphone=row['celular'],
                    )

                    customers_to_create.append(customer)
                try:
                    Customer.objects.bulk_create(customers_to_create)
                    created_customers = Customer.objects.filter(id__in=[c.id for c in customers_to_create])

                    agreement_instance = Agreement.objects.get(id=id_agreement)

                    agreement_instance.customers.add(*created_customers)
                    
                except Exception as e:
                   return Response({"message": str(e)}, status=500)
                    
                list_customer= list_users()

                try:
                   archive_comerssia = file_comerssia()
                except Exception as e:
                   return Response({"error_message": str(e)}, status=500)

                data = {'message': 'Archivo Excel cargado y procesado con éxito', 'data': list_customer}
                return Response(data, status=200)

            
            elif type == 'delete':

                df = pd.read_excel(archive)
                required_columns = ['documento']
                
                if not all(col in df.columns for col in required_columns) or len(df.columns) > 1:
                    if len(df.columns) > 1:
                        message = 'El archivo Excel tiene más de un encabezado. Debe tener solo un encabezado llamado "documento".'
                    else:
                        missing_columns = [col for col in required_columns if col not in df.columns]
                        message = f'Falta el encabezado en el archivo Excel: {", ".join(missing_columns)}'

                    data = {'message': message, 'data': None}
                    return Response(data, status=400)

                
                if df.empty:
                    data = {'message': 'El archivo Excel está vacío.', 'data': None}
                    return Response(data, status=400)
                
                validate_create = validate_empty_columns_delete_customers(df)

                if validate_create:
                    data = {'message': 'No pueden ir columnas vacías'}
                    return Response(data, status=500)
                
                validate_disable_customer = disable_customer(df)

                if validate_disable_customer:
                    data = {'message': ', '.join(validate_disable_customer)}
                    return Response(data, status=500)
    
                list_customer = list_users()
                archive_comerssia = file_comerssia()

                # if not isinstance(archive_comerssia,bool) and archive_comerssia:
                #     data = {'message': 'Ha ocurrido un error al guardar la informacion en comerssia'}
                #     return Response(data, status=500)
                      
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



