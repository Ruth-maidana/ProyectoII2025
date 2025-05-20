from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, JsonResponse
from django.views import View

from apps.inventarios.forms import AjusteStockForm, ConfiguracionStockForm
from apps.compras.models import Categoria, Producto
from apps.ventas.models import VentaDetalle
from .models import ConfiguracionStock, MovimientoStock
from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .utils import productos_stock_bajo, registrar_movimiento_stock
from django.utils import timezone
from django.db import transaction 
from datetime import datetime, timedelta
# Create your views here.

    
def listar_movimientos(request):
    movimientos = MovimientoStock.objects.all()
    if request.method == 'POST':
        ajustar_stock = AjusteStockForm(request.POST)
        if ajustar_stock.is_valid():
            try:
                with transaction.atomic():
                    ajuste = ajustar_stock.cleaned_data['ajuste']
                    cantidad = ajustar_stock.cleaned_data['cantidad']
                    producto = ajustar_stock.cleaned_data['producto']
                    descripcion = ajustar_stock.cleaned_data['descripcion']
                    movimiento = ajustar_stock.cleaned_data['movimiento']
                    
                    registrar_movimiento_stock(
                        producto=producto,
                        cantidad=cantidad,
                        movimiento=movimiento,
                        descripcion=descripcion,
                        ajuste=ajuste,
                        fecha_mov_producto=None,  # Aquí puedes agregar la fecha si es necesario
                        compra_cab=None,  # Aquí puedes agregar la compra si es necesario
                        venta_cab=None   # Aquí puedes agregar la venta si es necesario
                    )
                
                    messages.success(request, 'Ajuste de stock registrado correctamente.')
            except Exception as e:
                messages.error(request, f'Error al registrar el ajuste: {str(e)}')
                print('Error al registrar el ajuste:', e)
                #return HttpResponse('Error al registrar el ajuste')
        else:   
            print(ajustar_stock.errors)
            print('Error en el formulario')
            print(ajustar_stock.cleaned_data)
            messages.error(request, '¡Hubo un error al registrar el ajuste!')
    else:
        ajustar_stock = AjusteStockForm()
    
    context = {
        'Movimientos': movimientos,
       'form_ajustar_stock': ajustar_stock,
    }
    
    return render(request, 'stock/listar2.html', context)

def listar_movimientos_version_act(request):
    movimientos = MovimientoStock.objects.all()
    
    categoria_id = request.GET.get('categoria')
    producto_id = request.GET.get('producto')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    nivel_stock = request.GET.get('nivel_stock')
    
    
    
    # Filtrar por categoría si se proporciona
    if categoria_id:
        movimientos = movimientos.filter(producto__categoria__id=categoria_id)
    
    # Filtrar por producto si se proporciona
    if producto_id:
        movimientos = movimientos.filter(producto__id=producto_id)
        
    # Filtrar por rango de fechas si se proporciona
    if fecha_inicio and fecha_fin:
        try:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
            # Ajusta la fecha fin para incluir todo el día
            fecha_fin = fecha_fin.replace(hour=23, minute=59, second=59)
            movimientos = movimientos.filter(fecha__range=[fecha_inicio, fecha_fin])
        except ValueError:
            messages.error(request, 'Formato de fecha inválido. Usa YYYY-MM-DD.')
    
    
    # Filtrar por nivel de stock
    '''if nivel_stock:
        try:
            config_stock = ConfiguracionStock.objects.latest('fecha_configuracion')
            if nivel_stock == 'bajo':
                movimientos = movimientos.filter(
                    cantidad_actual__lt=config_stock.cantidad_maxima
                )
            elif nivel_stock == 'suficiente':
                movimientos = movimientos.filter(
                    cantidad_actual__gte=config_stock.cantidad_maxima
                )
        except ConfiguracionStock.DoesNotExist:
            messages.error(request, 'No se encontró configuración de stock.')'''
    
    # Obtener categorías para el formulario
    categorias = Categoria.objects.all()
    productos = Producto.objects.all()


    context = {
        'Movimientos': movimientos, 
        'categorias': categorias,
        'productos': productos,
        'categoria_seleccionada': int(categoria_id) if categoria_id else None,
        'producto_seleccionado': int(producto_id) if producto_id else None,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'nivel_stock_seleccionado': nivel_stock,
    }
    
    return render(request, 'stock/listar3.html', context)

def ajustar_stock(request):
    if request.method == 'POST':
        ajustar_stock = AjusteStockForm(request.POST)
        if ajustar_stock.is_valid():
            try:
                with transaction.atomic():
                    ajuste = ajustar_stock.cleaned_data['ajuste']
                    cantidad = ajustar_stock.cleaned_data['cantidad']
                    producto = ajustar_stock.cleaned_data['producto']
                    descripcion = ajustar_stock.cleaned_data['descripcion']
                    movimiento = ajustar_stock.cleaned_data['movimiento']
                    
                    registrar_movimiento_stock(
                        producto=producto,
                        cantidad=cantidad,
                        movimiento=movimiento,
                        descripcion=descripcion,
                        ajuste=ajuste,
                        fecha_mov_producto=None,  # Aquí puedes agregar la fecha si es necesario
                        compra_cab=None,  # Aquí puedes agregar la compra si es necesario
                        venta_cab=None   # Aquí puedes agregar la venta si es necesario
                    )
                
                    messages.success(request, 'Ajuste de stock registrado correctamente.')
            except Exception as e:
                messages.error(request, f'Error al registrar el ajuste: {str(e)}')
                print('Error al registrar el ajuste:', e)
                #return HttpResponse('Error al registrar el ajuste')
        else:   
            print(ajustar_stock.errors)
            print('Error en el formulario')
            print(ajustar_stock.cleaned_data)
            messages.error(request, '¡Hubo un error al registrar el ajuste!')
    else:
        ajustar_stock = AjusteStockForm()
    
    context = {
       'form_ajustar_stock': ajustar_stock,
    }
    
    return render(request, 'stock/ajustar.html', context)




'''
def filtrar_movimiento_stock(request):
    # Filtrar por fecha si se proporciona
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    if fecha_inicio and fecha_fin:
        movimientos = movimientos.filter(fecha_movimiento__range=[fecha_inicio, fecha_fin])
    # Filtrar por producto si se proporciona
    producto_id = request.GET.get('producto')
    if producto_id:
        movimientos = movimientos.filter(producto__id=producto_id)
    # Filtrar por tipo de movimiento si se proporciona
    tipo_movimiento = request.GET.get('tipo_movimiento')
    if tipo_movimiento:
        movimientos = movimientos.filter(tipo=tipo_movimiento)
    # Filtrar por ajuste si se proporciona
    ajuste = request.GET.get('ajuste')
    if ajuste:
        movimientos = movimientos.filter(ajuste=ajuste)
    # Filtrar por usuario si se proporciona
    usuario_id = request.GET.get('usuario')
    if usuario_id:
        movimientos = movimientos.filter(usuario__id=usuario_id)
    # Filtrar por compra si se proporciona
    compra_id = request.GET.get('compra')
    if compra_id:
        movimientos = movimientos.filter(compra__id=compra_id)
    # Filtrar por venta si se proporciona
    venta_id = request.GET.get('venta')
    if venta_id:
        movimientos = movimientos.filter(venta__id=venta_id)
    # Filtrar por fecha de movimiento si se proporciona
    fecha_movimiento = request.GET.get('fecha_movimiento')
    if fecha_movimiento:
        movimientos = movimientos.filter(fecha_movimiento=fecha_movimiento)
    # Filtrar por cantidad si se proporciona
    cantidad = request.GET.get('cantidad')
    if cantidad:
        movimientos = movimientos.filter(cantidad=cantidad)
    # Filtrar por cantidad inicial si se proporciona
    cantidad_inicial = request.GET.get('cantidad_inicial')
    if cantidad_inicial:
        movimientos = movimientos.filter(cantidad_inicial=cantidad_inicial)
    # Filtrar por cantidad actual si se proporciona
    cantidad_actual = request.GET.get('cantidad_actual')
    if cantidad_actual:
        movimientos = movimientos.filter(cantidad_actual=cantidad_actual)
    # Filtrar por descripción si se proporciona
    descripcion = request.GET.get('descripcion')
    if descripcion:
        movimientos = movimientos.filter(descripcion__icontains=descripcion)
    # Filtrar por fecha de creación si se proporciona
    fecha_creacion = request.GET.get('fecha_creacion')
    if fecha_creacion:
        movimientos = movimientos.filter(fecha__date=fecha_creacion)
    # Filtrar por fecha de modificación si se proporciona
    fecha_modificacion = request.GET.get('fecha_modificacion')
    if fecha_modificacion:
        movimientos = movimientos.filter(fecha__date=fecha_modificacion)
    # Filtrar por fecha de ajuste si se proporciona
    fecha_ajuste = request.GET.get('fecha_ajuste')
    if fecha_ajuste:
        movimientos = movimientos.filter(fecha__date=fecha_ajuste)
    # Filtrar por fecha de entrada si se proporciona
    fecha_entrada = request.GET.get('fecha_entrada')
    if fecha_entrada:
        movimientos = movimientos.filter(fecha__date=fecha_entrada)
    # Filtrar por fecha de salida si se proporciona
    fecha_salida = request.GET.get('fecha_salida')
    if fecha_salida:
        movimientos = movimientos.filter(fecha__date=fecha_salida)
    # Filtrar por fecha de ajuste si se proporciona
    fecha_ajuste = request.GET.get('fecha_ajuste')
    if fecha_ajuste:
        movimientos = movimientos.filter(fecha__date=fecha_ajuste)          
    return render(request, 'stock/listar2.html', {'Movimientos': movimientos})'''

def configurar_stock(request):
    config = get_object_or_404(ConfiguracionStock)
    if request.method == 'POST':
        form_config_notificacion = ConfiguracionStockForm(request.POST)
        if form_config_notificacion.is_valid():
            form_config_notificacion.save()
            messages.success(request, 'Configuración de stock guardada correctamente.')
        else:
            messages.error(request, 'Error al guardar la configuración de stock.')
    else:
        form_config_notificacion = ConfiguracionStockForm(instance=config)
        
    return render(request, 'stock/configurar_notificacion.html', {'form_config_notificacion': form_config_notificacion})

def alerta_stock_bajo(request):
    producto_stock_bajo_notificar = productos_stock_bajo()
    config_stock = ConfiguracionStock.objects.first()
    if producto_stock_bajo_notificar:
        for producto in producto_stock_bajo_notificar:
            mensaje = f'{config_stock.descripcion}. El producto {producto.nombre} tiene un stock bajo: {producto.cantidad_en_stock} unidades.'
            messages.warning(request, mensaje)

def stock_actual(producto):
    entradas = MovimientoStock.objects.filter(producto=producto, tipo='entrada').aggregate(total=Sum('cantidad'))['total'] or 0
    salidas = MovimientoStock.objects.filter(producto=producto, tipo='salida').aggregate(total=Sum('cantidad'))['total'] or 0
    return entradas - salidas


def pantalla_stock(request):
    productos_bajos = productos_stock_bajo()
    alerta = len(productos_bajos) > 0
    mensaje = ''
    if alerta:
        productos = ', '.join([p[0].nombre for p in productos_bajos])
        mensaje = f"¡Atención! Productos con stock bajo: {productos}"
    return render(request, 'stock/alerta.html', {
        'productos_bajos': productos_bajos,
        'alerta': alerta,
        'mensaje_alerta': mensaje,
    })


def api_stock_bajo(request):
    config = ConfiguracionStock.get_config()
    productos_bajos = Producto.objects.filter(
        cantidad_en_stock__lte=config.cantidad_maxima
    ).values('id', 'nombre', 'cantidad_en_stock')
    print('productos_bajos', productos_bajos)
    return JsonResponse({
        'productos': list(productos_bajos),
        'mensaje': config.descripcion,
        'frecuencia': config.frecuencia_notificacion
    })