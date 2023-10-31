from apps.agreement.models import Agreement

def create_client_agreement(id_agreement, customer):
    try:
        agreement_instance = Agreement.objects.get(id=id_agreement)
        customer.agreements.add(agreement_instance)
        return True 
    except Agreement.DoesNotExist:
        return False
