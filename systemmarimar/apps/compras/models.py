from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from apps.compras.utils import validar_stock_compra


# Create your models here.


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, null=False,unique=True)
    descripcion = models.TextField(null=True, blank=True)
    fecha_insercion = models.DateTimeField(default=timezone.now)
    activo = models.BooleanField(default=True)
    
    def clean(self):
        # Convertir el nombre a mayúsculas para la validación
        nombre_upper = self.nombre.upper()
        if Categoria.objects.filter(nombre__iexact=nombre_upper).exclude(id=self.id).exists():
            raise ValidationError({'nombre': 'Ya existe una categoría con este nombre.'})

    def save(self, *args, **kwargs):
        
        
        # Convertir el nombre a mayúsculas antes de guardar
        self.nombre = self.nombre.upper()
        
        self.full_clean()  # Llama a clean() para validar el modelo
        
        super(Categoria, self).save(*args, **kwargs)
    
    
    def __str__(self):
        return '{}'.format(self.nombre,self.descripcion,self.fecha_insercion,self.activo)

class Proveedor(models.Model):
    razon_social = models.CharField(max_length=50,unique=True, null=False)
    nro_documento = models.CharField(max_length=30, null=False, unique=True)
    direccion = models.CharField(max_length=100, null=True,blank=True)
    num_regex = RegexValidator(regex = r"^\+?1?\d{8,15}$",message="Ingrese un numero de telefono valido.")
    num_tel = models.CharField(validators = [num_regex], max_length = 16, unique = True)
    correo = models.EmailField(max_length=30, null=False, unique=True)
    fecha_insercion = models.DateTimeField(default=timezone.now)  
    descripcion = models.CharField(max_length=30)
    TIPO_DOC = (
        ('RUC','RUC'),
        ( 'CI','CI'),
    )
    tipo_documento = models.CharField(max_length=100, choices=TIPO_DOC)
    activo = models.BooleanField(default=True)
    
    
    def clean(self):
        # Convertir el nombre a mayúsculas para la validación
        razon_social_upper = self.razon_social.upper()
        if Proveedor.objects.filter(razon_social__iexact=razon_social_upper).exclude(id=self.id).exists():
            raise ValidationError({'razon_social': 'Ya existe un proveedor con este nombre.'})
    
    def save(self, *args, **kwargs):
        
        # Convertir el nombre a mayúsculas antes de guardar
        self.razon_social = self.razon_social.upper()
        
        self.full_clean()  # Llama a clean() para validar el modelo
        
        super(Proveedor, self).save(*args, **kwargs)

    def __str__(self):
        return'{}'.format(self.razon_social,self.nro_documento,self.num_tel,self.direccion,self.correo,self.descripcion,self.tipo_documento,self.activo)


class Producto(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100, null=False,unique=True)
    descripcion = models.TextField(null=True, blank=True)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    iva = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    cantidad_en_stock = models.IntegerField(null=False)#cantidad actual en stock
    fecha_insercion = models.DateTimeField(default=timezone.now)
    activo = models.BooleanField(default=True)
    UNIDAD = (
        ('METROS','METROS'),
        ( 'UNIDADES','UNIDADES'),
        ('KILOGRAMOS','KILOGRAMOS'),
        ('LITROS','LITROS'),
        ('CAJAS','CAJAS'),
        ('PAQUETES','PAQUETES')
    )
    unidad_medida = models.CharField(max_length=100, null=False,choices=UNIDAD)
    
    
    def clean(self):
        # Convertir el nombre a mayúsculas para la validación
        nombre_upper = self.nombre.upper()
        if Producto.objects.filter(nombre__iexact=nombre_upper).exclude(id=self.id).exists():
            raise ValidationError({'nombre': 'Ya existe un producto con este nombre.'})
        
        # Validar el stock antes de guardar
        validar_stock_compra(self, self.cantidad_en_stock)
    
    @property 
    def total_inventario(self):
        return self.precio_venta * self.cantidad_en_stock
    
    
    def save(self, *args, **kwargs):
        
        # Convertir el nombre a mayúsculas antes de guardar
        self.nombre = self.nombre.upper()
        self.full_clean()  # Llama a clean() para validar el modelo
        super(Producto, self).save(*args, **kwargs)

    def __str__(self):
        return '{}'.format(self.nombre,self.iva,self.descripcion,self.precio_compra,self.cantidad_en_stock,self.fecha_insercion,self.activo,self.categoria,self.proveedor)
 
class OrdenCompraCab(models.Model):
    nro_comprobante = models.CharField(max_length=100, null=False,unique=True)
    fecha_compra = models.DateTimeField(default=timezone.now)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    activo = models.BooleanField(default=True)
    total= models.DecimalField(max_digits=10, decimal_places=2, null=False)
    TIPO_PAGO = (
        ('EFECTIVO','EFECTIVO'),
        ( 'TRANSFERENCIA','TRANSFERENCIA')
    )
    forma_pago = models.CharField(max_length=100, null=False, choices=TIPO_PAGO)
    fecha_insercion = models.DateTimeField(default=timezone.now) 
    descuento = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    iva_diez = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    iva_cinco = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    def __str__(self):
        return '{}'.format(self.nro_comprobante,self.fecha_compra,self.proveedor,self.total)
    
    
class OrdenCompraDet(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    descripcion = models.TextField(null=True, blank=True)
    cantidad = models.IntegerField(null=False)
    UNIDAD = (
        ('METROS','METROS'),
        ( 'UNIDADES','UNIDADES'),
        ('KILOGRAMOS','KILOGRAMOS'),
        ('LITROS','LITROS'),
        ('CAJAS','CAJAS'),
        ('PAQUETES','PAQUETES')
    )
    unidad_medida = models.CharField(max_length=100, null=False,choices=UNIDAD)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    #descuento = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    total_producto = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    orden_compra_cab = models.ForeignKey(OrdenCompraCab, on_delete=models.CASCADE)
    fecha_insercion = models.DateTimeField(default=timezone.now) 
    
    def clean(self):
        validar_stock_compra(self.producto, self.cantidad)
        
    def save(self, *args, **kwargs):
        # Actualizar cantidad del producto
        #self.producto.cantidad_en_stock += self.cantidad
        self.full_clean()
        #self.producto.save()
        super(OrdenCompraDet, self).save(*args, **kwargs)
        
    def __str__(self):
        return '{}'.format(self.producto,self.cantidad,self.precio_compra)
    
