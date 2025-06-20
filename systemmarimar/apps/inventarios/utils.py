from apps.compras.models import Producto
from .models import ConfiguracionStock, MovimientoStock
from django.utils import timezone

'''def registrar_movimiento_stock(producto, cantidad, movimiento='ENTRADA', descripcion='', ajuste=None,fecha_mov_producto=None, compra_cab=None,venta_cab=None):
    """
    Registra un movimiento de stock para un producto
    Args:
        producto: Instancia de Producto
        cantidad: Cantidad del movimiento (positiva)
        movimiento: 'ENTRADA'|'SALIDA'|'AJUSTE'
        descripcion: Texto descriptivo
        ajuste: Solo si movimiento='AJUSTE'
    """
    MovimientoStock.objects.create(
        producto=producto,
        cantidad=cantidad,
        cantidad_inicial=producto.cantidad_en_stock,
        cantidad_actual=producto.cantidad_en_stock + (cantidad if movimiento == 'ENTRADA' else -cantidad),
        movimiento=movimiento,
        ajuste=ajuste,
        descripcion=descripcion,
        fecha_movimiento=fecha_mov_producto or timezone.now(),
        compra=compra_cab,
        venta=venta_cab
        #usuario=usuario
    )
    # Actualiza el stock del producto
    if movimiento == 'ENTRADA':
        producto.cantidad_en_stock += cantidad
    else:
        producto.cantidad_en_stock -= cantidad
    producto.save()'''
    
    
    
def registrar_movimiento_stock(producto, cantidad, movimiento='ENTRADA', descripcion='', ajuste=None, fecha_mov_producto=None, compra_cab=None, venta_cab=None):
    """
    Registra un movimiento de stock para un producto
    Args:
        producto: Instancia de Producto
        cantidad: Cantidad del movimiento (siempre positiva)
        movimiento: 'ENTRADA'|'SALIDA'|'AJUSTE'|'REVERSO'
        descripcion: Texto descriptivo
        ajuste: Solo si movimiento='AJUSTE'
    """
    # Determinar el efecto en el stock según el tipo de movimiento
    if movimiento in 'ENTRADA':
        efecto = cantidad
        cantidad_actual = producto.cantidad_en_stock + cantidad
        cantidad_original = producto.cantidad_en_stock
        
    elif movimiento == 'REV_SAL':
        print('Movimiento de reverso de salida')
        efecto = cantidad
        print(f'Efecto: {efecto}')
        cantidad_actual = producto.cantidad_en_stock + cantidad
        print(f'Cantidad actual: {cantidad_actual}')
        cantidad_original = cantidad_actual
        print(f'Cantidad original: {cantidad_original}')
        
    elif movimiento == 'REV_ENT':
        efecto = -cantidad
        cantidad_actual = producto.cantidad_en_stock - cantidad
        cantidad_original = cantidad_actual
        
    elif movimiento in 'SALIDA':
        efecto = -cantidad
        cantidad_actual = producto.cantidad_en_stock - cantidad
        cantidad_original = producto.cantidad_en_stock
        
    else:  # AJUSTE
        efecto = cantidad - producto.cantidad_en_stock
        cantidad_actual = cantidad
        cantidad_original = producto.cantidad_en_stock

    # Crear el registro de movimiento
    MovimientoStock.objects.create(
        producto=producto,
        cantidad=cantidad,
        cantidad_inicial=cantidad_original,
        cantidad_actual=cantidad_actual,
        movimiento=movimiento,
        ajuste=ajuste,
        descripcion=descripcion,
        fecha_movimiento=fecha_mov_producto or timezone.now(),
        compra=compra_cab,
        venta=venta_cab
    )

    # Actualizar el stock del producto
    producto.cantidad_en_stock = cantidad_actual
    producto.save()

def productos_stock_bajo(producto):
    productos= Producto.objects.all()
    config_stock = ConfiguracionStock.objects.first()
    productos_bajos = []
    for producto in productos:
        if producto.cantidad_en_stock <= config_stock.cantidad_maxima:
            productos_bajos.append(producto)
            
    return productos_bajos
    
    '''if producto.cantidad_en_stock <= config_stock.cantidad_maxima:
        mensaje = f'{config_stock.descripcion}. El producto {producto.nombre} tiene un stock bajo: {producto.cantidad_en_stock} unidades.'
        return mensaje'''

    
'''def estado_stock(self):
    if self.producto.cantidad_en_stock < ConfiguracionStock.cantidad_maxima:
        return 'Bajo'
    elif self.producto.cantidad_en_stock > ConfiguracionStock.cantidad_maxima:
        return 'Alto'
    else:
        return 'Normal'''
    
    