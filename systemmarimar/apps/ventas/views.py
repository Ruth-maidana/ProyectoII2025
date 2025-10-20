import io
from datetime import datetime
from django.template.loader import get_template
from xhtml2pdf import pisa
import matplotlib.pyplot as plt
import matplotlib
from django.utils import timezone
import logging
from apps.inventarios.models import MovimientoStock
matplotlib.use('Agg') 
import base64
from django.db.models.functions import ExtractMonth, ExtractYear
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required,permission_required
from apps.compras.models import Producto
from .models import Cliente, ConfigTimbradoNumeracion, Empresa, VentaCabecera, VentaDetalle
from .forms import ClienteViewForm, FormEditarCliente, FormEditarVentaCabecera, FormRegistrarCliente, FormRegVentaCabecera, FormRegVentaDetalle, FormEditVentaDetalle, FormConfigTimbradoNumeracion
from django.forms import formset_factory, inlineformset_factory
from django.db.models import Q,Sum
from apps.inventarios.utils import registrar_movimiento_stock
from django.db import transaction 
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required,permission_required
from django.views.decorators.http import require_http_methods
 # Para evitar problemas con el backend gráfico
# Create your views here.

logger = logging.getLogger(__name__)


def registrar_config_tim_num(request):
    config = ConfigTimbradoNumeracion.objects.first()

    if request.method == 'POST':
        form = FormConfigTimbradoNumeracion(request.POST, instance=config)
        if form.is_valid():
            form.save()
            return redirect('home')  # o a ventas, según flujo
    else:
        form = FormConfigTimbradoNumeracion(instance=config)

    return render(request, 'configuracion/timbrado_numeracion.html', {'form': form})
       

@login_required(login_url='login/')
@permission_required('ventas.add_cliente', raise_exception=True)
@require_http_methods(["GET", "POST"])
def registrar_cliente(request):
    if request.method == 'POST':
        form_reg_cliente = FormRegistrarCliente(request.POST)
        if form_reg_cliente.is_valid():
            form_reg_cliente.save()
            messages.success(request, ("Cliente Registrado Exitosamente"))
            print('Entro correctamente')
            return redirect('list_clientes')
        else:
            print('Hay error')  # Replace with logging if needed
            print(form_reg_cliente.errors)
            messages.error(request, '¡Hubo un error al registrar el cliente!')
    else:
        form_reg_cliente = FormRegistrarCliente()

    context = {
        'form_cliente': form_reg_cliente,
    }

    return render(request, 'clientes/registrar.html', context)


@login_required(login_url='login/')
@permission_required('ventas.change_cliente', raise_exception=True)
@require_http_methods(["GET", "POST"])
def editar_cliente(request, id_cliente):
    # Recuperamos la instancia del proyecto
    cliente = Cliente.objects.get(id=id_cliente)

    if request.method == "GET":
        # Actualizamos el formulario con los datos recibidos
        form_edit_cliente = FormEditarCliente(instance=cliente)
        print("Obtiene los datos")
    else:
        form_edit_cliente = FormEditarCliente(request.POST, instance=cliente)

        if form_edit_cliente.is_valid():
            form_edit_cliente.save()
            print("Modificado exitosamente")
            messages.success(request, ("Cliente Modificado Exitosamente"))
            return redirect('list_clientes')

        else:
            messages.error(request, ("Error, Verifique los campos"))
            print("Error en el campo")
    context = {
        'form_cliente': form_edit_cliente,
    }
    return render(request, 'clientes/editar.html', context)

@login_required(login_url='login/')
@permission_required('ventas.delete_cliente', raise_exception=True)
def inactivar_cliente(request, id_cliente):
    cliente = Cliente.objects.get(id=id_cliente)
    cliente.activo = False
    messages.success(request, "Cliente eliminado correctamente")
    cliente.save()
    return redirect('list_clientes')


@login_required(login_url='login/')
@permission_required('ventas.view_cliente', raise_exception=True)
def listar_cliente(request):
    clientes = Cliente.objects.all().order_by('id')
    clientes_forms = []
    for cliente in clientes:
        formulario = ClienteViewForm(instance=cliente)
        clientes_forms.append({
            'cliente': cliente,
            'form': formulario
        })
    return render(request, 'clientes/listar.html', {'Clientes': clientes, 'clientes_forms': clientes_forms})


##################### VENTAS  #######################

@login_required(login_url='login/')
@permission_required('ventas.add_ventacabecera', raise_exception=True)
@permission_required('ventas.add_ventadetalle', raise_exception=True)
@require_http_methods(["GET", "POST"])
def registrar_venta(request):
    formset_venta = formset_factory(FormRegVentaDetalle, extra=0, can_delete=True)
    datos_empresa = Empresa.objects.first()
    fecha_actual = timezone.now
        
    if datos_empresa:
        print(f"Datos de la empresa: {datos_empresa.nombre}, {datos_empresa.ruc}, {datos_empresa.direccion}")
    else:
        print("No se encontraron datos de la empresa.")
        
    config = ConfigTimbradoNumeracion.objects.first()  # Asumiendo solo una config activa
    numero_formateado = config.obtener_numeracion_formateada()

    if request.method == 'POST':
        form_venta_cab = FormRegVentaCabecera(request.POST)
        form_venta_det = formset_venta(request.POST,prefix='form')
        
        logger.debug(f"Datos POST recibidos: {dict(request.POST)}")

        if form_venta_cab.is_valid() and form_venta_det.is_valid():
            
            logger.info("Formularios válidos")
            
            # CORRECCIÓN: Validar que haya detalles ANTES de guardar la cabecera
            detalles_validos = []
            
            for form_det in form_venta_det:
                if form_det.cleaned_data and not form_det.cleaned_data.get('DELETE', False):
                    producto_id = form_det.cleaned_data.get('producto_id')
                    cantidad = form_det.cleaned_data.get('cantidad')
					
                    if producto_id and cantidad:
                        detalles_validos.append(form_det)
                    else:
                        messages.warning(request, "Detalle inválido - campos obligatorios faltantes")
                        logger.warning("Detalle inválido - campos obligatorios faltantes")
            
            logger.info(f"Total de detalles válidos: {len(detalles_validos)}")
            
            # Si no hay detalles válidos, mostrar error y no guardar nada
            if len(detalles_validos) == 0:
                messages.warning(request, "Debe ingresar al menos un detalle de venta válido.")
                logger.warning("No se encontraron detalles válidos")
	
                context = {
                    'form_venta_cab': form_venta_cab,
                    'form_venta_det': form_venta_det,
                    'empresa': datos_empresa,
                    'form_venta_det_prefix':form_venta_det.prefix
				}
                return render(request, 'ventas/registrar5.html', context)
            
            
            try:
                with transaction.atomic():
                    # Guardar la cabecera de la venta
                    cabecera = form_venta_cab.save()
                    logger.info(f"Cabecera de compra guardada: {cabecera.nro_comprobante}")
                    
                    # Guardar los detalles válidos
                    detalles_guardados = 0
                    
                    # Guardar los detalles de la venta
                    for form_det in detalles_validos:
                        
                        logger.debug(f"Procesando detalle: {form_det.cleaned_data}")
                        
                        producto_id = form_det.cleaned_data.get('producto_id')
                        cantidad = form_det.cleaned_data.get('cantidad')
                        descripcion = form_det.cleaned_data.get('descripcion')
                        unidad_medida = form_det.cleaned_data.get('unidad_medida')
                        precio_venta = form_det.cleaned_data.get('precio_unit_venta')
                        subtotal = form_det.cleaned_data.get('subtotal')
                        
                        try:
                            producto_instance = Producto.objects.get(id=producto_id)
                        except Producto.DoesNotExist:
                            messages.error(request, f"Producto con ID {producto_id} no existe. Detalle omitido.")
                            logger.error(f"Producto con ID {producto_id} no existe. Saltando detalle.")
                            continue
                        
                        # Aquí puedes realizar la lógica para guardar los detalles de la venta
                        detalle = VentaDetalle(
                            venta_cab=cabecera,
                            producto=producto_instance,
                            cantidad=cantidad,
                            descripcion=descripcion,
                            unidad_medida=unidad_medida,
                            precio_unit_venta=precio_venta,
                            subtotal=subtotal,
                        )
                        
                        logger.debug(f"Guardando detalle: {detalle}")
                        
                        detalle.save()
                        detalles_guardados += 1
                        
                        # Guardar el movimiento de stock
                        registrar_movimiento_stock(
                            producto=detalle.producto,
                            cantidad=detalle.cantidad,
                            movimiento='SALIDA',
                            descripcion=f"Venta registrada: {cabecera.nro_comprobante}",
                            ajuste=None,
                            fecha_mov_producto=cabecera.fecha_venta,
                            compra_cab=None,
                            venta_cab=cabecera
                        )
                        
                        
                        logger.debug(f"Movimiento de stock registrado para producto {detalle.producto.nombre}")
                        
                    # Actualizar el número de timbrado
                    config.incrementar_numeracion()  # Actualiza el número de timbrado
                    logger.info(f"Número de timbrado actualizado a {config.nro_final}")
                    
                    messages.success(request, "Venta registrada exitosamente")
                    
                    return redirect('list_ventas')
                
            except Exception as e:
                messages.error(request, f'Error al registrar la venta: {str(e)}')
                logger.error(f'Error al registrar la venta: {str(e)}')
                            
        else:
            
            logger.warning("Errores en los formularios")
            
            errores = []
            # Errores de detalles
            for i, form in enumerate(form_venta_det, start=1):
                for field, field_errors in form.errors.items():
                    for error in field_errors:
                        errores.append(f"Detalle #{i}, Campo [{field}]: {error}")

            #Errores de cabecera
            for field, field_errors in form_venta_cab.errors.items():
                for error in field_errors:
                    errores.append(f"Cabecera, Campo [{field}]: {error}")

            # Ahora mostramos todos
            if errores:
                messages.error(request, "\\n".join(errores))

            logger.debug(f"Errores encontrados: {errores}")
            
        # Mantener los datos del formulario aunque falle validación
        context = {
            'form_venta_cab': form_venta_cab,
            'form_venta_det': form_venta_det,
            'empresa': datos_empresa,
            'form_venta_det_prefix':form_venta_det.prefix
        }
        return render(request, 'ventas/registrar5.html', context)
            
    else:
            
        form_venta_cab = FormRegVentaCabecera(initial={
            'nro_comprobante': numero_formateado,
            'timbrado': config.obtener_timbrado(),
            'fecha_venta': fecha_actual,
            'vendedor': request.user,
        })
        
        form_venta_det = formset_venta(prefix='form')

    context = {
        'form_venta_cab': form_venta_cab,
        'form_venta_det': form_venta_det,
        'empresa': datos_empresa,
        'form_venta_det_prefix':form_venta_det.prefix
    }
    return render(request, 'ventas/registrar5.html', context)



# Función auxiliar para obtener stock actual (debes implementarla según tu modelo)
def obtener_stock_actual(producto):
    """
    Función para obtener el stock actual de un producto.
    Ajusta según tu modelo de datos.
    """
    try:
        # Ejemplo: si tienes un campo stock en el modelo Producto
        print(f"Obteniendo stock para el producto: {producto.nombre}", producto.id, producto.cantidad_en_stock)
        return producto.cantidad_en_stock if hasattr(producto, 'cantidad_en_stock') else 0
        
        # O si calculas stock desde movimientos:
        # from django.db.models import Sum
        # entradas = MovimientoStock.objects.filter(
        #     producto=producto, movimiento='ENTRADA'
        # ).aggregate(Sum('cantidad'))['cantidad__sum'] or 0
        # 
        # salidas = MovimientoStock.objects.filter(
        #     producto=producto, movimiento='SALIDA'
        # ).aggregate(Sum('cantidad'))['cantidad__sum'] or 0
        # 
        # return entradas - salidas
        
    except Exception as e:
        print(f"Error al obtener stock de {producto}: {e}")
        return 0


    
    
@login_required(login_url='login/')
@permission_required('ventas.change_ventacabecera', raise_exception=True)
@permission_required('ventas.change_ventadetalle', raise_exception=True)
@require_http_methods(["GET", "POST"])
def editar_venta_v3(request, id_venta):
    
    venta = get_object_or_404(VentaCabecera, id=id_venta)
    datos_empresa = Empresa.objects.first()
    detalles_originales = VentaDetalle.objects.filter(venta_cab=venta)
    
    formset_venta = formset_factory(FormEditVentaDetalle, extra=0, can_delete=True)

    if request.method == 'POST':
        form_venta_cab = FormEditarVentaCabecera(request.POST, instance=venta)
        form_venta_det = formset_venta(request.POST,prefix='form')

        logger.debug(f"Datos POST recibidos: {dict(request.POST)}")

        if form_venta_cab.is_valid() and form_venta_det.is_valid():
            
            logger.info("Formularios válidos para edición de compra")
            
            detalles_validos = []
            
            for form_det in form_venta_det:
                if form_det.cleaned_data and not form_det.cleaned_data.get('DELETE', False):
                    producto_id = form_det.cleaned_data.get('producto_id')
                    cantidad = form_det.cleaned_data.get('cantidad')
					
                    if producto_id and cantidad:
                        detalles_validos.append(form_det)
                    else:
                        messages.warning(request, "Detalle inválido - campos obligatorios faltantes")
                        logger.warning("Detalle inválido - campos obligatorios faltantes")
            
            logger.info(f"Total de detalles válidos: {len(detalles_validos)}")
            
            
            if len(detalles_validos) == 0:
                messages.warning(request, "Debe ingresar al menos un detalle de venta válido.")
                logger.warning("No se encontraron detalles válidos")
	
                context = {
                    'form_venta_cab': form_venta_cab,
                    'form_venta_det': form_venta_det,
                    'empresa': datos_empresa,
                    'form_venta_det_prefix':form_venta_det.prefix
				}
                return render(request, 'ventas/editar3.html', context)
            
            try:
                with transaction.atomic():
                    # 1. REVERSIÓN: Eliminar movimientos de stock originales
                    for detalle in detalles_originales:
                        registrar_movimiento_stock(
                            producto=detalle.producto,
                            cantidad=detalle.cantidad,
                            movimiento='REV_SAL',  # Nuevo tipo de movimiento
                            descripcion=f"Reverso por edición venta #{venta.id}",
                            fecha_mov_producto=venta.fecha_venta,
                            venta_cab=venta
                        )
                    
                    # 2. Actualizar cabecera
                    cabecera = form_venta_cab.save()
                    
                    # 3. Eliminar detalles antiguos
                    detalles_originales.delete()
                    
                    # 4. Crear nuevos detalles válidos
                    detalles_guardados = 0
                    
                    # 4. Crear nuevos detalles y movimientos
                    for form_det in detalles_validos:
                        
                        logger.debug(f"Procesando detalle para guardar: {form_det.cleaned_data}")

                        producto_id = form_det.cleaned_data.get('producto_id')
                        cantidad = form_det.cleaned_data.get('cantidad')
                        descripcion = form_det.cleaned_data.get('descripcion')
                        unidad_medida = form_det.cleaned_data.get('unidad_medida')
                        precio_venta = form_det.cleaned_data.get('precio_unit_venta')
                        subtotal = form_det.cleaned_data.get('subtotal')
                                                    
                        try:
                            producto_instance = Producto.objects.get(id=producto_id)
                        except Producto.DoesNotExist:
                            messages.error(request, f"Producto con ID {producto_id} no existe. Detalle omitido.")
                            logger.error(f"Producto con ID {producto_id} no existe. Saltando detalle.")
                            continue
                        
                        # Crear nuevo detalle
                        detalle = VentaDetalle(
                            venta_cab=cabecera,
                            producto=producto_instance,
                            cantidad=cantidad,
                            descripcion=descripcion,
                            unidad_medida=unidad_medida,
                            precio_unit_venta=precio_venta,
                            subtotal=subtotal,
                        )
                        detalle.save()
                        detalles_guardados += 1
                    

                        # 5. Registrar movimiento de stock
                        registrar_movimiento_stock(
                            producto=producto_instance,
                            cantidad=cantidad,
                            movimiento='SALIDA',
                            descripcion=f"Venta editada #{cabecera.id}",
                            fecha_mov_producto=cabecera.fecha_venta,
                            venta_cab=cabecera
                        )
                
                    messages.success(request, "Venta actualizada exitosamente")
                    return redirect('list_ventas')
                    
            except Exception as e:
                logger.error(f'Error al actualizar la venta: {str(e)}')
                messages.error(request, f'Error al actualizar la venta: {str(e)}')
                # Aquí podrías agregar un rollback manual si es necesario
        else:
            logger.warning("Errores en los formularios de edición de venta")
            errores = []
            # Errores de detalles
            for i, form in enumerate(form_venta_det, start=1):
                for field, field_errors in form.errors.items():
                    for error in field_errors:
                        errores.append(f"Detalle #{i}, Campo [{field}]: {error}")

            #Errores de cabecera
            for field, field_errors in form_venta_cab.errors.items():
                for error in field_errors:
                    errores.append(f"Cabecera, Campo [{field}]: {error}")

            # Ahora mostramos todos
            if errores:
                messages.error(request, "\\n".join(errores))

            logger.debug(f"Errores encontrados: {errores}")
            
        # Mantener los datos del formulario aunque falle validación
        context = {
            'form_venta_cab': form_venta_cab,
            'form_venta_det': form_venta_det,
            'empresa': datos_empresa,
            'form_venta_det_prefix':form_venta_det.prefix
        }
            
            #messages.error(request, "Error en el formulario. Verifica los datos.")
    else:
        # Preparar datos iniciales para el formulario
        detalle_inicial = [{
            'producto_id': det.producto.id,
            'producto_nombre': det.producto.nombre,
            'producto_iva': det.producto.iva,
            'cantidad': det.cantidad,
            'descripcion': det.descripcion,
            'unidad_medida': det.unidad_medida,
            'precio_unit_venta': det.precio_unit_venta,
            'subtotal': det.subtotal
        } for det in detalles_originales]
        
        form_venta_cab = FormEditarVentaCabecera(instance=venta)
        form_venta_det = formset_venta(initial=detalle_inicial,prefix='form')

    context = {
        'form_venta': form_venta_cab,
        'form_venta_det': form_venta_det,
        'empresa': datos_empresa,
        'form_venta_det_prefix':form_venta_det.prefix
    }
    return render(request, 'ventas/editar3.html', context)

    

@login_required(login_url='login/')
@permission_required('ventas.delete_ventacabecera', raise_exception=True)
@permission_required('ventas.delete_ventadetalle', raise_exception=True)
def inactivar_venta(request, id_venta):
    # Obtener la cabecera de la venta
    venta_cab = get_object_or_404(VentaCabecera, id=id_venta)
    # Obtener los detalles relacionados
    venta_det = venta_cab.detalles.all()

    # Cambiar estado de los detalles de la cabecera
    for item in venta_det:
        print(item)
        item.activo = False
        item.save()

    # Cambiar el estado a inactivo
    venta_cab.activo = False
    venta_cab.save()

    # Mostrar un mensaje de éxito
    messages.success(request, "La venta fue eliminada correctamente.")

    # Redirigir a la lista de ventas
    return redirect('list_ventas')

@login_required(login_url='login/')
#@permission_required('ventas.view_ventacabecera', raise_exception=True)
#@permission_required('ventas.view_ventadetalle', raise_exception=True)
@require_http_methods(["GET"])
def listar_ventas(request):
    ventas = VentaCabecera.objects.prefetch_related('detalles').all()  # Usar related_name definido
    print("Ventas con detalles prefetch_related:")
    for venta in ventas:
        print(f"Venta ID: {venta.id}, Detalles: {list(venta.detalles.all())}")
    context = {'Ventas': ventas}
    return render(request, 'ventas/listar2.html', context)

@require_http_methods(["GET"])
def buscar_productos(request):
    q = request.GET.get('q', '')
    productos = Producto.objects.filter(
        Q(nombre__icontains=q),
        activo=True
    )

    data = []
    for p in productos:
        data.append({
            'id': p.id,
            'nombre': f"{p.nombre}",
            'precio_venta': float(p.precio_venta),  # Cambiar a 'precio_venta' para coincidir con el frontend
            'iva': float(p.iva) if p.iva else 10,
            'unidad_medida': p.unidad_medida,
            'descripcion': p.descripcion[:100] if p.descripcion else p.nombre
        })
    print(data)
    return JsonResponse(data, safe=False)


##################### FIN VENTAS  #######################
@require_http_methods(["GET"])
def reporte_ventas(request):
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    cliente_id = request.GET.get('cliente')
    producto_id = request.GET.get('producto')
    
    ventas = VentaCabecera.objects.filter(activo=True).order_by('-fecha_venta')
    
    # Aplicar filtros
    if fecha_inicio and fecha_fin:
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
        ventas = ventas.filter(fecha_venta__date__range=[fecha_inicio, fecha_fin])
    
    if cliente_id:
        ventas = ventas.filter(cliente_id=cliente_id)
    
    if producto_id:
        # Filtrar ventas que contengan el producto en sus detalles
        ventas = ventas.filter(detalles__producto_id=producto_id).distinct()
    
    # Datos para el gráfico
    datos_grafico = ventas.values('fecha_venta__date').annotate(total_ventas=Sum('total')).order_by('fecha_venta__date')
    
    fechas = [item['fecha_venta__date'].strftime('%d-%m-%Y') for item in datos_grafico]
    montos = [float(item['total_ventas']) for item in datos_grafico]
    
    # Calcular total general
    total_general = ventas.aggregate(
        total=Sum('total')
    )['total'] or 0
    
    # Generar gráfico
    plt.figure(figsize=(10, 5))
    plt.bar(fechas, montos, color='skyblue')
    plt.xlabel('Fecha')
    plt.ylabel('Total Ventas')
    plt.title('Ventas por Día')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Guardar gráfico en buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    grafico_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    
    # Obtener listas de clientes y productos para el formulario
    clientes = Cliente.objects.filter(activo=True)
    productos = Producto.objects.filter(activo=True)
    
    context = {
        'ventas': ventas,
        'grafico': grafico_base64,
        'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d') if fecha_inicio else '',
        'fecha_fin': fecha_fin.strftime('%Y-%m-%d') if fecha_fin else '',
        'total_general': total_general,
        'clientes': clientes,
        'productos': productos,
        'cliente_seleccionado': int(cliente_id) if cliente_id else None,
        'producto_seleccionado': int(producto_id) if producto_id else None,
    }
    
    return render(request, 'reportes/rep_ventas.html', context)


@require_http_methods(["GET"])
def exportar_ventas_pdf(request):
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    cliente_id = request.GET.get('cliente')
    
    ventas = VentaCabecera.objects.filter(activo=True).order_by('-fecha_venta')
    
    if fecha_inicio and fecha_fin:
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
        ventas = ventas.filter(fecha_venta__date__range=[fecha_inicio, fecha_fin])
    
    if cliente_id:
        ventas = ventas.filter(cliente_id=cliente_id)
    
    
    # Calcular total general
    total_general = ventas.aggregate(
        total=Sum('total')
    )['total'] or 0
    
    template_path = 'reportes/rep_ventas_pdf.html'
    context = {
        'ventas': ventas,
        'total_general': total_general,
        'fecha_inicio': fecha_inicio.strftime('%d/%m/%Y') if fecha_inicio else '',
        'fecha_fin': fecha_fin.strftime('%d/%m/%Y') if fecha_fin else '',
    }
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_ventas.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('Error al generar PDF', status=500)
    
    return response
    
@require_http_methods(["GET"])
def rep_ventas_mensual_anual(request):
    # Obtener parámetros
    tipo_reporte = request.GET.get('tipo_reporte', 'mensual')  # 'mensual' o 'anual'
    anio = request.GET.get('anio', datetime.now().year)
    mes = request.GET.get('mes') if tipo_reporte == 'mensual' else None
    
    # Validación básica
    if not anio:
        messages.error(request, 'Debe seleccionar al menos el año')
        return render(request, 'reportes/rep_ventas_mens_anual.html', {})

    # Filtrar ventas
    ventas = VentaCabecera.objects.filter(activo=True)
    
    if tipo_reporte == 'mensual' and mes:
        ventas = ventas.filter(
            fecha_venta__year=anio,
            fecha_venta__month=mes
        )
        grupo = 'fecha_venta__day'
        titulo_grafico = f'Ventas Diarias - {mes}/{anio}'
    else:
        ventas = ventas.filter(fecha_venta__year=anio)
        grupo = 'fecha_venta__month'
        titulo_grafico = f'Ventas Mensuales - Año {anio}'

    # Agrupar datos para el gráfico
    datos_grafico = ventas.values(grupo).annotate(
        total_ventas=Sum('total')
    ).order_by(grupo)

    # Preparar datos para el gráfico
    if tipo_reporte == 'mensual':
        categorias = [f'{item[grupo]}/{mes}' for item in datos_grafico]
    else:
        meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
                 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        categorias = [meses[item[grupo]-1] for item in datos_grafico]
    
    montos = [float(item['total_ventas']) for item in datos_grafico]

    # Generar gráfico
    plt.figure(figsize=(12, 6))
    if tipo_reporte == 'mensual':
        plt.bar(categorias, montos, color='#4CAF50')
    else:
        plt.plot(categorias, montos, marker='o', color='#2196F3', linewidth=2)
    
    plt.title(titulo_grafico, pad=20, fontweight='bold')
    plt.xlabel('Días' if tipo_reporte == 'mensual' else 'Meses')
    plt.ylabel('Total Ventas (Gs)')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Formatear eje Y con separadores de miles
    ax = plt.gca()
    ax.yaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
    
    plt.tight_layout()
    
    # Convertir gráfico a base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=100)
    buffer.seek(0)
    grafico_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()

    # Totales
    total_general = ventas.aggregate(total=Sum('total'))['total'] or 0
    promedio = total_general / len(montos) if len(montos) > 0 else 0

    # Obtener años disponibles para el filtro
    años_disponibles = VentaCabecera.objects.dates('fecha_venta', 'year')

    context = {
        'ventas': ventas,
        'grafico': grafico_base64,
        'total_general': total_general,
        'promedio': promedio,
        'tipo_reporte': tipo_reporte,
        'anio_seleccionado': int(anio),
        'mes_seleccionado': int(mes) if mes else None,
        'años_disponibles': años_disponibles,
        'mostrar_filtro_mes': tipo_reporte == 'mensual',
        'meses' : [(1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'),(4, 'Abril'),(5, 'Mayo'),(6, 'Junio'),(7, 'Julio'),(8, 'Agosto'),(9, 'Setiembre'),(10, 'Octubre'),(11, 'Noviembre'),(12, 'Diciembre')]
    }

    return render(request, 'reportes/rep_ventas_mens_anual.html', context)


@require_http_methods(["GET"])
def exportar_ventas_mensual_anual_pdf(request):
    # Obtener parámetros (los mismos que en la función original)
    tipo_reporte = request.GET.get('tipo_reporte', 'mensual')  # 'mensual' o 'anual'
    anio = request.GET.get('anio', datetime.now().year)
    mes = request.GET.get('mes') if tipo_reporte == 'mensual' else None
    
    # Validación básica
    if not anio:
        messages.error(request, 'Debe seleccionar al menos el año')

    # Filtrar ventas (igual que en la función original)
    ventas = VentaCabecera.objects.filter(activo=True)
    
    if tipo_reporte == 'mensual' and mes:
        ventas = ventas.filter(
            fecha_venta__year=anio,
            fecha_venta__month=mes
        )
        grupo = 'fecha_venta__day'
        titulo_grafico = f'Compras Diarias - {mes}/{anio}'
        periodo = f"{mes}/{anio}"
    else:
        ventas = ventas.filter(fecha_venta__year=anio)
        grupo = 'fecha_venta__month'
        titulo_grafico = f'Compras Mensuales - Año {anio}'
        periodo = f"Año {anio}"

    # Agrupar datos para el gráfico (igual que en la función original)
    datos_grafico = ventas.values(grupo).annotate(
        total_ventas=Sum('total')
    ).order_by(grupo)

    # Preparar datos para el gráfico (igual que en la función original)
    if tipo_reporte == 'mensual':
        categorias = [f'Día {item[grupo]}' for item in datos_grafico]
    else:
        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        categorias = [meses[item[grupo]-1] for item in datos_grafico]
    
    montos = [float(item['total_ventas']) for item in datos_grafico]

    # Generar gráfico (similar a la función original)
    plt.figure(figsize=(10, 5))
    if tipo_reporte == 'mensual':
        plt.bar(categorias, montos, color='#4CAF50')
    else:
        plt.plot(categorias, montos, marker='o', color='#2196F3', linewidth=2)
    
    plt.title(titulo_grafico, pad=20, fontweight='bold')
    plt.xlabel('Días' if tipo_reporte == 'mensual' else 'Meses')
    plt.ylabel('Total Ventas (Gs)')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Formatear eje Y con separadores de miles
    ax = plt.gca()
    ax.yaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
    
    plt.tight_layout()
    
    # Convertir gráfico a base64 para el PDF
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=100)
    buffer.seek(0)
    grafico_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()

    # Totales (igual que en la función original)
    total_general = ventas.aggregate(total=Sum('total'))['total'] or 0
    promedio = total_general / len(montos) if len(montos) > 0 else 0

    # Preparar el contexto para el PDF
    context = {
        'grafico': grafico_base64,
        'tipo_reporte': tipo_reporte,
        'periodo': periodo,
        'total_general': total_general,
        'promedio': promedio,
        'fecha_generacion': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
        'datos': zip(categorias, montos),  # Para la tabla de datos
    }

    # Configurar la respuesta PDF
    template_path = 'reportes/rep_ventas_mens_anual_pdf.html'
    response = HttpResponse(content_type='application/pdf')
    nombre_archivo = f"ventas_{'mensual' if tipo_reporte == 'mensual' else 'anual'}_{anio}"
    if mes:
        nombre_archivo += f"_{mes}"
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}.pdf"'

    # Renderizar el template a PDF
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('Error al generar PDF', status=500)
    
    return response