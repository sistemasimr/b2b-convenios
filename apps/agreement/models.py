from django.db import models
from django.utils import timezone
from apps.company.models import Company

class Agreement(models.Model):
    name = models.CharField(max_length=60)
    quota = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, blank=True)
    company = models.ManyToManyField(Company,related_name='company')

    def __str__(self):
        return f'{self.name} {self.quota}'
    
    class Meta:
        verbose_name = "Agreement"
        verbose_name_plural = "Agreements"
        
    

    

