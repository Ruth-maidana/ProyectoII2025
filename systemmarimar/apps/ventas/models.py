from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone


# Create your models here.

class Cliente(models.Model):
    nombre = models.CharField(max_length=50,null=False)
    apellido = models.CharField(max_length=50,null=False)
    nro_documento = models.CharField(max_length=30,null=False,unique=True)
    nacionalidad = models.CharField(max_length=30,null=False)
    estado_civil = models.CharField(max_length=30,null=False)
    num_regex = RegexValidator(regex = r"^\+?1?\d{8,15}$",message="Ingrese un numero de telefono valido.")
    num_tel = models.CharField(validators = [num_regex], max_length = 16, unique = True)
    correo = models.EmailField(max_length=30,null=False,unique=True)
    direccion = models.CharField(max_length=30,null=False)
    #fecha_insercion = models.DateTimeField(auto_now_add=True)
    fecha_insercion = models.DateTimeField(default=timezone.now)
    activo = models.BooleanField(default=True)
    fecha_modificacion = models.DateTimeField(null=True)
    #fecha_modificacion = models.DateTimeField(auto_now_add=True)

        
    def __str__(self):
        return'{}'.format(self.nombre,self.apellido,self.num_tel,self.correo,self.direccion,self.activo,self.fecha_insercion)
