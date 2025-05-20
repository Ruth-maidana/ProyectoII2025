from django.core.exceptions import ValidationError




def validar_stock_venta(producto, cantidad):
    
    if cantidad is None:
        raise ValidationError(f'La cantidad es invalido {producto.nombre}.')
    
    if cantidad < 0:
        raise ValidationError(f'La cantidad debe ser mayor a cero para el producto {producto.nombre}.')
    
    if cantidad == 0:
        raise ValidationError(f'La cantidad no puede ser cero para el producto {producto.nombre}.')
    
    if not isinstance(cantidad, int):
        raise ValidationError(f'La cantidad debe ser un número entero para el producto {producto.nombre}.')

    if producto.cantidad_en_stock < cantidad:
        raise ValidationError(f'No hay suficiente stock para el producto {producto.nombre}. Stock disponible: {producto.cantidad_en_stock}')
    return True


def validar_stock_compra(producto, cantidad):
    
    if cantidad is None:
        raise ValidationError(f'La cantidad es invalido {producto.nombre}.')
    
    if cantidad < 0:
        raise ValidationError(f'La cantidad debe ser mayor a cero para el producto {producto.nombre}.')
    
    if cantidad == 0:
        raise ValidationError(f'La cantidad no puede ser cero para el producto {producto.nombre}.')
    
    
    if not isinstance(cantidad, int):
        raise ValidationError(f'La cantidad debe ser un número entero para el producto {producto.nombre}.')