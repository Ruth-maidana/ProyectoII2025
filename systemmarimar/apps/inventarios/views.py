from itertools import count
import logging
from django.shortcuts import get_object_or_404, render,redirect
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.template.loader import render_to_string, get_template
from weasyprint import HTML, CSS
from io import BytesIO
from xhtml2pdf import pisa
import matplotlib.pyplot as plt
from django.db.models.functions import Coalesce, Round
import base64
import plotly.graph_objects as go
from django.utils.safestring import mark_safe
from apps.inventarios.forms import AjusteStockForm, ConfiguracionStockForm
from apps.compras.models import Categoria, Producto, Proveedor
from apps.ventas.models import VentaDetalle
from django.db.models import Sum,F, Q, Count, DecimalField, IntegerField, Case, When, Value,OuterRef, Subquery, Exists, ExpressionWrapper, FloatField, Max
from .models import ConfiguracionStock, MovimientoStock
from django.db.models import Sum, FloatField
from django.contrib import messages
from django.utils.decorators import method_decorator
from .utils import productos_stock_bajo, registrar_movimiento_stock
from django.utils import timezone
from django.db import transaction,models
from random import randint
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required,permission_required
from django.utils.safestring import mark_safe
import json
# Create your views here.

logger = logging.getLogger(__name__)

#@login_required(login_url='login/')
#@permission_required('inventarios.view_movimientostock', raise_exception=True)
def listar_movimientos(request):
    movimientos = MovimientoStock.objects.all().order_by('fecha_movimiento')
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


@login_required(login_url='login/')
@permission_required('inventarios.view_movimientostock', raise_exception=True)
def listar_movimientos_version_act(request):
    movimientos = MovimientoStock.objects.all().order_by('-fecha_movimiento')  # Ordenar por fecha del movimiento
    
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
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            
            # CORRECCIÓN: Usar fecha_movimiento en lugar de fecha
            movimientos = movimientos.filter(
                fecha_movimiento__range=[fecha_inicio_dt, fecha_fin_dt]
            )
            
            logger.debug(f"Filtrando movimientos por fecha_movimiento entre {fecha_inicio_dt} y {fecha_fin_dt}")
            
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


'''def listar_movimientos_version_act(request):
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
    
    return render(request, 'stock/listar3.html', context)'''

@login_required(login_url='login/')
@permission_required('inventarios.add_movimientostock', raise_exception=True)
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
                    return redirect('list_movimientos')
                    
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

@login_required(login_url='login/')
@permission_required('inventarios.add_configuracionstock', raise_exception=True)
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
    
    


'''def productos_mas_vendidos(request):
    # Filtra ventas activas y agrupa por producto
    productos = VentaDetalle.objects.filter(activo=True).values(
        'producto__nombre',  # Asegúrate de que 'nombre' sea el campo correcto en tu modelo Producto
        #'producto__codigo',  # Opcional: para mostrar el código
    ).annotate(
        total_vendido=Sum('cantidad')
    ).order_by('-total_vendido')[:2]  # Top 10 productos más vendidos

    # Preparar datos para el gráfico
    nombres = [p['producto__nombre'] for p in productos]
    cantidades = [p['total_vendido'] for p in productos]

    context = {
        'nombres': nombres,
        'cantidades': cantidades,
    }
    return render(request, 'reportes/productos_mas_vendidos.html', context)'''



def productos_mas_vendidos_v2(request):
    # Filtros
    categoria_id = request.GET.get('categoria')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    # Consulta base
    productos_query = VentaDetalle.objects.filter(activo=True)
    
    # Aplicar filtro de categoría si existe
    if categoria_id:
        productos_query = productos_query.filter(producto__categoria_id=categoria_id)
        
    if fecha_inicio and fecha_fin:
        try:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
            productos_query = productos_query.filter(
                venta_cab__fecha_venta__range=(fecha_inicio, fecha_fin)
            )
        except ValueError:
            print('ERROR, VERIFIQUE LA FECHA')
    
    # Top 10 productos para la tabla
    top_10_productos = productos_query.values(
        'producto__nombre',
        'producto__categoria__nombre'  # Nombre de la categoría
    ).annotate(
        total_vendido=Sum('cantidad'),
        total_ingresos=Sum('subtotal')
    ).order_by('-total_vendido')[:10]  # Limita a 10 resultados
    
     # Cálculo del total general de ventas
    totales = productos_query.aggregate(
        total_ventas=Sum('subtotal'),
        total_unidades=Sum('cantidad')
    )
  
   # Gráfico Plotly (sin pandas)
    nombres = [p['producto__nombre'] for p in top_10_productos[:5]]  # Top 5
    cantidades = [p['total_vendido'] for p in top_10_productos[:5]]
    ingresos = [p['total_ingresos'] for p in top_10_productos[:5]]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=nombres,
        y=cantidades,
        marker_color='#4e73df',
        text=[f"{v} unid.<br>{i:,.0f} GS" for v, i in zip(cantidades, ingresos)],
        textposition='auto',
        hoverinfo='text'
    ))
    
    fig.update_layout(
        title='Top 5 Productos Más Vendidos',
        xaxis_title='Productos',
        yaxis_title='Cantidad Vendida',
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode='x',
        showlegend=False
    )
    
    context = {
        'productos': top_10_productos,
        'total_ventas': totales.get('total_ventas', 0),
        'total_unidades': totales.get('total_unidades', 0),
        'graph_json': fig.to_json(),
        'todas_categorias': Categoria.objects.all(),
        'categoria_seleccionada': int(categoria_id) if categoria_id else None,
        'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d') if fecha_inicio else '',
        'fecha_fin': fecha_fin.strftime('%Y-%m-%d') if fecha_fin else ''
    }
    
    return render(request, 'reportes/productos_mas_vendidos_v3.html', context)

def exportar_productos_mas_vendidos_pdf(request):
    
    # Filtros
    categoria_id = request.GET.get('categoria')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    # Consulta base
    productos_query = VentaDetalle.objects.filter(activo=True)
    
    # Aplicar filtro de categoría si existe
    if categoria_id:
        productos_query = productos_query.filter(producto__categoria_id=categoria_id)
        
    if fecha_inicio and fecha_fin:
        try:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
            productos_query = productos_query.filter(
                venta_cab__fecha_venta__range=(fecha_inicio, fecha_fin)
            )
        except ValueError:
            print('ERROR, VERIFIQUE LA FECHA')
    
    # Top 10 productos para la tabla
    top_10_productos = productos_query.values(
        'producto__nombre',
        'producto__categoria__nombre'  # Nombre de la categoría
    ).annotate(
        total_vendido=Sum('cantidad'),
        total_ingresos=Sum('subtotal')
    ).order_by('-total_vendido')[:10]  # Limita a 10 resultados
    
     # Cálculo del total general de ventas
    totales = productos_query.aggregate(
        total_ventas=Sum('subtotal'),
        total_unidades=Sum('cantidad')
    )
   
    context = {
        'productos': top_10_productos,
        'total_ventas': totales.get('total_ventas', 0),
        'total_unidades': totales.get('total_unidades', 0),
        'filtro_categoria': Categoria.objects.get(id=categoria_id).nombre if categoria_id else 'Todas',
        'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d') if fecha_inicio else '',
        'fecha_fin': fecha_fin.strftime('%Y-%m-%d') if fecha_fin else ''
    }
    
    
    # Renderizar HTML
    html_string = render_to_string('reportes/mas_vendidos_pdf.html', context)
    
    # CSS para el PDF
    css = CSS(string='''
        @page { size: A4; margin: 1cm; }
        body { font-family: Arial; font-size: 10pt; }
        h1 { color: #2c3e50; text-align: center; }
        .header-info { margin-bottom: 20px; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th { background-color: #f2f2f2; text-align: left; }
        th, td { border: 1px solid #ddd; padding: 6px; }
        .total-row { font-weight: bold; background-color: #e9ecef; }
        .text-right { text-align: right; }
    ''')
    
    # Generar PDF
    pdf_buffer = BytesIO()
    HTML(string=html_string).write_pdf(pdf_buffer, stylesheets=[css])
    
    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    filename = f"inventario_{categoria_id if categoria_id else 'completo'}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response



def valor_inventario_gral_v3(request):
    # Filtros
    categoria_id = request.GET.get('categoria')
    producto_nombre = request.GET.get('producto')
    
    # Consulta base de productos
    productos = Producto.objects.all().order_by('nombre')
    
    productos = productos.annotate(
        stock_final=F('cantidad_en_stock'),
        valor_costo=F('cantidad_en_stock') * F('precio_compra'),
        valor_venta=F('cantidad_en_stock') * F('precio_venta')
    )
    
    # Aplicar filtros adicionales
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    if producto_nombre:
        productos = productos.filter(nombre__icontains=producto_nombre)
    
    # Calcular totales generales
    totales = productos.aggregate(
        total_costo=Sum('valor_costo'),
        total_venta=Sum('valor_venta')
    )
    
    # Datos para el gráfico por categorías
    categorias_data = Categoria.objects.annotate(
        total_costo=Sum(
            F('producto__cantidad_en_stock') * F('producto__precio_compra'),
            output_field=models.DecimalField()
        ),
        total_venta=Sum(
            F('producto__cantidad_en_stock') * F('producto__precio_venta'),
            output_field=models.DecimalField()
        )
    ).filter(total_costo__gt=0).order_by('-total_costo')
    
    # Calcular totales para el grafico
    total_costo_grafico = sum(float(cat.total_costo) for cat in categorias_data)
    total_venta_grafico = sum(float(cat.total_venta) for cat in categorias_data)
    
    # Preparar datos para Chart.js (ahora combinados en una sola lista de tuplas)
    datos_grafico = [
        {
            'nombre': cat.nombre,
            'valor_costo': float(cat.total_costo),
            'valor_venta': float(cat.total_venta),
            'porcentaje': round((float(cat.total_costo) / total_costo_grafico) * 100, 1) if total_costo_grafico > 0 else 0,
            'color': f"rgba({randint(50, 200)}, {randint(50, 200)}, {randint(50, 200)}, 0.7)"
        }
        for cat in categorias_data
    ]
    
    context = {
        'productos': productos,
        'total_general': totales.get('total_costo', 0),
        'total_venta': totales.get('total_venta', 0),
        'todas_categorias': Categoria.objects.all(),
        'categoria_seleccionada': int(categoria_id) if categoria_id else None,
        'datos_grafico': datos_grafico,  # Datos ya combinados
        'datos_grafico_json': mark_safe(json.dumps([
            {
                'nombre': item['nombre'],
                'valor_costo': item['valor_costo'],
                'valor_venta': item['valor_venta'],
                'porcentaje':item['porcentaje'],
                'color': item['color']
            }
            for item in datos_grafico
        ])),
        'total_costo_grafico': total_costo_grafico,
        'total_venta_grafico': total_venta_grafico
    }
    
    return render(request, 'reportes/valor_inventario.html', context)


def exportar_grafico_pdf_v2(request):
    # Reutilizamos la lógica para obtener los datos del gráfico
    categorias_data_queryset = Categoria.objects.annotate(
        total_costo=Sum(F('producto__cantidad_en_stock') * F('producto__precio_compra')),
        total_venta=Sum(F('producto__cantidad_en_stock') * F('producto__precio_venta'))
    ).filter(total_costo__gt=0).order_by('-total_costo')

    # Preparar datos
    categorias = [cat.nombre for cat in categorias_data_queryset]
    valores_costo = [float(cat.total_costo) for cat in categorias_data_queryset]
    valores_venta = [float(cat.total_venta) for cat in categorias_data_queryset]
    total_costo = sum(valores_costo)
    total_venta = sum(valores_venta)

    # Colores válidos para matplotlib (tuplas RGB normalizadas entre 0 y 1)
    colores = [
        (randint(50, 200)/255, randint(50, 200)/255, randint(50, 200)/255)
        for _ in categorias_data_queryset
    ]

    # Crear el gráfico con matplotlib
    plt.figure(figsize=(10, 6))
    plt.bar(categorias, valores_costo, color=colores)
    plt.plot(categorias, valores_venta, color='red', marker='o', linestyle='--', linewidth=2, label='Valor Venta')
    plt.title('Distribución del Inventario por Categoría', fontsize=16)
    plt.xlabel('Categorías', fontsize=12)
    plt.ylabel('Valor (GS)', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.legend()
    plt.tight_layout()

    # Guardar el gráfico en un buffer
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150)
    plt.close()
    img_buffer.seek(0)
    img_data = base64.b64encode(img_buffer.read()).decode('utf-8')

    # Calcular porcentaje de participación por categoría
    categorias_data = []
    for nombre, costo, venta, color in zip(categorias, valores_costo, valores_venta, colores):
        porcentaje = (costo / total_costo * 100) if total_costo > 0 else 0
        categorias_data.append((nombre, costo, venta, color, porcentaje))

    # Renderizar el template PDF
    context = {
        'grafico_img': img_data,
        'categorias_data': categorias_data,
        'total_costo': total_costo,
        'total_venta': total_venta,
        'fecha': timezone.now().strftime("%d/%m/%Y %H:%M")
    }

    html_string = render_to_string('reportes/valor_inventario_grafico_pdf.html', context)

    # Generar PDF
    pdf_buffer = BytesIO()
    HTML(string=html_string).write_pdf(pdf_buffer)

    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="grafico_inventario.pdf"'
    return response


def exportar_inventario_pdf(request):
    # Reutilizamos la misma lógica de filtrado que en valor_inventario_gral_v3
    categoria_id = request.GET.get('categoria')
    producto_nombre = request.GET.get('producto')
    
    productos = Producto.objects.all().order_by('nombre')
    productos = productos.annotate(
        valor_costo=F('cantidad_en_stock') * F('precio_compra'),
        valor_venta=F('cantidad_en_stock') * F('precio_venta')
    )
    
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    if producto_nombre:
        productos = productos.filter(nombre__icontains=producto_nombre)
    
    totales = productos.aggregate(
        total_costo=Sum('valor_costo'),
        total_venta=Sum('valor_venta')
    )
    
    context = {
        'productos': productos,
        'total_general': totales.get('total_costo', 0),
        'total_venta': totales.get('total_venta', 0),
        'filtro_categoria': Categoria.objects.get(id=categoria_id).nombre if categoria_id else 'Todas',
        'filtro_producto': producto_nombre if producto_nombre else 'Todos'
    }
    
    # Renderizar HTML
    html_string = render_to_string('reportes/valor_inventario_pdf.html', context)
    
    # CSS para el PDF
    css = CSS(string='''
        @page { size: A4; margin: 1cm; }
        body { font-family: Arial; font-size: 10pt; }
        h1 { color: #2c3e50; text-align: center; }
        .header-info { margin-bottom: 20px; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th { background-color: #f2f2f2; text-align: left; }
        th, td { border: 1px solid #ddd; padding: 6px; }
        .total-row { font-weight: bold; background-color: #e9ecef; }
        .text-right { text-align: right; }
    ''')
    
    # Generar PDF
    pdf_buffer = BytesIO()
    HTML(string=html_string).write_pdf(pdf_buffer, stylesheets=[css])
    
    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    filename = f"inventario_{categoria_id if categoria_id else 'completo'}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def inventory_summary(request):
    # Productos en stock crítico (debajo del mínimo)
    
    confi = ConfiguracionStock.get_config()
    stock_minimo = confi.cantidad_maxima
    critical_items = Producto.objects.filter(
        cantidad_en_stock__lte=stock_minimo
    ).count()
    
    # Movimientos de stock en el día actual
    movements_today = MovimientoStock.objects.filter(
        fecha_movimiento__date=timezone.now().date()
    ).count()
    
    # Valor total del inventario (sumatoria de precio_compra * cantidad)
    total_value = Producto.objects.aggregate(
        total_value=Sum(F('cantidad_en_stock') * F('precio_compra'))
    )['total_value'] or 0
    
    return JsonResponse({
        'critical_items': critical_items,
        'movements_today': movements_today,
        'total_value': round(total_value, 2) if total_value else 0
    })

def lista_stock_critico(request):
    confi = ConfiguracionStock.get_config()
    if not confi:
        messages.error(request, 'No hay configuración de stock crítico definida.')
        #return redirect('inventario:configurar_stock')
        productos_criticos = []
        stock_minimo = 0
    else:
        stock_minimo = confi.cantidad_maxima
        productos_criticos = Producto.objects.filter(
            cantidad_en_stock__lte=stock_minimo
        ).order_by('cantidad_en_stock')

        # Agregamos una propiedad `clase` para el template
        for p in productos_criticos:
            if p.cantidad_en_stock <= stock_minimo:
                p.clase = 'text-danger'
            else:
                p.clase = 'text-warning'
            p.diferencia = p.cantidad_en_stock - stock_minimo

    context = {
        'productos': productos_criticos,
        'titulo': 'Productos en Stock Crítico',
        'stock_minimo': stock_minimo,
    }
    return render(request, 'stock/stock_critico.html', context)


def movimientos_recientes(request):
    # Últimos 30 días de movimientos
    fecha_inicio = timezone.now() - timezone.timedelta(days=30)
    
    movimientos = MovimientoStock.objects.filter(
        fecha_movimiento__gte=fecha_inicio
    ).select_related('producto').order_by('-fecha_movimiento')
    
    # Agrupar por día para el template
    movimientos_por_dia = {}
    for mov in movimientos:
        fecha = mov.fecha_movimiento.date()
        if fecha not in movimientos_por_dia:
            movimientos_por_dia[fecha] = []
        movimientos_por_dia[fecha].append(mov)
    
    context = {
        'movimientos_por_dia': sorted(movimientos_por_dia.items(), reverse=True),
        'titulo': 'Historial de Movimientos'
    }
    return render(request, 'stock/ultimos_movimientos.html', context)


def valor_inventario_historico(request):
    # Filtros temporales
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    anio = request.GET.get('anio')
    mes = request.GET.get('mes')
    dia = request.GET.get('dia')
    
    print('Mes:', mes, 'Año:', anio, 'Día:', dia)
    
    # Filtros por producto/proveedor
    categoria_id = request.GET.get('categoria')
    producto_id = request.GET.get('producto')
    proveedor_id = request.GET.get('proveedor')
    
    # Filtros por tipo de transacción
    tipo_movimiento = request.GET.get('tipo_movimiento')
    tipo_ajuste = request.GET.get('tipo_ajuste')
    
    # Consulta base
    movimientos = MovimientoStock.objects.select_related(
        'producto', 
        'producto__categoria', 
        'producto__proveedor'
    ).order_by('-fecha')
    
    # Aplicar filtros temporales
    if fecha_inicio and fecha_fin:
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d') + timedelta(days=1)
        movimientos = movimientos.filter(fecha__range=[fecha_inicio, fecha_fin])
    elif anio:
        if mes:
            if dia:
                # Filtro por día específico
                fecha = datetime(int(anio), int(mes), int(dia))
                movimientos = movimientos.filter(fecha__date=fecha)
            else:
                # Filtro por mes/año
                movimientos = movimientos.filter(
                    fecha__year=anio,
                    fecha__month=mes
                )
        else:
            # Filtro solo por año
            movimientos = movimientos.filter(fecha__year=anio)
    
    # Aplicar filtros de producto/proveedor
    if categoria_id:
        movimientos = movimientos.filter(producto__categoria_id=categoria_id)
    if producto_id:
        movimientos = movimientos.filter(producto_id=producto_id)
    if proveedor_id:
        movimientos = movimientos.filter(producto__proveedor_id=proveedor_id)
    
    # Aplicar filtros de transacción
    if tipo_movimiento:
        movimientos = movimientos.filter(movimiento=tipo_movimiento)
    if tipo_ajuste:
        movimientos = movimientos.filter(ajuste=tipo_ajuste)
    
    # Anotar con valor de costo y venta
    movimientos = movimientos.annotate(
        valor_costo=F('cantidad') * F('producto__precio_compra'),
        valor_venta=F('cantidad') * F('producto__precio_venta')
    )
    
    if dia:
        agrupacion = 'fecha__date'
        formato_fecha = lambda x: x.strftime("%d/%m/%Y")
        resumen = movimientos.values(agrupacion).annotate(
            total_costo=Sum('valor_costo'),
            total_venta=Sum('valor_venta'),
            total_movimientos=Count('id')
        ).order_by(agrupacion)
    elif mes:
        agrupacion = 'fecha__day'
        formato_fecha = lambda x: f"Día {x}"
        resumen = movimientos.values(agrupacion).annotate(
            total_costo=Sum('valor_costo'),
            total_venta=Sum('valor_venta'),
            total_movimientos=Count('id')
        ).order_by(agrupacion)
    else:
        agrupacion = 'fecha__month'
        meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
                 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        formato_fecha = lambda x: meses[x-1] if 1 <= x <= 12 else str(x)
        resumen = movimientos.values(agrupacion).annotate(
            total_costo=Sum('valor_costo'),
            total_venta=Sum('valor_venta'),
            total_movimientos=Count('id')
        ).order_by(agrupacion)
    
    # Preparar datos para el gráfico
    datos_grafico = {
        'fechas': [formato_fecha(item[agrupacion]) for item in resumen],
        'costos': [float(item['total_costo']) for item in resumen],
        'ventas': [float(item['total_venta']) for item in resumen]
    }
    
    # Agregar totales por período
    resumen = movimientos.values(agrupacion).annotate(
        total_costo=Sum('valor_costo'),
        total_venta=Sum('valor_venta'),
        total_movimientos=Count('id')
    ).order_by(agrupacion)
    
    # Totales generales
    totales = movimientos.aggregate(
        total_costo=Sum('valor_costo'),
        total_venta=Sum('valor_venta'),
        total_movimientos=Count('id')
    )
    
    # Obtener opciones para filtros
    categorias = Categoria.objects.all()
    productos = Producto.objects.all()
    proveedores = Proveedor.objects.all()
    
    context = {
        'movimientos': movimientos,
        'resumen': resumen,
        'datos_grafico': datos_grafico,
        'totales': totales,
        'categorias': categorias,
        'productos': productos,
        'proveedores': proveedores,
        'meses' : [(1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'),(4, 'Abril'),(5, 'Mayo'),(6, 'Junio'),(7, 'Julio'),(8, 'Agosto'),(9, 'Setiembre'),(10, 'Octubre'),(11, 'Noviembre'),(12, 'Diciembre')],
        'filtros': {
            'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d') if fecha_inicio else '',
            'fecha_fin': fecha_fin.strftime('%Y-%m-%d') if fecha_fin else '',
            'anio': anio,
            'mes': int(mes) if mes else None,
            'dia': dia,
            'categoria_id': int(categoria_id) if categoria_id else None,
            'producto_id': int(producto_id) if producto_id else None,
            'proveedor_id': int(proveedor_id) if proveedor_id else None,
            'tipo_movimiento': tipo_movimiento,
            'tipo_ajuste': tipo_ajuste,
        }
    }
    
    return render(request, 'reportes/valor_inventario_historico.html', context)



def exportar_inventario_historico_pdf(request):
    # Obtener los mismos parámetros de filtro que en la vista principal
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    anio = request.GET.get('anio')
    mes = request.GET.get('mes')
    dia = request.GET.get('dia')
    categoria_id = request.GET.get('categoria')
    producto_id = request.GET.get('producto')
    proveedor_id = request.GET.get('proveedor')
    tipo_movimiento = request.GET.get('tipo_movimiento')
    tipo_ajuste = request.GET.get('tipo_ajuste')
    
    # Replicar la lógica de filtrado de la vista principal
    movimientos = MovimientoStock.objects.select_related(
        'producto', 'producto__categoria', 'producto__proveedor'
    ).order_by('-fecha')
    
    # Aplicar filtros (igual que en la vista principal)
    if fecha_inicio and fecha_fin:
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d') + timedelta(days=1)
        movimientos = movimientos.filter(fecha__range=[fecha_inicio, fecha_fin])
    elif anio:
        if mes:
            if dia:
                fecha = datetime(int(anio), int(mes), int(dia))
                movimientos = movimientos.filter(fecha__date=fecha)
            else:
                movimientos = movimientos.filter(
                    fecha__year=anio,
                    fecha__month=mes
                )
        else:
            movimientos = movimientos.filter(fecha__year=anio)
    
    if categoria_id:
        movimientos = movimientos.filter(producto__categoria_id=categoria_id)
    if producto_id:
        movimientos = movimientos.filter(producto_id=producto_id)
    if proveedor_id:
        movimientos = movimientos.filter(producto__proveedor_id=proveedor_id)
    if tipo_movimiento:
        movimientos = movimientos.filter(movimiento=tipo_movimiento)
    if tipo_ajuste:
        movimientos = movimientos.filter(ajuste=tipo_ajuste)
    
    # Anotar con valores calculados
    movimientos = movimientos.annotate(
        valor_costo=F('cantidad') * F('producto__precio_compra'),
        valor_venta=F('cantidad') * F('producto__precio_venta')
    )
    
    # Calcular totales
    totales = movimientos.aggregate(
        total_costo=Sum('valor_costo'),
        total_venta=Sum('valor_venta'),
        total_movimientos=Count('id')
    )
    
    # Obtener el nombre del mes si hay filtro por mes
    nombre_mes = ''
    if mes:
        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        nombre_mes = meses[int(mes)-1] if 1 <= int(mes) <= 12 else mes
    
    # Preparar el contexto para el PDF
    context = {
        'movimientos': movimientos,
        'totales': totales,
        'filtros': {
            'fecha_inicio': fecha_inicio.strftime('%d/%m/%Y') if fecha_inicio else '',
            'fecha_fin': fecha_fin.strftime('%d/%m/%Y') if fecha_fin else '',
            'anio': anio,
            'mes': nombre_mes,
            'dia': dia,
            'categoria': Categoria.objects.get(id=categoria_id).nombre if categoria_id else 'Todas',
            'producto': Producto.objects.get(id=producto_id).nombre if producto_id else 'Todos',
            'proveedor': Proveedor.objects.get(id=proveedor_id).nombre if proveedor_id else 'Todos',
            'tipo_movimiento': dict(MovimientoStock.TIPO_MOVIMIENTO).get(tipo_movimiento, 'Todos') if tipo_movimiento else 'Todos',
            'tipo_ajuste': dict(MovimientoStock.TIPO_AJUSTE).get(tipo_ajuste, 'Todos') if tipo_ajuste else 'Todos',
        },
        'fecha_generacion': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    }
    
    # Renderizar el template HTML
    template = get_template('reportes/inventario_historico_pdf.html')
    #template = get_template('reportes/prueba.html')
    html = template.render(context)
    
    print('HTML generado para PDF:', html)  # Para depuración
    
    # Crear el PDF
    response = HttpResponse(content_type='application/pdf')
    nombre_archivo = f"Inventario_Historico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
    
    # Generar PDF
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('Error al generar PDF', status=500)
    
    return response


def analisis_abc(request):
    # Calcular valor total por producto
    productos = Producto.objects.annotate(
        valor_total=ExpressionWrapper(
            F('cantidad_en_stock') * F('precio_compra'),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )
    ).filter(
        cantidad_en_stock__gt=0
    ).order_by('-valor_total')
    
    # Calcular valores acumulados
    valor_total_inventario = sum(p.valor_total for p in productos)
    acumulado = 0
    abc_data = []
    
    for producto in productos:
        porcentaje_valor = (producto.valor_total / valor_total_inventario) * 100
        acumulado += porcentaje_valor
        
        if acumulado <= 80:
            clase = 'A'
        elif acumulado <= 95:
            clase = 'B'
        else:
            clase = 'C'
        
        '''abc_data.append({
            'id': producto.id,
            'nombre': producto.nombre,
            'valor_total': producto.valor_total,
            'porcentaje': porcentaje_valor,
            'porcentaje_acumulado': acumulado,
            'clase': clase
        })'''
        abc_data.append({
            'id': producto.id,
            'nombre': producto.nombre,
            'valor_total': float(producto.valor_total),  #
            'porcentaje': float(porcentaje_valor),
            'porcentaje_acumulado': float(acumulado),
            'clase': clase
    })
    # Ordenar por clase y luego por valor total    
    # Estadísticas resumen
    count_a = len([p for p in abc_data if p['clase'] == 'A'])
    count_b = len([p for p in abc_data if p['clase'] == 'B'])
    count_c = len([p for p in abc_data if p['clase'] == 'C'])
    
    return JsonResponse({
        'abc_data': abc_data,
        'stats': {
            'total_valor': float(valor_total_inventario),  # Convertir a float para JSON
            'count_a': count_a,
            'count_b': count_b,
            'count_c': count_c,
            'percent_a': float(sum(p['porcentaje'] for p in abc_data if p['clase'] == 'A')),
            'percent_b': float(sum(p['porcentaje'] for p in abc_data if p['clase'] == 'B')),
            'percent_c': float(sum(p['porcentaje'] for p in abc_data if p['clase'] == 'C'))
        }
    })
    
'''def prediccion_reabastecimiento(request):
    productos = Producto.objects.annotate(
        ventas_30d=Coalesce(
            Sum('ventadetalle__cantidad', 
                filter=Q(ventadetalle__venta_cab__fecha_venta__gte=timezone.now()-timedelta(days=30))),
            0
        )
    ).filter(
        ventas_30d__gt=0  # Solo productos con ventas recientes
    )
    
    predicciones = []
    for p in productos:
        dias_restantes = (p.cantidad_actual / (p.ventas_30d/30)) if p.ventas_30d else 0
        predicciones.append({
            'nombre': p.nombre,
            'stock_actual': p.cantidad_actual,
            'dias_restantes': round(dias_restantes, 1),
            'cantidad_sugerida': round((p.ventas_30d/30)*15)  # 15 días de stock
        })
    
    return {
        'predicciones': sorted(predicciones, key=lambda x: x['dias_restantes'])
    }'''
    
    
def api_rotacion_inventario(request):
    try:
        # Productos con mayor rotación (ventas/stock)
        top_rotacion = Producto.objects.filter(
            cantidad_en_stock__gt=0
        ).annotate(
            ventas_30d=Coalesce(
                Sum('ventadetalle__cantidad',
                    filter=Q(ventadetalle__venta_cab__fecha_venta__gte=timezone.now()-timedelta(days=30))),
                0
            ),
            rotacion=ExpressionWrapper(
                F('ventas_30d') / F('cantidad_en_stock'),
                output_field=FloatField()
            )
        ).filter(
            ventas_30d__gt=0
        ).order_by('-rotacion')[:5].values('nombre', 'rotacion')
        
        print('Top rotación:', list(top_rotacion))  # Para depuración
        
        # Productos sin movimiento en 30 días
        sin_rotacion = Producto.objects.annotate(
            ultima_venta=Max('ventadetalle__venta_cab__fecha_venta')
        ).filter(
            ultima_venta__lt=timezone.now()-timedelta(days=30)
        ).annotate(
            dias_sin_movimiento=ExpressionWrapper(
                timezone.now().date() - F('ultima_venta__date'),
                output_field=FloatField()
            )
        ).order_by('-dias_sin_movimiento').values('nombre', 'dias_sin_movimiento')
        
        # Datos para el gráfico (top 5 productos)
        chart_data = Producto.objects.filter(
            cantidad_en_stock__gt=0
        ).annotate(
            rotacion=ExpressionWrapper(
                Coalesce(
                    Sum('ventadetalle__cantidad',
                        filter=Q(ventadetalle__venta_cab__fecha_venta__gte=timezone.now()-timedelta(days=30))),
                    0
                ) / F('cantidad_en_stock'),
                output_field=FloatField()
            )
        ).order_by('-rotacion')[:5]
        
        response_data = {
            'top_rotacion': list(top_rotacion),
            'sin_rotacion': list(sin_rotacion),
            'chart_labels': [p.nombre for p in chart_data],
            'chart_values': [float(p.rotacion) for p in chart_data]
        }
        
        return JsonResponse(response_data)
    
    except Exception as e:
        print(f"Error en api_rotacion_inventario: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


def prediccion_reabastecimiento(request):
    DIAS_PREDICCION = 15
    DIAS_HISTORICO = 30
    
    productos = Producto.objects.filter(
        cantidad_en_stock__gt=0
    ).annotate(
        ventas_30d=Coalesce(
            Sum('ventadetalle__cantidad',
                filter=Q(
                    ventadetalle__venta_cab__fecha_venta__gte=timezone.now()-timedelta(days=DIAS_HISTORICO)
                )),
            0
        ),
        ventas_diarias=ExpressionWrapper(
            F('ventas_30d') / DIAS_HISTORICO,
            output_field=FloatField()
        )
    ).filter(
        ventas_30d__gt=0
    ).annotate(
        dias_restantes=Case(
            When(ventas_diarias__gt=0, then=F('cantidad_en_stock')/F('ventas_diarias')),
            default=float('inf'),
            output_field=FloatField()
        ),
        sugerencia=Round(F('ventas_diarias') * DIAS_PREDICCION)
    )
    
    return {
        'predicciones': productos.order_by('dias_restantes').values(
            'nombre',
            'cantidad_en_stock',
            'dias_restantes',
            'sugerencia'
        )
    }