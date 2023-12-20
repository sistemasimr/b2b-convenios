from rest_framework import serializers
from ...models import Customer
from django.db import connections


class CustomerSerializer(serializers.ModelSerializer):
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    saldo_disponible = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    saldo_usado = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Customer
        fields = ('first_name', 'last_name', 'is_active', 'document', 'document_type_display', 'quota', 'saldo_disponible', 'saldo_usado')

def get_available_balance():
    cursor_b2b = connections['bigjohndb'].cursor()
    query = """SELECT clicodigo, cfnvalor2, cfnvalor3 FROM BIGJOHN.dbo.CodigosFinancieros WHERE TCFcodigo = 06"""
    cursor_b2b.execute(query)
    results = cursor_b2b.fetchall()

    balance_dict = {row[0]: {'saldo_disponible': row[1], 'saldo_usado': row[2]} for row in results}


    return balance_dict

balances = get_available_balance()

customers = Customer.objects.all()

serialized_customers = []

for customer in customers:
    customer_data = CustomerSerializer(customer).data
    document = customer_data['document']
    
    if document in balances:
        customer_data['saldo_disponible'] = balances[document]['saldo_disponible']
        customer_data['saldo_usado'] = balances[document]['saldo_usado']

    serialized_customers.append(customer_data)

        
 