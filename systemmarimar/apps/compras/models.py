from django.db import models
from django.utils import timezone

# Create your models here.
class Producto(models.Model):
    nombre = models.CharField(max_length=100, null=False)
    descripcion = models.TextField(null=True, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    cantidad_en_stock = models.IntegerField(null=False)
    fecha_insercion = models.DateTimeField(default=timezone.now)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre
    

class Compra(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(null=False)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    fecha_compra = models.DateTimeField(default=timezone.now)
    proveedor = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return '{} - {} unidades'.format(self.producto.nombre, self.cantidad)