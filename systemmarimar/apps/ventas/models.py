from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from apps.compras.models import Producto
from apps.compras.utils import validar_stock_venta


# Create your models here.


class ConfigTimbradoNumeracion(models.Model):
    numero_timbrado = models.CharField(max_length=100, null=False, unique=True)
    fecha_inicio = models.DateField(default=timezone.now)
    fecha_fin = models.DateField(default=timezone.now)
    nro_inicial = models.IntegerField(null=False)
    nro_final = models.IntegerField(null=True)
    nro_actual = models.IntegerField(null=False, default=0)
    
    fecha_insercion = models.DateTimeField(default=timezone.now)
    establecimiento = models.IntegerField(default=1)        # 001
    punto_expedicion = models.IntegerField(default=1)
    
    
    def obtener_timbrado(self):
        return self.numero_timbrado
    
    def obtener_numeracion_formateada(self):
        if self.nro_actual == 0:
            self.nro_actual = self.nro_inicial
            return f"{self.establecimiento:03d}-{self.punto_expedicion:03d}-{self.nro_actual:08d}"
        else:
            return f"{self.establecimiento:03d}-{self.punto_expedicion:03d}-{self.nro_actual:08d}"
    
    '''def obtener_siguiente_numero(self):
        siguiente = self.nro_actual + 1
        if self.nro_final and siguiente > self.nro_final:
            raise ValueError("Se alcanzó el número final del timbrado.")
        return f"{siguiente:03d}-{1:03d}-{1:03d}"  # Personaliza si los otros bloques cambian'''
    
    def incrementar_numeracion(self):
        if self.nro_final and self.nro_actual + 1 > self.nro_final:
            raise ValueError("No se puede incrementar, se alcanzó el número final.")
        self.nro_actual += 1
        self.save()


    
    def __str__(self):
        return '{}'.format(self.numero_timbrado,self.fecha_inicio,self.fecha_fin,self.nro_inicial,self.nro_final,self.nro_actual)
    

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
    CONDICION_VENTA_CHOICES = (
        ('contado','Contado'),
        ('credito','Credito')
    )
    condicion_venta = models.CharField(max_length=100, null=False,choices=CONDICION_VENTA_CHOICES)
    timbrado = models.CharField(max_length=100, null=False)
    nota_remision = models.CharField(max_length=100, null=True)
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
        return '{}'.format(self.fecha_venta,self.nro_comprobante,self.condicion_venta,self.vendedor,self.total,self.estado,self.cliente,self.activo,self.forma_pago,self.iva_diez,self.iva_cinco,self.descuento)
    
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
    
    

    '''def clean(self):
        validar_stock_venta(self.producto, self.cantidad)'''
        # Validar que la cantidad sea mayor a cero
    
    
    def save(self, *args, **kwargs):
        
        self.full_clean()  # Llama a clean() para validar el modelo
        # Actualizar cantidad del producto
        #self.producto.cantidad_en_stock -= self.cantidad
        #self.producto.save()
        super(VentaDetalle, self).save(*args, **kwargs)
        
    def __str__(self):
        return '{}'.format(self.venta_cab,self.producto,self.cantidad,self.descripcion,self.subtotal)
        

class Empresa(models.Model):
    nombre = models.CharField(max_length=100, null=False)
    ruc = models.CharField(max_length=20, null=False, unique=True)
    direccion = models.CharField(max_length=200, null=False)
    descripcion = models.TextField(null=True, blank=True)
    ramo_actividad = models.CharField(max_length=100, null=False)
    telefono = models.CharField(max_length=15, null=False)
    email = models.EmailField(max_length=100, null=False)
    fecha_insercion = models.DateTimeField(default=timezone.now)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    def __str__(self):
       return '{}'.format(self.nombre,self.ruc,self.direccion,self.descripcion,self.ramo_actividad,self.telefono,self.email,self.fecha_insercion,self.fecha_modificacion)
    
    def clean(self):
        if Empresa.objects.filter(ruc=self.ruc).exclude(id=self.id).exists():
            raise ValidationError({'ruc': 'Ya existe una empresa con ese RUC.'})