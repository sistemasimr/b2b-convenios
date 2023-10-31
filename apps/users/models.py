from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from simple_history.models import HistoricalRecords


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, password,document):
        user = self.create_user(
            document,
            password=password,
        )
        user.document = document
        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)
        return user

DOCUMENT_TYPE_CHOICES = (
    (1, 'CC'),
    (2, 'TI'),
    (3, 'CE'),
)

class User(AbstractBaseUser):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    document_type = models.IntegerField(choices=DOCUMENT_TYPE_CHOICES,null=True)
    document = models.CharField(max_length=255, unique=True)
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,null=True
    )
    cellphone = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()
    objects = UserManager()

    USERNAME_FIELD = 'document'
    
    def is_staff(self):
        return self.is_admin
    
    def has_module_perms(self):
        return self.is_admin
    
    def has_perm(self, perm):
        """
        Devuelve True si el usuario tiene el permiso especificado.
        """
        # Comprueba si el usuario es un superusuario.
        if self.is_admin:
            return True

        # Obtén los permisos que tiene el usuario.
        permissions = self.get_all_permissions()

        # Comprueba si el permiso especificado está en los permisos del usuario.
        return perm in permissions

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


class PasswordResetCode(models.Model):
    code = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code