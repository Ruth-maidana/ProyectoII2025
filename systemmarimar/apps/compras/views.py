from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required,permission_required
from datetime import datetime
from .models import Categoria, OrdenCompraCab, OrdenCompraDet, Producto, Proveedor
from .forms import CategoriaViewForm, CompraCabEditForm, CompraDetForm, FormEditCompraCabecera, FormEditCompraDetalle, FormRegCompraCabecera, FormRegCompraDetalle, ProductoForm, CategoriaForm, CompraFormset, ProductoViewForm, ProveedorEditForm, ProveedorForm, ProveedorViewForm
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.forms import formset_factory, inlineformset_factory
from django.http import HttpResponse
from .models import OrdenCompraCab, Proveedor
from .forms import FiltroComprasForm
from apps.inventarios.utils import registrar_movimiento_stock
from django.db import transaction 
from django.db.models import Q,Sum
import matplotlib.pyplot as plt
import base64
import io
from django.template.loader import get_template
from xhtml2pdf import pisa
import matplotlib
matplotlib.use('Agg')  # Configura el backend para que no requiera GUI
from django.http import JsonResponse
# Create your views here.

"""
Views for handling product and purchase registration in the compras app.
Functions:
	registrar_producto(request):
		Handles the registration of a new product. If the request method is POST and the form is valid, 
		saves the product and redirects to the product list. Otherwise, renders the product registration form.
	registrar_compra(request):
		Handles the registration of a new purchase. If the request method is POST and the form is valid, 
		saves the purchase and redirects to the purchase list. Otherwise, renders the purchase registration form.
"""

@login_required(login_url='login/')
@permission_required('compras.add_categoria', raise_exception=True)
def registrar_categoria(request):
	if request.method == 'POST':
		form = CategoriaForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(request,"Categoria Registrada Exitosamente")
			# Log success message
			print('Entro correctamente')  # Replace with logging if needed
			return redirect('list_categorias')
		else:
			
			print('Hay error')  # Replace with logging if needed
			print(form.errors)
			messages.error(request, '¡Hubo un error al registrar la categoría!')
			# Iterar sobre los errores del formulario
			#for field, errors in form.errors.items():
				#for error in errors:
					#messages.error(request, f"{field}: {error}")
					# Agregar un mensaje de error personalizado para cada campo
					#form.add_error(field, f"Error en el campo '{field}': {error}")
			# Agregar un mensaje general al formulario
			#form.add_error(None, 'Hubo un error al registrar la categoría.')
			#messages.error(request, '¡Hubo un error al registrar la categoría!') # Log error message
	else:
		form = CategoriaForm()
	context = {'form_categoria': form}
	return render(request, 'categorias/registrar.html', context)


@login_required(login_url='login/')
@permission_required('compras.change_categoria', raise_exception=True)
def editar_categoria(request, id_categoria):
	
	# Recuperamos la instancia del proyecto
	categoria = Categoria.objects.get(id=id_categoria)

	if request.method == "GET":
		# Actualizamos el formulario con los datos recibidos
		form = CategoriaForm(instance=categoria)
	else:
		form = CategoriaForm(request.POST,instance=categoria)
		if form.is_valid():
			form.save()
			messages.success(request,"Categoria Modificado Exitosamente")
			return redirect('list_categorias')
		else:
			messages.error(request,("Error, Verifique los campos"))
			print('Hay error')
			print(form.errors)
	context = {'form_categoria': form}
	return render(request, 'categorias/editar.html',context)

@login_required(login_url='login/')
@permission_required('compras.delete_categoria', raise_exception=True)
def inactivar_categoria(request,id_categoria):
	categoria = Categoria.objects.get(id = id_categoria)
	categoria.activo = False
	messages.success(request,"La categoria fue desactivada correctamente")
	categoria.save()
	return redirect('list_categorias')

@login_required(login_url='login/')
@permission_required('compras.view_categoria', raise_exception=True)
def listar_categorias(request):
	categorias = Categoria.objects.all().order_by('id')
	categorias_forms = [
		{'categoria': categoria, 'form': CategoriaViewForm(instance=categoria)}
		for categoria in categorias
	]
	return render(request, 'categorias/listar.html', {'Categorias': categorias, 'categorias_forms': categorias_forms})



#------------------------------------------------------------------------------
@login_required(login_url='login/')
@permission_required('compras.add_producto', raise_exception=True)
def registrar_producto(request):
	if request.method == 'POST':
		form = ProductoForm(request.POST)
		if form.is_valid():
			form.save()
			print('Entro correctamente')
			print(form)
			messages.success(request,"Producto Registrado Exitosamente")
			return redirect('list_productos')
		else:
			messages.error(request, '¡Error al registrar el producto!')
			# Log error message
			print('Hay error')  # Replace with logging if needed
			print(form.errors)
	else:
		form = ProductoForm()
	context = {'form_producto': form}
	return render(request, 'productos/registrar.html', context)


@login_required(login_url='login/')
@permission_required('compras.change_producto', raise_exception=True)
def editar_producto(request, id_producto):
	
	# Recuperamos la instancia del proyecto
	producto = Producto.objects.get(id=id_producto)

	if request.method == "GET":
		# Actualizamos el formulario con los datos recibidos
		form = ProductoForm(instance=producto)
	else:
		form = ProductoForm(request.POST,instance=producto)
		if form.is_valid():
			form.save()
			messages.success(request,"Producto Modificado Exitosamente")
			return redirect('list_productos')
		else:
			messages.error(request,("Error al modificar el producto"))
			print('Hay error')
			print(form.errors)
	context = {'form_producto': form}
	return render(request, 'productos/editar.html',context)


@login_required(login_url='login/')
@permission_required('compras.delete_producto', raise_exception=True)
def inactivar_producto(request,id_producto):
	producto = Producto.objects.get(id = id_producto)
	producto.activo = False
	messages.success(request,"Producto Desactivado Correctamente")
	producto.save()
	return redirect('list_productos')


@login_required(login_url='login/')
@permission_required('compras.view_producto', raise_exception=True)
def listar_productos(request):
	productos = Producto.objects.all().order_by('id')
	productos_forms = [
				{'producto': producto, 'form': ProductoViewForm(instance=producto)}
				for producto in productos
			]
	#producto = Producto.objects.filter(activo=True).order_by('id')
	return render(request, 'productos/listar.html',{'Productos': productos,'productos_forms': productos_forms})

#------------------------------------------------------------------------------
@login_required(login_url='login/')
@permission_required('compras.add_proveedor', raise_exception=True)
def registrar_proveedor(request):
	if request.method == 'POST':
		form = ProveedorForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(request,"Proveedor Registrado Exitosamente")
			print('Entro correctamente')  # Replace with logging if needed
			return redirect('list_proveedores')
		else:
			# Log error message
			print('Hay error')  # Replace with logging if needed
			print(form.errors)
			messages.error(request, '¡Hubo un error al registrar el proveedor!')
	else:
		form = ProveedorForm()
	context = {'form_proveedor': form}
	return render(request, 'proveedor/registrar.html', context)


@login_required(login_url='login/')
@permission_required('compras.change_proveedor', raise_exception=True)
def editar_proveedor(request, id_proveedor):
	
	# Recuperamos la instancia del proyecto
	proveedor = Proveedor.objects.get(id=id_proveedor)

	if request.method == "GET":
		# Actualizamos el formulario con los datos recibidos
		form = ProveedorEditForm(instance=proveedor)
	else:
		form = ProveedorEditForm(request.POST,instance=proveedor)
		if form.is_valid():
			form.save() 
			print(form)
			messages.success(request,"Proveedor Modificado Exitosamente")
			return redirect('list_proveedores')
		else:
			print(form)
			messages.error(request,("Error, Verifique los campos"))
			print('Hay error')
			print(form.errors)
	context = {'form_proveedor': form}
	return render(request, 'proveedor/editar.html',context)

@login_required(login_url='login/')
@permission_required('compras.delete_proveedor', raise_exception=True)
def inactivar_proveedor(request,id_proveedor):
	proveedor = Proveedor.objects.get(id = id_proveedor)
	proveedor.activo=False
	messages.success(request,"Proveedor Desactivado Correctamente")
	proveedor.save()
	return redirect('list_proveedores')


@login_required(login_url='login/')
@permission_required('compras.view_proveedor', raise_exception=True)
def listar_proveedores(request):
	proveedores = Proveedor.objects.all().order_by('id')
	proveedores_forms = [
			{'proveedor': proveedor, 'form': ProveedorViewForm(instance=proveedor)}
			for proveedor in proveedores
		]
	return render(request, 'proveedor/listar.html',{'Proveedores': proveedores,'proveedores_forms': proveedores_forms})


#------------------------------------------------------------------------------

@login_required(login_url='login/')
@permission_required('compras.add_ordencompracab', raise_exception=True)
@permission_required('compras.add_ordencompradet', raise_exception=True)
def registrar_compra_cab_det_version_act_v2(request):
    formset_compra = formset_factory(FormRegCompraDetalle, extra=0, can_delete=True)
    
    print("Entrando a registrar_compra_cab_det_version_act_v2")
    #fecha_actual = datetime.now().date()

    if request.method == 'POST':
        form_compra_cab = FormRegCompraCabecera(request.POST)
        form_compra_det = formset_compra(request.POST)

        # Imprimir los datos enviados al backend
        print("Datos enviados al backend:")
        print(request.POST)
        print("Detalles de la compra:")
        # Imprimir los datos de cada detalle de la venta
        for i, form_det in enumerate(form_compra_det):
            print(f"Form Detalle #{i}: {form_det}")

        if form_compra_cab.is_valid() and form_compra_det.is_valid():
            print("Formularios válidos, procediendo a guardar la compra")
            try:
                with transaction.atomic():
                    # Guardar la cabecera de la venta
                    cabecera = form_compra_cab.save()
                    print(f"Cabecera de compra guardada: {cabecera}")
                    
                    # Guardar los detalles de la venta
                    for form_det in form_compra_det:
                        if form_det.cleaned_data and not form_det.cleaned_data.get('DELETE', False):
                            
                            print("Procesando detalle de compra")
                            
                            producto_id = form_det.cleaned_data.get('producto_id')
                            cantidad = form_det.cleaned_data.get('cantidad')
                            descripcion = form_det.cleaned_data.get('descripcion')
                            unidad_medida = form_det.cleaned_data.get('unidad_medida')
                            precio_compra = form_det.cleaned_data.get('precio_compra')
                            subtotal = form_det.cleaned_data.get('subtotal')
                            producto_instance = Producto.objects.get(id=producto_id)
                            
                            print(f"Producto ID: {producto_id}, Cantidad: {cantidad}, Descripción: {descripcion}, Unidad de Medida: {unidad_medida}, Precio Unitario: {precio_compra}, Subtotal: {subtotal}")
                            
                            detalle = OrdenCompraDet(
								orden_compra_cab=cabecera,
								producto=producto_instance,
								cantidad=cantidad,
								descripcion=descripcion,
								unidad_medida=unidad_medida,
								precio_compra=precio_compra,
								total_producto=subtotal,
							)
                            print(f"Detalle: {detalle}")
                            detalle.save()
                            
                            registrar_movimiento_stock(
								producto=detalle.producto,
								cantidad=detalle.cantidad,
								movimiento='ENTRADA',
								descripcion=f"Compra registrada: {cabecera.nro_comprobante}",
								ajuste=None,
								fecha_mov_producto=cabecera.fecha_compra,
								compra_cab=cabecera,
								venta_cab=None
							)

                    messages.success(request, "Compra registrada exitosamente")
                    
                    return redirect('list_compras')
                
            except Exception as e:
                print(f'Error: {e}')  # Log the error
                messages.error(request, '¡Error al guardar en la base de datos!')
                print('Error de integridad')
            
        else:
            
            errores = []
            # Errores de detalles
            for i, form in enumerate(form_compra_det, start=1):
                for field, field_errors in form.errors.items():
                    for error in field_errors:
                        errores.append(f"Detalle #{i}, Campo [{field}]: {error}")

            #Errores de cabecera
            for field, field_errors in form_compra_cab.errors.items():
                for error in field_errors:
                    errores.append(f"Cabecera, Campo [{field}]: {error}")

            # Ahora mostramos todos
            if errores:
                messages.error(request, "\\n".join(errores))

            print("Errores","\\n".join(errores))
            

            context = {
				'form_compra_cab': form_compra_cab,
				'form_compra_det': form_compra_det,
				'form_compra_det_prefix': form_compra_det.prefix  # Pasar el prefijo al template
			}
            
            return render(request, 'compras/registrar3.html', context)
            
    else:
            
        form_compra_cab = FormRegCompraCabecera()
        form_compra_det = formset_compra()

    context = {
        'form_compra_cab': form_compra_cab,
        'form_compra_det': form_compra_det,
        'form_compra_det_prefix': form_compra_det.prefix  # Pasar el prefijo al template
    }
    return render(request, 'compras/registrar3.html', context)



@login_required(login_url='login/')
@permission_required('compras.change_ordencompracab', raise_exception=True)
@permission_required('compras.change_ordencompradet', raise_exception=True)
def editar_compra(request,id_compra):
    
    compra = get_object_or_404(OrdenCompraCab, id=id_compra)
    detalles_originales = OrdenCompraDet.objects.filter(orden_compra_cab=compra)
    
    formset_compra = formset_factory(FormEditCompraDetalle, extra=0, can_delete=True)
    
    print("Entrando a registrar_compra_cab_det_version_act_v2")
    #fecha_actual = datetime.now().date()

    if request.method == 'POST':
        form_compra_cab = FormEditCompraCabecera(request.POST,instance=compra)
        form_compra_det = formset_compra(request.POST)

        # Imprimir los datos enviados al backend
        print("Datos enviados al backend:")
        print(request.POST)
        print("Detalles de la compra:")
        # Imprimir los datos de cada detalle de la venta
        for i, form_det in enumerate(form_compra_det):
            print(f"Form Detalle #{i}: {form_det}")

        if form_compra_cab.is_valid() and form_compra_det.is_valid():
            print("Formularios válidos, procediendo a guardar la compra")
            try:
                with transaction.atomic():
                    
                    for detalle in detalles_originales:
                        registrar_movimiento_stock(
								producto=detalle.producto,
								cantidad=detalle.cantidad,
								movimiento='REV_ENT',
								descripcion=f"Reverso por edición compra: {compra.nro_comprobante}",
								fecha_mov_producto=compra.fecha_compra,
								compra_cab=compra
							)
                        
                    # 2. Actualizar cabecera
                    cabecera = form_compra_cab.save()
                    
                    # 3. Eliminar detalles antiguos
                    detalles_originales.delete() 
                    
                    # 4. Crear nuevos detalles y movimientos
                    for form_det in form_compra_det:
                        if form_det.cleaned_data and not form_det.cleaned_data.get('DELETE', False):
                            
                            print("Procesando modificacion del detalle de la compra")
                            
                            producto_id = form_det.cleaned_data.get('producto_id')
                            cantidad = form_det.cleaned_data.get('cantidad')
                            descripcion = form_det.cleaned_data.get('descripcion')
                            unidad_medida = form_det.cleaned_data.get('unidad_medida')
                            precio_compra = form_det.cleaned_data.get('precio_compra')
                            subtotal = form_det.cleaned_data.get('subtotal')
                            producto_instance = Producto.objects.get(id=producto_id)
                            
                            print(f"Producto ID: {producto_id}, Cantidad: {cantidad}, Descripción: {descripcion}, Unidad de Medida: {unidad_medida}, Precio Unitario: {precio_compra}, Subtotal: {subtotal}")
                            print(f"Creando nuevo detalle")
                            
                            detalle = OrdenCompraDet(
								orden_compra_cab=cabecera,
								producto=producto_instance,
								cantidad=cantidad,
								descripcion=descripcion,
								unidad_medida=unidad_medida,
								precio_compra=precio_compra,
								total_producto=subtotal,
							)
                          
                            detalle.save()
                            
                            # 5. Registrar movimiento de stock
                            print(f"Registrando movimiento de stock: Producto:{producto_instance.nombre}, Cantidad: {cantidad}")
                            registrar_movimiento_stock(
								producto=producto_instance,
								cantidad=cantidad,
								movimiento='ENTRADA',
								descripcion=f"Compra editada: #{cabecera.nro_comprobante}",
								ajuste=None,
								fecha_mov_producto=cabecera.fecha_compra,
								compra_cab=cabecera,
								venta_cab=None
							)

                    messages.success(request, "Compra editada exitosamente")
                    
                    return redirect('list_compras')
                
            except Exception as e:
                print(f'Error: {e}')  # Log the error
                messages.error(request, '¡Error al guardar en la base de datos!')
                print('Error de integridad')
            
        else:
            print("Formularios no válidos, mostrando errores")
            print("-----------------------------------------")
            print("Errores de cabecera:")
            print(form_compra_cab.errors)
            print("Errores de detalles:")
            for form_det in form_compra_det:
                print(form_det.errors)

            messages.error(request, '¡Hubo un error al registrar la compra!')
            #print('Prefix', form_compra_det.prefix)  # Imprimir el prefijo del formset para depuración
            
            context = {
				'form_compra_cab': form_compra_cab,
				'form_compra_det': form_compra_det,
				'form_compra_det_prefix': form_compra_det.prefix  # Pasar el prefijo al template
			}
            
            return render(request, 'compras/editar3.html', context)
            
    else:
        
        # Preparar datos iniciales para el formulario
        detalle_inicial = [{
            'producto_id': det.producto.id,
            'producto_nombre': det.producto.nombre,
            'producto_iva': det.producto.iva,
            'cantidad': det.cantidad,
            'descripcion': det.descripcion,
            'unidad_medida': det.unidad_medida,
            'precio_compra': det.precio_compra,
            'subtotal': det.total_producto
        } for det in detalles_originales]
            
        form_compra_cab = FormEditCompraCabecera(instance=compra)
        form_compra_det = formset_compra(initial=detalle_inicial)

    context = {
        'form_compra_cab': form_compra_cab,
        'form_compra_det': form_compra_det,
        'form_compra_det_prefix': form_compra_det.prefix  # Pasar el prefijo al template
    }
    return render(request, 'compras/editar3.html', context)


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
            'precio_compra': float(p.precio_compra),  # Cambiar a 'precio_compra' para coincidir con el frontend
            'iva': float(p.iva) if p.iva else 10,
            'unidad_medida': p.unidad_medida,
            'descripcion': p.descripcion[:100] if p.descripcion else p.nombre
        })
    print(data)
    return JsonResponse(data, safe=False)

def obtener_datos_producto(request):
    producto_id = request.GET.get('producto_id')
    try:
        producto = Producto.objects.get(pk=producto_id)
        data = {
            'precio_compra': str(producto.precio_compra),
            'unidad_medida_id': producto.unidad_medida.id if producto.unidad_medida else '',
            'descripcion': producto.descripcion or ''
        }
        return JsonResponse(data)
    except Producto.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)



@login_required(login_url='login/')
@permission_required('compras.delete_ordencompracab', raise_exception=True)
@permission_required('compras.delete_ordencompradet', raise_exception=True)
def inactivar_compra(request, id_compra):
	# Obtener la cabecera de la compra
	compra_cab = get_object_or_404(OrdenCompraCab, id=id_compra)
	
	# Cambiar el estado a inactivo
	compra_cab.estado = False
	compra_cab.save()
	
	# Mostrar un mensaje de éxito
	messages.success(request, "La compra fue inactivada correctamente.")
	
	# Redirigir a la lista de compras
	return redirect('list_compras')


@login_required(login_url='login/')
@permission_required('compras.view_ordencompracab', raise_exception=True)
def listar_compras(request):
	compras = OrdenCompraCab.objects.prefetch_related('ordencompradet_set').all()  # Cargar detalles relacionados
	context = {'Compras': compras}
	return render(request, 'compras/listar.html', context)


def reporte_compras(request):
	fecha_inicio = request.GET.get('fecha_inicio')
	fecha_fin = request.GET.get('fecha_fin')
	proveedor_id = request.GET.get('proveedor')  # Cambiado de 'cliente' a 'proveedor'
	
	compras = OrdenCompraCab.objects.filter(activo=True).order_by('-fecha_compra')
	
	# Aplicar filtros
	if fecha_inicio and fecha_fin:
		fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
		fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
		compras = compras.filter(fecha_compra__date__range=[fecha_inicio, fecha_fin])
	
	if proveedor_id:
		compras = compras.filter(proveedor_id=proveedor_id)

	# Datos para el gráfico
	datos_grafico = compras.values('fecha_compra__date').annotate(total_compras=Sum('total')).order_by('fecha_compra__date')
	
	fechas = [item['fecha_compra__date'].strftime('%d-%m-%Y') for item in datos_grafico]
	montos = [float(item['total_compras']) for item in datos_grafico]
	
	# Calcular total general
	total_general = compras.aggregate(
		total=Sum('total')
	)['total'] or 0
	
	# Generar gráfico
	plt.figure(figsize=(10, 5))
	plt.bar(fechas, montos, color='skyblue')
	plt.xlabel('Fecha')
	plt.ylabel('Total Compras')  # Corregido de 'Ventas' a 'Compras'
	plt.title('Compras por Día')  # Corregido de 'Ventas' a 'Compras'
	plt.xticks(rotation=45)
	plt.tight_layout()
	
	# Guardar gráfico en buffer
	buffer = io.BytesIO()
	plt.savefig(buffer, format='png')
	buffer.seek(0)
	grafico_base64 = base64.b64encode(buffer.read()).decode('utf-8')
	plt.close()
	
	# Obtener lista de proveedores para el formulario
	proveedores = Proveedor.objects.filter(activo=True)
	
	context = {
		'compras': compras,
		'grafico': grafico_base64,
		'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d') if fecha_inicio else '',
		'fecha_fin': fecha_fin.strftime('%Y-%m-%d') if fecha_fin else '',
		'total_general': total_general,
		'proveedores': proveedores,  # Corregido: variable en lugar de string
		'proveedor_seleccionado': int(proveedor_id) if proveedor_id else None,
	}
	
	return render(request, 'reportes/rep_compras.html', context)



def exportar_compras_pdf(request):
	fecha_inicio = request.GET.get('fecha_inicio')
	fecha_fin = request.GET.get('fecha_fin')
	proveedor_id = request.GET.get('proveedor')
	
	compras = OrdenCompraCab.objects.filter(activo=True).order_by('-fecha_compra')
	
	# Aplicar filtros
	if fecha_inicio and fecha_fin:
		fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
		fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
		compras = compras.filter(fecha_compra__date__range=[fecha_inicio, fecha_fin])
	
	if proveedor_id:
		compras = compras.filter(proveedor_id=proveedor_id)
	
	# Calcular total general
	total_general = compras.aggregate(
		total=Sum('total')
	)['total'] or 0
	
	template_path = 'reportes/rep_compras_pdf.html'
	context = {
		'compras': compras,
		'total_general': total_general,
		'fecha_inicio': fecha_inicio.strftime('%d/%m/%Y') if fecha_inicio else '',
		'fecha_fin': fecha_fin.strftime('%d/%m/%Y') if fecha_fin else '',
	}
	
	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = 'attachment; filename="reporte_compras.pdf"'
	
	template = get_template(template_path)
	html = template.render(context)
	
	pisa_status = pisa.CreatePDF(html, dest=response)
	
	if pisa_status.err:
		return HttpResponse('Error al generar PDF', status=500)
	
	return response


def rep_compras_mensual_anual_v2(request):
    # Obtener parámetros
    tipo_reporte = request.GET.get('tipo_reporte', 'mensual')  # 'mensual' o 'anual'
    anio = request.GET.get('anio', datetime.now().year)
    mes = request.GET.get('mes') if tipo_reporte == 'mensual' else None
    
    # Validación básica
    if not anio:
        messages.error(request, 'Debe seleccionar al menos el año')
        return render(request, 'reportes/rep_compras_mens_anual.html', {})

    # Filtrar compras
    compras = OrdenCompraCab.objects.filter(activo=True)
    
    if tipo_reporte == 'mensual' and mes:
        compras = compras.filter(
            fecha_compra__year=anio,
            fecha_compra__month=mes
        )
        grupo = 'fecha_compra__day'
        titulo_grafico = f'Compras Diarias - {mes}/{anio}'
    else:
        compras = compras.filter(fecha_compra__year=anio)
        grupo = 'fecha_compra__month'
        titulo_grafico = f'Compras Mensuales - Año {anio}'

    # Agrupar datos para el gráfico
    datos_grafico = compras.values(grupo).annotate(
        total_compras=Sum('total')
    ).order_by(grupo)

    # Preparar datos para el gráfico
    if tipo_reporte == 'mensual':
        categorias = [f'Día {item[grupo]}' for item in datos_grafico]
    else:
        meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
                 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        categorias = [meses[item[grupo]-1] for item in datos_grafico]
    
    montos = [float(item['total_compras']) for item in datos_grafico]

    # Generar gráfico solo si hay datos
    grafico_base64 = None
    if categorias and montos:
        plt.figure(figsize=(12, 6))
        
        if tipo_reporte == 'mensual':
            plt.bar(categorias, montos, color='#4CAF50')
        else:
            plt.plot(categorias, montos, marker='o', color='#2196F3', linewidth=2)
        
        plt.title(titulo_grafico, pad=20, fontweight='bold')
        plt.xlabel('Días' if tipo_reporte == 'mensual' else 'Meses')
        plt.ylabel('Total Compras (Gs)')
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
    total_general = compras.aggregate(total=Sum('total'))['total'] or 0
    promedio = total_general / len(montos) if len(montos) > 0 else 0

    # Obtener años disponibles para el filtro
    años_disponibles = OrdenCompraCab.objects.dates('fecha_compra', 'year')

    context = {
        'compras': compras,
        'grafico': grafico_base64,
        'total_general': total_general,
        'promedio': promedio,
        'tipo_reporte': tipo_reporte,
        'anio_seleccionado': int(anio),
        'mes_seleccionado': int(mes) if mes else None,
        'años_disponibles': años_disponibles,
        'mostrar_filtro_mes': tipo_reporte == 'mensual',
        'meses': [(1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'), 
                 (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'),
                 (9, 'Setiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre')]
    }

    return render(request, 'reportes/rep_compras_mens_anual.html', context)


def exportar_compras_mensual_anual_pdf(request):
    # Obtener parámetros (los mismos que en la función original)
    tipo_reporte = request.GET.get('tipo_reporte', 'mensual')  # 'mensual' o 'anual'
    anio = request.GET.get('anio', datetime.now().year)
    mes = request.GET.get('mes') if tipo_reporte == 'mensual' else None
    
    # Validación básica
    if not anio:
        messages.error(request, 'Debe seleccionar al menos el año')
        #return render(request, 'reportes/rep_compras_mens_anual.html', {})

    # Filtrar compras (igual que en la función original)
    compras = OrdenCompraCab.objects.filter(activo=True)
    
    if tipo_reporte == 'mensual' and mes:
        compras = compras.filter(
            fecha_compra__year=anio,
            fecha_compra__month=mes
        )
        grupo = 'fecha_compra__day'
        titulo_grafico = f'Compras Diarias - {mes}/{anio}'
        periodo = f"{mes}/{anio}"
    else:
        compras = compras.filter(fecha_compra__year=anio)
        grupo = 'fecha_compra__month'
        titulo_grafico = f'Compras Mensuales - Año {anio}'
        periodo = f"Año {anio}"

    # Agrupar datos para el gráfico (igual que en la función original)
    datos_grafico = compras.values(grupo).annotate(
        total_compras=Sum('total')
    ).order_by(grupo)

    # Preparar datos para el gráfico (igual que en la función original)
    if tipo_reporte == 'mensual':
        categorias = [f'Día {item[grupo]}' for item in datos_grafico]
    else:
        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        categorias = [meses[item[grupo]-1] for item in datos_grafico]
    
    montos = [float(item['total_compras']) for item in datos_grafico]

    # Generar gráfico (similar a la función original)
    plt.figure(figsize=(10, 5))
    if tipo_reporte == 'mensual':
        plt.bar(categorias, montos, color='#4CAF50')
    else:
        plt.plot(categorias, montos, marker='o', color='#2196F3', linewidth=2)
    
    plt.title(titulo_grafico, pad=20, fontweight='bold')
    plt.xlabel('Días' if tipo_reporte == 'mensual' else 'Meses')
    plt.ylabel('Total Compras (Gs)')
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
    total_general = compras.aggregate(total=Sum('total'))['total'] or 0
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
    template_path = 'reportes/rep_compras_mens_anual_pdf.html'
    response = HttpResponse(content_type='application/pdf')
    nombre_archivo = f"compras_{'mensual' if tipo_reporte == 'mensual' else 'anual'}_{anio}"
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