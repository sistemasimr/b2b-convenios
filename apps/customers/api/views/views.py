import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response

from ...models import * 
from ..functions.functions import *
from decimal import Decimal



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

                required_columns = ['nombres', 'apellidos', 'tipo_documento', 'documento', 'genero', 'celular','cupo']

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
                existing_customers = {} 
                all_lines = []

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
                    
                    if not validate_customer_quota(row['cupo']):
                        data = {'message': 'El campo cupo debe contener solo números', 'data': None}
                        return Response(data, status=400)
                    
                    if not validate_customer_quota_range(row['cupo']):
                        data = {'message': 'El campo cupo debe ser igual o menor a $1.000.000', 'data': None}
                        return Response(data, status=400)
                    
                    if Customer.objects.filter(document=document_number).exists():
                        existing_customers[document_number] = {
                            'first_name': row['nombres'],
                            'last_name': row['apellidos']
                        }
                        continue
     
                    customer = Customer(
                        first_name=row['nombres'],
                        last_name=row['apellidos'],
                        document_type=document_type_model,
                        document=document_number,
                        gender=gender,
                        cellphone=row['celular'],
                        quota=row['cupo']
                    )

                    customers_to_create.append(customer)
                    all_lines.append(f'{document_number}|{abs(row["cupo"])}\n')

                try:
                    Customer.objects.bulk_create(customers_to_create)
                    
                    created_customers = Customer.objects.filter(document__in=[customer.document for customer in customers_to_create])
                    agreement = Agreement.objects.get(id=id_agreement)
                    agreement.customers.add(*created_customers)
   
                except Exception as e:
                   return Response({"message": str(e)}, status=500)
                    
                list_customer= list_users()
                file_comerssiaa = file_comerssia(all_lines)
                upload_file_to_ftp() 
                
                if existing_customers:
                    existing_customers_message = '\n {}'.format(',\n'.join(map(str, existing_customers)))
                    data = {'message': 'Archivo procesado, estos  documentos ya existen en el sistema:\n{}'.format(existing_customers_message), 'data': list_customer, 'archivo plano cargado': file_comerssiaa}
                    return Response(data, status=200)
                else:
                    data = {'message': 'Archivo Excel cargado y procesado con éxito', 'data': list_customer, 'archivo plano cargado': file_comerssiaa}
                    return Response(data, status=200)

            elif type == 'delete':

                df = pd.read_excel(archive)
                required_columns = ['documento']
                list_documents = df['documento'].tolist()

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
                send_delete_customer_email(['cnorena@imr.com.co', 'lnarvaez@imr.com.co'],list_documents)

                data = {'message': 'Clientes eliminados con éxito', 'data': list_customer}
                return Response(data, status=200)
            
            elif type == 'update':

                df = pd.read_excel(archive)
                required_columns = ['documento','cupo']

                if not all(col in df.columns for col in required_columns):
                    missing_columns = [col for col in required_columns if col not in df.columns]
                    data = {'message': f'Faltan los siguientes encabezados en el archivo Excel: {", ".join(missing_columns)}', 'data': None}
                    return Response(data, status=400)
                
                if df.empty:
                    data = {'message': 'El archivo Excel está vacío.', 'data': None}
                    return Response(data, status=400)
                
                validate_create = validate_empty_columns_update_customers(df)

                if validate_create:
                    data = {'message': 'No pueden ir columnas vacías'}
                    return Response(data, status=500)
                
                clients_not_found = []
                clients_could_not_update = []
                clients_with_negative_quota = []
                clients_quota = []
                documents_to_activate = []
                all_lines = []
                all_lines_update_quota = []
                all_lines_positives = []

                for index, row in df.iterrows():

                    if not validate_customer_quota_negative(row['cupo']):
                        data = {'message': f'El campo cupo para el documento {row["documento"]} debe contener solo números.', 'data': None}
                        return Response(data, status=400)

                    if not validate_customer_quota_range(row['cupo']):
                        data = {'message': f'El campo cupo para el documento {row["documento"]} debe ser igual o menor a $1.000.000.', 'data': None}
                        return Response(data, status=400)
                    
                    customer = Customer.objects.filter(document=row['documento'], is_active=True).first()
                    customer_all = Customer.objects.filter(document=row['documento']).first()

                    if customer is not None:
                        current_quota = customer.quota
                        new_quota = row['cupo']

                        if new_quota < 0 and abs(new_quota) > current_quota:
                            clients_could_not_update.append(row['documento'])
                        else:
                            if row['cupo'] < 0:
                                quota_comerssia_results = validate_quota_comerssia([row['documento']])

                                if quota_comerssia_results:
                                    cfnvalor2 = quota_comerssia_results[0][1]
                                    if row['cupo'] < cfnvalor2:
                                        clients_quota.append((row['documento'], cfnvalor2))
                                    else:
                                        Customer.objects.filter(document=row['documento'], is_active=True).update(quota=current_quota - abs(row['cupo']), updated_at=timezone.now())
                                        all_lines.append(f'{row["documento"]}|{abs(row["cupo"])}\n')
                                else:
                                        Customer.objects.filter(document=row['documento'], is_active=True).update(quota=current_quota - abs(row['cupo']), updated_at=timezone.now())
                                        all_lines.append(f'{row["documento"]}|{abs(row["cupo"])}\n')
                            else:
                                Customer.objects.filter(document=row['documento'], is_active=True).update(quota=current_quota + row['cupo'], updated_at=timezone.now())
                                all_lines_positives.append(f'{row["documento"]}|{abs(row["cupo"])}\n')
                    if customer_all is None:
                        clients_not_found.append(row['documento'])

                    customer_inactive = Customer.objects.filter(document=row['documento'], is_active=False).first()

                    if customer_inactive is not None:
                        new_quota_inactive = Decimal(row['cupo'])

                        if new_quota_inactive < 0:
                            clients_with_negative_quota.append(row['documento'])

                        elif new_quota_inactive >= 0:
                            quota_from_db = customer_inactive.quota

                            if new_quota_inactive == int(quota_from_db):
                                Customer.objects.filter(document=row['documento'], is_active=False).update(is_active=True, updated_at=timezone.now())
                                documents_to_activate.append(row['documento'])
                            else: 
                                Customer.objects.filter(document=row['documento'], is_active=False).update(is_active=True, quota=new_quota_inactive, updated_at=timezone.now())
                                all_lines_update_quota.append(f'{(row["documento"])}|{abs(new_quota_inactive)}\n')
                                documents_to_activate.append(row['documento'])

                if documents_to_activate:
                    send_activate_customer_email(['cnorena@imr.com.co', 'lnarvaez@imr.com.co'], documents_to_activate)

                list_customer = list_users()
                success_message = 'Clientes actualizados con éxito'

                if clients_not_found:
                    not_found_message = f'No se encontraron clientes con los siguientes documentos: {", ".join(map(str, clients_not_found))}'
                    success_message += f', excepto los siguientes: {not_found_message}'

                if clients_quota:
                    clients_not_quota = 'No se pudieron actualizar los siguientes documentos porque el nuevo cupo es menor que el saldo disponible: {}.'.format(", ".join("({}, {})".format(x[0], format(x[1], '.2f')) for x in clients_quota))
                    success_message += f'. {clients_not_quota}'

                if clients_with_negative_quota:
                    negative_quota_message = f'Los siguientes documentos tienen un nuevo cupo negativo y no se actualizaron: {", ".join(map(str, clients_with_negative_quota))}'
                    success_message += f'. {negative_quota_message}'
                else:
                    if clients_could_not_update:
                        could_not_update_message = f'No se pudo disminuir los cupos a los siguientes documentos debido a que el nuevo cupo no puede ser mayor al actual: {", ".join(map(str, clients_could_not_update))}'
                        success_message += f'. {could_not_update_message}'

                if all_lines:
                    file_comerssia_update_discre(all_lines)
                    upload_file_to_ftp_discre()

                if all_lines_positives:
                    file_comerssia_update_aumcre(all_lines_positives)
                    upload_file_to_ftp_aumcre()

                if all_lines_update_quota:
                    file_comerssia(all_lines_update_quota)
                    upload_file_to_ftp() 

                data = {'message': success_message, 'data': list_customer}
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


