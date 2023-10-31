# -*- coding: utf-8 -*-

import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from ...models import * 
from ..functions.functions import *

class CustomersLoad(APIView):
    def post(self, request, *args, **kwargs):
        
        if 'clientes' not in request.FILES:
            data = {'message': 'No se ha proporcionado un archivo Excel', 'data': None, 'code': 2}
            return Response(data, status=200)

        archive = request.FILES['clientes']
        
        if not archive.name.endswith('.xlsx'):
            data = {'message': 'No es un archivo válido, Recuerde que solo se permiten archivos con formato xlsx', 'data': None, 'code': 2}
            return Response(data, status=200)

        try:

            document_type_mapping = {
                'cc': 1,
                'ti': 2,
                'ce': 3,
            }

            df = pd.read_excel(archive)
            
            for index, row in df.iterrows():
                document_type_excel = row['tipo_documento'].lower() 
                id_agreement = row['cod_convenio']
                document_number = row['documento']

                if document_type_excel in document_type_mapping:
                    document_type_model = document_type_mapping[document_type_excel]

                if Customer.objects.filter(document=document_number).exists():
                    data = {'message': f'El documento {document_number} ya existe en la base de datos', 'data': None, 'code': 2}
                    return Response(data, status=200)
                
                if not Agreement.objects.filter(id=id_agreement).exists():
                    data = {'message': f"El convenio con id: {id_agreement} no existe en la base de datos", 'data': None, 'code': 2}
                    return Response(data, status=200)

                customer = Customer(
                    first_name=row['nombres'],
                    last_name=row['apellidos'],
                    document_type=document_type_model,
                    document=document_number,
                    gender=row['genero'],
                    cellphone=row['celular'],
                    email=row['email']
                                
                )

                customer.save()
                create_client_agreement(id_agreement, customer)
            
            data = {'message': 'Archivo Excel cargado y procesado con éxito', 'data': df.to_dict(orient='records'), 'code': 1}
            return Response(data, status=200)
        except Exception as e:
            data = {'message': 'Error al procesar el archivo Excel', 'data': str(e), 'code': 2}
            return Response(data, status=200)

    
      
 
