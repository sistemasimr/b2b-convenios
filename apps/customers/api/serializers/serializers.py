from rest_framework import serializers
from ...models import Customer
from django.db import connections


class CustomerSerializer(serializers.ModelSerializer):
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    available_balance = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    used_balance = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Customer
        fields = ('first_name', 'last_name', 'is_active', 'document', 'document_type_display', 'quota', 'available_balance', 'used_balance')

def get_available_balance():
    cursor_b2b = connections['bigjohndb'].cursor()
    query = """SELECT clicodigo, cfnvalor2, cfnvalor3 FROM BIGJOHN.dbo.CodigosFinancieros WHERE TCFcodigo = 06"""
    cursor_b2b.execute(query)
    results = cursor_b2b.fetchall()

    balance_dict = {row[0]: {'available_balance': row[1], 'used_balance': row[2]} for row in results}


    return balance_dict

balances = get_available_balance()

customers = Customer.objects.all()

serialized_customers = []

for customer in customers:
    customer_data = CustomerSerializer(customer).data
    document = customer_data['document']
    
    if document in balances:
        customer_data['available_balance'] = balances[document]['available_balance']
        customer_data['used_balance'] = balances[document]['used_balance']

    serialized_customers.append(customer_data)

        
 