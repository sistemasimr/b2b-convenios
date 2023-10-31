from django.db import models
from django.utils import timezone
from apps.agreement.models import Agreement
from simple_history.models import HistoricalRecords

GENDER_CHOICES = (
    ('M', 'Masculino'),
    ('F', 'Femenino'),
    ('O', 'Otro'),
)

DOCUMENT_TYPE_CHOICES = (
    (1, 'CC'),
    (2, 'TI'),
    (3, 'CE'),
)

class Customer(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    document_type = models.IntegerField(choices=DOCUMENT_TYPE_CHOICES)
    document = models.CharField(max_length=255, unique=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    cellphone = models.CharField(max_length=255)
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    agreements = models.ManyToManyField(Agreement, related_name='customers')
    history = HistoricalRecords()


    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
