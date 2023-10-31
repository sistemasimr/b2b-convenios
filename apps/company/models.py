from django.db import models
from django.utils import timezone

class Company(models.Model):
    name = models.CharField(max_length=100)
    nit = models.CharField(max_length=20, unique=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
        

