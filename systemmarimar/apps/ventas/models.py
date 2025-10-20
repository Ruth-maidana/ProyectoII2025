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

    CODIGOS_PAIS = (
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
        choices=CODIGOS_PAIS, 
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
    correo = models.EmailField(max_length=100,null=False,unique=True)
    direccion = models.CharField(max_length=200,null=False)
    fecha_insercion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    TIPO_DOC = (
        ('RUC','RUC'),
        ( 'CI','CI'),
    )
    tipo_documento = models.CharField(max_length=100, choices=TIPO_DOC)
    
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
    
    @property
    def telefono_completo(self):
        return f"{self.codigo_pais} {self.num_tel}"
        
    def __str__(self):
        return '{}'.format(self.nombre,self.apellido,self.nro_documento,self.fecha_insercion,self.activo)
    
    

class VentaCabecera(models.Model):
    fecha_venta = models.DateTimeField(default=timezone.now)
    nro_comprobante = models.CharField(max_length=100, null=False,unique=True)
    condicion_venta = models.CharField(max_length=100, null=False)
    timbrado = models.CharField(max_length=100, null=False)
    nota_remision = models.CharField(max_length=100, null=True)
    vendedor = models.CharField(max_length=100, null=False)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)
    TIPO_PAGO = (
        ('EFECTIVO','EFECTIVO'),
        ( 'TRANSFERENCIA','TRANSFERENCIA')
    )
    forma_pago = models.CharField(max_length=100, null=False, choices=TIPO_PAGO)
    iva_diez = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    iva_cinco = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    fecha_insercion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return '{}'.format(self.fecha_venta,self.nro_comprobante,self.condicion_venta,self.vendedor,self.total,self.cliente,self.activo,self.forma_pago,self.iva_diez,self.iva_cinco,self.descuento)
    
class VentaDetalle(models.Model):
    venta_cab = models.ForeignKey(VentaCabecera, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(null=False)
    descripcion = models.TextField(null=True)
    unidad_medida = models.CharField(max_length=100, null=True)
    precio_unit_venta = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_insercion = models.DateTimeField(default=timezone.now)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    
    
    
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