from django.shortcuts import render, redirect

from .models import Categoria, OrdenCompraCab, OrdenCompraDet, Producto, Proveedor
from .forms import CategoriaViewForm, CompraCabEditForm, CompraCabForm, CompraDetForm, ProductoForm, CategoriaForm, CompraFormset, ProductoViewForm, ProveedorEditForm, ProveedorForm, ProveedorViewForm
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.forms import inlineformset_factory
from django.http import HttpResponse
#from django.template.loader import render_to_string
#from weasyprint import HTML
#import pandas as pd
#from django.db.models import Q
from .models import OrdenCompraCab, Proveedor
from .forms import FiltroComprasForm
from apps.inventarios.utils import registrar_movimiento_stock
from django.db import transaction 

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

def inactivar_categoria(request,id_categoria):
	categoria = Categoria.objects.get(id = id_categoria)
	categoria.activo = False
	messages.success(request,"La categoria fue desactivada correctamente")
	categoria.save()
	return redirect('list_categorias')

def listar_categorias(request):
	categorias = Categoria.objects.all().order_by('id')
	categorias_forms = [
		{'categoria': categoria, 'form': CategoriaViewForm(instance=categoria)}
		for categoria in categorias
	]
	return render(request, 'categorias/listar.html', {'Categorias': categorias, 'categorias_forms': categorias_forms})



#------------------------------------------------------------------------------
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


#@login_required(login_url='/login_user')
#@permission_required('producto.change_producto', raise_exception=True)
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


def inactivar_producto(request,id_producto):
	producto = Producto.objects.get(id = id_producto)
	producto.activo = False
	messages.success(request,"Producto Desactivado Correctamente")
	producto.save()
	return redirect('list_productos')

def listar_productos(request):
	productos = Producto.objects.all().order_by('id')
	productos_forms = [
				{'producto': producto, 'form': ProductoViewForm(instance=producto)}
				for producto in productos
			]
	#producto = Producto.objects.filter(activo=True).order_by('id')
	return render(request, 'productos/listar.html',{'Productos': productos,'productos_forms': productos_forms})

#------------------------------------------------------------------------------

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

def inactivar_proveedor(request,id_proveedor):
	proveedor = Proveedor.objects.get(id = id_proveedor)
	proveedor.activo=False
	messages.success(request,"Proveedor Desactivado Correctamente")
	proveedor.save()
	return redirect('list_proveedores')

def listar_proveedores(request):
	proveedores = Proveedor.objects.all().order_by('id')
	proveedores_forms = [
			{'proveedor': proveedor, 'form': ProveedorViewForm(instance=proveedor)}
			for proveedor in proveedores
		]
	return render(request, 'proveedor/listar.html',{'Proveedores': proveedores,'proveedores_forms': proveedores_forms})


#------------------------------------------------------------------------------

'''def registrar_compra_cab_det(request):

	if request.method == 'POST':
		form_cab = CompraCabForm(request.POST)
		#form_det = CompraDetForm(request.POST)
		formset = CompraFormset(request.POST)
		if form_cab.is_valid() and formset.is_valid():
			#compra_cab = form_cab.save(commit=False)
			#for obj_compra_cab in compra_cab:
			compra = form_cab.save()
			formset.instance = compra
			formset.save()

			registrar_stock_entrada(formset.instance)
			print('Entro correctamente')
			print(formset)

				
				#formset.instance = obj_compra_cab
				#obj_compra_cab.save()
				#formset.save()
				
				#compra_det.instance.cabecera = compra_cab
				#compra_det.save()
			#formset.save()
			#return redirect('lista_compras')
			messages.success(request,"Compra Registrado Exitosamente")
			return redirect('list_compras')
		else:
			print('Hay error')
			print(form_cab.errors)
			print(formset.errors)
			messages.error(request, '¡Hubo un error al registrar la compra!')
	else:
		form_cab = CompraCabForm()
		formset = CompraFormset()
	context = {
		'form_compra': form_cab,
		'form_det_compra': formset}
	return render(request, 'compras/registrar2.html', context)'''



def registrar_compra_cab_det_version_act(request):

	if request.method == 'POST':
		form_cab = CompraCabForm(request.POST)
		#form_det = CompraDetForm(request.POST)
		formset = CompraFormset(request.POST)
		if form_cab.is_valid() and formset.is_valid():
			try:
				with transaction.atomic():
        
					# Guardar la cabecera de la compra
					compra = form_cab.save()

					# Guardar los detalles de la compra
					instances = formset.save(commit=False)
					for detalle in instances:
						detalle.orden_compra_cab = compra
						detalle.save()
						
						# Registrar el movimiento de stock
						registrar_movimiento_stock(
							producto=detalle.producto,
							cantidad=detalle.cantidad,
							movimiento='ENTRADA',
							descripcion=f"Compra registrada: {compra.nro_comprobante}",
							ajuste=None,
							fecha_mov_producto=compra.fecha_compra,
       						compra_cab=compra
						)
      
					messages.success(request,"Compra Registrado Exitosamente")
					return redirect('list_compras')
 
			except Exception as e:
				print(f'Error: {e}')  # Log the error
				messages.error(request, '¡Error al guardar en la base de datos!')
				print('Error de integridad')
		else:
			messages.error(request, '¡Hubo errores en el formulario!')
			print(form_cab.errors, formset.errors)
	  
	else:
		form_cab = CompraCabForm()
		formset = CompraFormset()
	context = {
		'form_compra': form_cab,
		'form_det_compra': formset}
	return render(request, 'compras/registrar2.html', context)


def editar_compra(request, id_compra):
	# Obtener la cabecera de la compra
	compra = get_object_or_404(OrdenCompraCab, id=id_compra)

	# Crear un formset para los detalles de la compra
	CompraFormset = inlineformset_factory(
		OrdenCompraCab,
		OrdenCompraDet,
		form=CompraDetForm,
		extra=0,  # No agregar filas adicionales por defecto
		can_delete=True  # Permitir eliminar detalles
	)

	if request.method == 'POST':
		form_cab = CompraCabEditForm(request.POST, instance=compra)
		formset = CompraFormset(request.POST, instance=compra)

		if form_cab.is_valid() and formset.is_valid():
			# Guardar la cabecera y los detalles
			form_cab.save()
			formset.save()
			messages.success(request, "¡La compra fue actualizada exitosamente!")
			return redirect('list_compras')  # Redirigir a la lista de compras
		else:
			print('Hay error')
			print(form_cab)
			print(formset)
			messages.error(request, "¡Hubo un error al actualizar la compra! Verifica los datos ingresados.")
	else:
		form_cab = CompraCabEditForm(instance=compra)
		formset = CompraFormset(instance=compra)

	context = {
		'form_compra': form_cab,
		'form_det_compra': formset,
	}
	return render(request, 'compras/editar2.html', context)


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


def listar_compras(request):
	compras = OrdenCompraCab.objects.prefetch_related('ordencompradet_set').all()  # Cargar detalles relacionados
	context = {'Compras': compras}
	return render(request, 'compras/listar.html', context)


'''
def manage_books(request, author_id):
	author = Author.objects.get(pk=author_id)
	BookInlineFormSet = inlineformset_factory(Author, Book, fields=["title"])
	if request.method == "POST":
		formset = BookInlineFormSet(request.POST, request.FILES, instance=author)
		if formset.is_valid():
			formset.save()
			# Do something. Should generally end with a redirect. For example:
			return HttpResponseRedirect(author.get_absolute_url())
	else:
		formset = BookInlineFormSet(instance=author)
	return render(request, "manage_books.html", {"formset": formset})


var = var_form(commit = False)
var.product = product.title
var.save()
'''

'''
def export_pdf(request):
	# Filter purchases based on request parameters (e.g., date range, provider)
	compras = OrdenCompraCab.objects.prefetch_related('ordencompradet_set').all()  # Replace with actual filtering logic

	# Render the purchases to an HTML template
	html_string = render_to_string('compras/reporte_pdf.html', {'compras': compras})
	html = HTML(string=html_string)

	# Generate PDF
	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = 'inline; filename="reporte_compras.pdf"'
	html.write_pdf(response)
	return response

def export_excel(request):
	# Filter purchases based on request parameters (e.g., date range, provider)
	compras = OrdenCompraCab.objects.prefetch_related('ordencompradet_set').all()  # Replace with actual filtering logic

	# Create a DataFrame for Excel export
	data = []
	for compra in compras:
		for detalle in compra.ordencompradet_set.all():
			data.append({
				'Nro. Comprobante': compra.nro_comprobante,
				'Fecha Compra': compra.fecha_compra,
				'Proveedor': compra.proveedor.razon_social,
				'Forma de Pago': compra.forma_pago,
				'Producto': detalle.producto.nombre,
				'Cantidad': detalle.cantidad,
				'Precio Unitario': detalle.precio_compra,
				'Descuento': detalle.descuento,
				'Total Producto': detalle.total_producto,
			})

	df = pd.DataFrame(data)

	# Generate Excel file
	response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
	response['Content-Disposition'] = 'attachment; filename="reporte_compras.xlsx"'
	with pd.ExcelWriter(response, engine='openpyxl') as writer:
		df.to_excel(writer, index=False, sheet_name='Compras')
	return response


def listar_compras(request):
	form = FiltroComprasForm(request.GET or None)
	compras = OrdenCompraCab.objects.all()

	if form.is_valid():
		fecha_inicio = form.cleaned_data.get('fecha_inicio')
		fecha_fin = form.cleaned_data.get('fecha_fin')
		proveedor = form.cleaned_data.get('proveedor')

		if fecha_inicio and fecha_fin:
			compras = compras.filter(fecha_compra__range=(fecha_inicio, fecha_fin))
		if proveedor:
			compras = compras.filter(proveedor=proveedor)

	return render(request, 'compras/listar.html', {'form': form, 'compras': compras})
'''