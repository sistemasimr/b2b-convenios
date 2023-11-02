from rest_framework import serializers
from ...models import Customer

class CustomerSerializer(serializers.ModelSerializer):
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)

    class Meta:
        model = Customer
        fields = ('first_name','last_name','is_active', 'document_type_display', 'agreements')

    agreements = serializers.StringRelatedField(many=True)
        
