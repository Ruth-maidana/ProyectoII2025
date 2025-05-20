from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from apps.compras.models import Producto
from apps.compras.utils import validar_stock_venta


# Create your models here.

class Cliente(models.Model):
    nombre = models.CharField(max_length=100,null=False)
    apellido = models.CharField(max_length=100,null=False)
    nro_documento = models.CharField(max_length=100,null=False,unique=True)
    nacionalidad = models.CharField(max_length=30,null=False)
    TIPO_COMP = (
        ('Casado/a','Casado/a'),
        ('Viudo/a','Viudo/a'),
        ( 'Soltero/a','Soltero/a'),
    )
    estado_civil = models.CharField(max_length=30,null=False,choices=TIPO_COMP)
    num_regex = RegexValidator(regex = r"^\+?1?\d{8,15}$",message="Ingrese un numero de telefono valido.")
    num_tel = models.CharField(validators = [num_regex], max_length = 30, unique = True)
    correo = models.EmailField(max_length=100,null=False,unique=True)
    direccion = models.CharField(max_length=200,null=False)
    #fecha_insercion = models.DateTimeField(auto_now_add=True)
    fecha_insercion = models.DateTimeField(default=timezone.now)
    activo = models.BooleanField(default=True)
    fecha_modificacion = models.DateTimeField(null=True)
    TIPO_DOC = (
        ('RUC','RUC'),
        ( 'CI','CI'),
    )
    tipo_documento = models.CharField(max_length=100, choices=TIPO_DOC)
    #fecha_modificacion = models.DateTimeField(auto_now_add=True)
    
    
    '''def clean(self):
        # Convertir el nombre a mayúsculas para la validación
        nombre_upper = self.nombre.upper()
        apellido_upper = self.apellido.upper()
        if Cliente.objects.filter(nombre__iexact=nombre_upper, apellido__iexact=apellido_upper).exclude(id=self.id).exists():
            raise ValidationError({'nombre': 'Ya existe un cliente con ese nombre y apellido.', 'apellido': 'Ya existe un cliente con ese nombre y apellido.'})'''

    '''def save(self, *args, **kwargs):
        # Convertir el nombre a mayúsculas antes de guardar
        self.nombre = self.nombre.upper()
        self.apellido = self.apellido.upper()
        self.nacionalidad = self.nacionalidad.upper()
        super(Cliente, self).save(*args, **kwargs)'''
        
    def __str__(self):
        return '{}'.format(self.nombre,self.apellido,self.nro_documento,self.fecha_insercion,self.activo)
    
    

class VentaCabecera(models.Model):
    fecha_venta = models.DateTimeField(default=timezone.now)
    nro_comprobante = models.CharField(max_length=100, null=False,unique=True)
    TIPO_COMP = (
        ('boleta','Boleta'),
        ('factura','Factura'),
        ( 'Ticket','Ticket')
    )
    tipo_comprobante = models.CharField(max_length=100, null=False,choices=TIPO_COMP)
    vendedor = models.CharField(max_length=100, null=False)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, default='Pendiente')
    activo = models.BooleanField(default=True)
    TIPO_PAGO = (
        ('EFECTIVO','EFECTIVO'),
        ( 'TRANSFERENCIA','TRANSFERENCIA')
    )
    forma_pago = models.CharField(max_length=100, null=False, choices=TIPO_PAGO)
    iva_diez = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    iva_cinco = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    fecha_insercion = models.DateTimeField(default=timezone.now)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return '{}'.format(self.fecha_venta,self.nro_comprobante,self.tipo_comprobante,self.vendedor,self.total,self.estado,self.cliente,self.activo,self.forma_pago,self.iva_diez,self.iva_cinco,self.descuento)
    
class VentaDetalle(models.Model):
    venta_cab = models.ForeignKey(VentaCabecera, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    #monto_iva_cinco = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    #monto_iva_diez = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    cantidad = models.PositiveIntegerField(null=False)
    descripcion = models.TextField(null=True)
    #categoria = models.CharField(max_length=100, null=True)
    unidad_medida = models.CharField(max_length=100, null=True)
    precio_unit_venta = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_insercion = models.DateTimeField(default=timezone.now)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return '{}'.format(self.venta_cab,self.producto,self.cantidad,self.descripcion,self.subtotal)

    def clean(self):
        validar_stock_venta(self.producto, self.cantidad)
        # Validar que la cantidad sea mayor a cero
    
    
    def save(self, *args, **kwargs):
        
        self.full_clean()  # Llama a clean() para validar el modelo
        # Actualizar cantidad del producto
        #self.producto.cantidad_en_stock -= self.cantidad
        #self.producto.save()
        super(VentaDetalle, self).save(*args, **kwargs)
        
