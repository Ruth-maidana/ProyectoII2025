
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from apps.compras.utils import validar_stock_compra
import logging
logger = logging.getLogger(__name__)

# Create your models here.


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, null=False,unique=True)
    descripcion = models.TextField(blank=True)
    fecha_insercion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    
    def clean(self):
        """
        Validación personalizada del modelo.
        Previene la desactivación de categorías con productos asignados.
        """
        super().clean()  # Llama al método clean del modelo base
        
        # Convertir el nombre a mayúsculas para la validación
        nombre_upper = self.nombre.upper()
        if Categoria.objects.filter(nombre__iexact=nombre_upper).exclude(id=self.id).exists():
            raise ValidationError({'nombre': 'Ya existe una categoría con este nombre.'})
        
        if not self.activo and self.pk: 
            productos_activos = self.producto_set.filter(activo=True)
            productos_count = productos_activos.count()
            if productos_count > 0:
                raise ValidationError("No se puede desactivar: tiene productos asignados")

    def save(self, *args, **kwargs):
        # Convertir el nombre a mayúsculas antes de guardar
        self.nombre = self.nombre.upper()
        
        """Override del método save para ejecutar validaciones."""
        self.full_clean() 
        super(Categoria, self).save(*args, **kwargs)
    
    
    def __str__(self):
        return '{}'.format(self.nombre,self.descripcion,self.fecha_insercion)

class Proveedor(models.Model):
    razon_social = models.CharField(max_length=50,unique=True, null=False)
    representante = models.CharField(max_length=50, blank=True)
    nro_documento = models.CharField(max_length=30, null=False, unique=True)
    direccion = models.CharField(max_length=100, null=True,blank=True)
    CODIGOS_NUM_PAIS = (
        ('+595', 'Paraguay (+595)'),
        ('+54', 'Argentina (+54)'),
        ('+55', 'Brasil (+55)'),
        ('+1', 'Estados Unidos/Canadá (+1)'),
        ('+34', 'España (+34)'),
        ('+49', 'Alemania (+49)'),
        ('+33', 'Francia (+33)'),
        ('+39', 'Italia (+39)'),
        ('+81', 'Japón (+81)'),
        ('+86', 'China (+86)'),
        ('+91', 'India (+91)'),
        ('+52', 'México (+52)'),
        ('+56', 'Chile (+56)'),
        ('+57', 'Colombia (+57)'),
        ('+58', 'Venezuela (+58)'),
        ('+51', 'Perú (+51)'),
        ('+598', 'Uruguay (+598)'),
        ('+591', 'Bolivia (+591)'),
    )
    
    codigo_pais = models.CharField(
        max_length=5, 
        choices=CODIGOS_NUM_PAIS, 
        default='+595',
        help_text="Código de país para el teléfono"
    )
    
    # Validador básico (ya suficiente para la mayoría de casos)
    num_regex = RegexValidator(
        regex=r"^\d{6,12}$",
        message="Ingrese solo números, entre 6 y 12 dígitos."
    )
    
    num_tel = models.CharField(
        validators=[num_regex], 
        max_length=15,
        help_text="Número de teléfono sin código de país"
    )
    
    correo = models.EmailField(max_length=30, null=False, unique=True)
    fecha_insercion = models.DateTimeField(auto_now_add=True)
    descripcion = models.CharField(max_length=100, null=True,blank=True)
    TIPO_DOC = (
        ('RUC','RUC'),
        ( 'CI','CI'),
    )
    tipo_documento = models.CharField(max_length=100, choices=TIPO_DOC)
    activo = models.BooleanField(default=True)
    
    class Meta:
        # Combinación única de código de país + número
        unique_together = [['codigo_pais', 'num_tel']]
    
    def clean(self):
        
        """Validaciones BÁSICAS - suficientes para empezar"""
        super().clean()
        
        # Solo validaciones esenciales
        if self.codigo_pais == '+595':  # Paraguay
            if len(self.num_tel) < 8:
                raise ValidationError({
                    'num_tel': 'Para Paraguay, mínimo 8 dígitos.'
                })
        elif self.codigo_pais == '+1':  # USA/Canadá
            if len(self.num_tel) != 10:
                raise ValidationError({
                    'num_tel': 'Para USA/Canadá, exactamente 10 dígitos.'
                })
        elif self.codigo_pais in ['+54', '+55', '+56', '+57']:  # Latinoamérica
            if len(self.num_tel) < 8 or len(self.num_tel) > 11:
                raise ValidationError({
                    'num_tel': 'Entre 8 y 11 dígitos para este país.'
                })
                
        # Convertir el nombre a mayúsculas para la validación
        razon_social_upper = self.razon_social.upper()
        if Proveedor.objects.filter(razon_social__iexact=razon_social_upper).exclude(id=self.id).exists():
            raise ValidationError({'razon_social': 'Ya existe un proveedor con este nombre.'})
        
       
    @property
    def telefono_completo(self):
        return f"{self.codigo_pais} {self.num_tel}"
    
    
    
    def save(self, *args, **kwargs):
        
        # Convertir el nombre a mayúsculas antes de guardar
        self.razon_social = self.razon_social.upper()
        
        self.full_clean()  # Llama a clean() para validar el modelo
        
        super(Proveedor, self).save(*args, **kwargs)

    def __str__(self):
        return'{}'.format(self.razon_social,self.nro_documento,self.telefono_completo,self.descripcion,self.tipo_documento)


class Producto(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100, null=False,unique=True)
    descripcion = models.TextField(null=True, blank=True)
    precio_compra = models.DecimalField(max_digits=100, decimal_places=2, null=False)
    precio_venta = models.DecimalField(max_digits=100, decimal_places=2, null=False)
    iva_selected = (
        (10,10),
        (5,5)
    )
    iva = models.IntegerField(null=False, choices=iva_selected, default='10')
    cantidad_en_stock = models.IntegerField(null=False)#cantidad actual en stock
    fecha_insercion = models.DateTimeField(auto_now_add=True)
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
    total= models.DecimalField(max_digits=100, decimal_places=2, null=False)
    TIPO_PAGO = (
        ('EFECTIVO','EFECTIVO'),
        ( 'TRANSFERENCIA','TRANSFERENCIA')
    )
    forma_pago = models.CharField(max_length=100, null=False, choices=TIPO_PAGO)
    fecha_insercion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
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
    precio_compra = models.DecimalField(max_digits=100, decimal_places=2, null=False)
    total_producto = models.DecimalField(max_digits=100, decimal_places=2, null=False)
    orden_compra_cab = models.ForeignKey(OrdenCompraCab, on_delete=models.CASCADE)
    fecha_insercion = models.DateTimeField(auto_now_add=True) 
    activo = models.BooleanField(default=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    '''def clean(self):
        validar_stock_compra(self.producto, self.cantidad)'''
        
    def save(self, *args, **kwargs):
        # Actualizar cantidad del producto
        #self.producto.cantidad_en_stock += self.cantidad
        self.full_clean()
        #self.producto.save()
        super(OrdenCompraDet, self).save(*args, **kwargs)
        
    def __str__(self):
        return '{}'.format(self.producto,self.cantidad,self.precio_compra)
    
