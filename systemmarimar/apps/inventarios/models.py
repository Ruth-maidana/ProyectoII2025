from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator

from apps.compras.models import Producto,OrdenCompraCab
from apps.ventas.models import VentaCabecera

# Create your models here.


class ConfiguracionStock(models.Model):
    cantidad_maxima = models.IntegerField(default=3)
    descripcion = models.CharField(max_length=255,default='Configuración de stock')
    fecha_configuracion = models.DateTimeField(default=timezone.now)
    frecuencia_notificacion = models.PositiveIntegerField(default=1800)
    
    
    @classmethod
    def get_config(cls):
        """Devuelve la configuración existente o crea una por defecto."""
        return cls.objects.first() or cls.objects.create(
            cantidad_maxima=3,
            descripcion='Configuración de stock',
            frecuencia_notificacion=1800
        )
    
    def __str__(self):
        return '{}'.format(self.cantidad_maxima,self.descripcion,self.fecha_configuracion,self.frecuencia_notificacion)
    
    
    
    
class MovimientoStock(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    TIPO_MOVIMIENTO = (
        ('ENTRADA', 'ENTRADA'),
        ('SALIDA', 'SALIDA'),
    )
    
    TIPO_AJUSTE = (
        ('DEVOLUCION', 'DEVOLUCION'),
        ('PERDIDA', 'PERDIDA'),
        ('DETERIORO', 'DETERIORO'),
        ('VENCIDO', 'VENCIDO'),
        ('EXTRAVIO', 'EXTRAVIO'),
        ('RECLAMO', 'RECLAMO'),
        ('REPOSICION', 'REPOSICION'),
        ('OTRO', 'OTRO'),
    )
    
    ajuste = models.CharField(max_length=10, choices=TIPO_AJUSTE, null=True)
    movimiento = models.CharField(max_length=10, choices=TIPO_MOVIMIENTO)
    cantidad_inicial = models.IntegerField()
    cantidad_actual = models.IntegerField()
    cantidad = models.IntegerField()
    fecha_movimiento = models.DateTimeField(default=timezone.now)
    #fecha_modificacion = models.DateTimeField(default=timezone.now)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    descripcion = models.TextField(null=True, blank=True)
    # Agrega estos campos para mejor trazabilidad
    compra = models.ForeignKey(OrdenCompraCab, on_delete=models.SET_NULL, null=True, blank=True)
    venta = models.ForeignKey(VentaCabecera, on_delete=models.SET_NULL, null=True, blank=True)
    #usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    
    
    def get_icono(self):
        if self.movimiento == 'ENTRADA':
            return '⬆️'  # Icono flecha arriba
        elif self.movimiento == 'SALIDA':
            return '⬇️'  # Icono flecha abajo
        return '🔄'  # Icono para ajustes
    
    
    def get_color(self):
        return {
            'ENTRADA': 'success',
            'SALIDA': 'danger'
        }.get(self.movimiento, 'secondary')
    
    def get_cantidad_formateada(self):
        return f"+{self.cantidad}" if self.movimiento == 'ENTRADA' else f"-{self.cantidad}"
    
        
    def __str__(self):
        return '{}'.format(self.fecha,self.producto,self.cantidad,self.descripcion,self.movimiento,self.ajuste)
    

