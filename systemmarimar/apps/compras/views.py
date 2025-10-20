#from venv import logger
import logging
from time import timezone
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required,permission_required
from datetime import datetime
from .models import Categoria, OrdenCompraCab, OrdenCompraDet, Producto, Proveedor
from .forms import CategoriaViewForm, FormEditCompraCabecera, FormEditCompraDetalle, FormRegCompraCabecera, FormRegCompraDetalle, ProductoForm, CategoriaForm, ProductoViewForm, ProveedorForm, ProveedorViewForm
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.forms import ValidationError, formset_factory, inlineformset_factory
from django.http import HttpResponse
from .models import OrdenCompraCab, Proveedor
from apps.inventarios.utils import registrar_movimiento_stock
from django.db import IntegrityError, transaction 
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

logger = logging.getLogger(__name__)


@login_required(login_url='login/')
@permission_required('compras.add_categoria', raise_exception=True)
def registrar_categoria(request):
	if request.method == 'POST':
		form = CategoriaForm(request.POST)
		if form.is_valid():
			try:
				with transaction.atomic():
					# Guardar la categoría
					categoria = form.save()
					messages.success(
						request, 
						f"Categoría creada correctamente"
					)
	 
					logger.info(f"Categoría creada: {categoria.nombre}")
	 
					return redirect('list_categorias')
 
			except ValidationError as e:
				messages.error(request, str(e))
	
			except Exception as e:
				messages.error(request, "Error interno del servidor")
				logger.error(f"Error al crear categoría: {e}")
		else:
			messages.error(request, 'Error en el formulario al crear categoría')
	else:
		form = CategoriaForm()
  
	context = {'form_categoria': form}
	return render(request, 'categorias/registrar.html', context)


@login_required(login_url='login/')
@permission_required('compras.change_categoria', raise_exception=True)
def editar_categoria(request, id_categoria):
	
	# Recuperamos la instancia del proyecto
	categoria = get_object_or_404(Categoria, id=id_categoria)

	if request.method == "GET":
		# Actualizamos el formulario con los datos recibidos
		form = CategoriaForm(instance=categoria)
	else:
		form = CategoriaForm(request.POST,instance=categoria)
		if form.is_valid():
			try:
				with transaction.atomic():
					categoria_actualizada = form.save()
					messages.success(
						request, 
						f"Categoría '{categoria_actualizada.nombre}' actualizada correctamente"
					)
	 
					logger.info(f"Categoría actualizada: {categoria_actualizada.nombre}")
	 
					return redirect('list_categorias')
 
			except ValidationError as e:
				messages.error(request, str(e))
	
			except Exception as e:
				messages.error(request, "Error interno del servidor")
				logger.error(f"Error al actualizar categoría {id_categoria}: {e}")
		else:
			messages.error(request, 'Por favor corrija los errores del formulario')
	context = {'form_categoria': form}
	return render(request, 'categorias/editar.html',context)

@login_required(login_url='login/')
@permission_required('compras.delete_categoria', raise_exception=True)
def inactivar_categoria(request,id_categoria):
	"""
	Desactiva una categoría si no tiene productos asignados.
	
	Args:
		request: HttpRequest object
		id_categoria: ID de la categoría a desactivar
		
	Returns:
		HttpResponse: Redirect a la lista de categorías
	"""
	categoria = get_object_or_404(Categoria, id=id_categoria)
	
 	#categoria = Categoria.objects.get(id = id_categoria)

	'''categoria.activo = False
	messages.success(request,"La categoria fue desactivada correctamente")
	categoria.save()'''
 
	if not categoria.activo:
		messages.info(request, f"La categoría ya está inactiva.")
		return redirect('list_categorias')

	# Validar ANTES de intentar guardar
	productos_activos = categoria.producto_set.filter(activo=True)
	productos_count = productos_activos.count()
 
	if productos_count > 0:
		messages.error(
			request, 
			f"No se puede desactivar la categoría "
			f"porque tiene producto(s) asignado(s)."
		)
		logger.warning(f"Intento de desactivar categoría con productos: {categoria.nombre}")
		return redirect('list_categorias')
 
	try:
		with transaction.atomic():
			categoria.activo = False
			categoria.save()  # Aquí se ejecuta clean() automáticamente
			
			messages.success(
				request, 
				f"La categoría fue desactivada correctamente"
			)
			logger.info(f"Categoría desactivada exitosamente: {categoria.nombre}")
			  
	except Exception as general_error:
		messages.error(request, "Error interno del servidor. Intente nuevamente.")
		logger.error(f"Error inesperado al desactivar categoría {id_categoria}: {general_error}")
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
	'''
	Vista para registrar un nuevo producto
	'''
	if request.method == 'POST':
		form = ProductoForm(request.POST)
  
		if form.is_valid():
			try:
				producto = form.save()
				logger.info(f"Producto '{producto.nombre}' registrado exitosamente por usuario {request.user}")
				messages.success(request, f"Producto registrado exitosamente")
				return redirect('list_productos')
			
			except IntegrityError as e:
				logger.error(f"Error de integridad al registrar producto: {str(e)}")
				if 'unique constraint' in str(e).lower():
					messages.error(request, "Ya existe un producto con ese nombre")
				else:
					messages.error(request, "Error al registrar el producto. Verifique los datos.")
			
			except ValidationError as e:
				logger.error(f"Error de validación al registrar producto: {str(e)}")
				messages.error(request, f"Error de validación: {str(e)}")
			
			except Exception as e:
				logger.error(f"Error inesperado al registrar producto: {str(e)}")
				messages.error(request, "Error inesperado al registrar el producto")
				
		else:
			logger.warning(f"Formulario inválido para registro de producto: {form.errors}")
			messages.error(request, "Error en el formulario al registrar producto")
			
			# Agregar errores específicos a los messages
			#for field, errors in form.errors.items():
				#for error in errors:
					#messages.error(request, f"{field}: {error}")
	else:
		form = ProductoForm()
	context = {'form_producto': form}
	return render(request, 'productos/registrar.html', context)


@login_required(login_url='login/')
@permission_required('compras.change_producto', raise_exception=True)
def editar_producto(request, id_producto):
	"""
	Vista para editar un producto existente
	"""
 
	# Usar get_object_or_404 para mejor manejo de errores
	producto = get_object_or_404(Producto, id=id_producto)
	
	# Verificar si el producto está activo (opcional)
	if not producto.activo:
		messages.warning(request, "Este producto está desactivado")
		
	if request.method == "GET":
		# Actualizamos el formulario con los datos recibidos
		form = ProductoForm(instance=producto)
	else:
		form = ProductoForm(request.POST, instance=producto)
		if form.is_valid():
			try:
				producto_actualizado = form.save()
				logger.info(f"Producto '{producto_actualizado.nombre}' modificado exitosamente por usuario {request.user}")
				messages.success(request, f"Producto modificado exitosamente")
				return redirect('list_productos')
				
			except IntegrityError as e:
				logger.error(f"Error de integridad al modificar producto {id_producto}: {str(e)}")
				if 'unique constraint' in str(e).lower():
					messages.error(request, "Ya existe un producto con ese nombre")
				else:
					messages.error(request, "Error al modificar el producto. Verifique los datos.")
				
			except ValidationError as e:
				logger.error(f"Error de validación al modificar producto {id_producto}: {str(e)}")
				messages.error(request, f"Error de validación: {str(e)}")
				
			except Exception as e:
				logger.error(f"Error inesperado al modificar producto {id_producto}: {str(e)}")
				messages.error(request, "Error inesperado al modificar el producto")
			
		else:
			logger.warning(f"Formulario inválido para edición de producto {id_producto}: {form.errors}")
			messages.error(request, "Por favor corrige los errores en el formulario")
			
			# Agregar errores específicos a los messages
			for field, errors in form.errors.items():
				for error in errors:
					messages.error(request, f"{field}: {error}")
	 
	context = {'form_producto': form}
	return render(request, 'productos/editar.html',context)


@login_required(login_url='login/')
@permission_required('compras.delete_producto', raise_exception=True)
def inactivar_producto(request,id_producto):
	"""
	Vista para inactivar un producto (soft delete)
	"""
	producto = get_object_or_404(Producto, id=id_producto)
	
	# Verificar si ya está inactivo
	if not producto.activo:
		messages.warning(request, f"El producto '{producto.nombre}' ya está desactivado")
		return redirect('list_productos')

	try:
		# Verificar si el producto tiene stock antes de desactivar (opcional)
		if producto.cantidad_en_stock > 0:
			messages.warning(
				request, 
				f"El producto '{producto.nombre}' tiene stock ({producto.cantidad_en_stock} unidades). "
				f"¿Está seguro de desactivarlo?"
			)
		
		producto.activo = False
		producto.save()
		
		logger.info(f"Producto '{producto.nombre}' desactivado por usuario {request.user}")
		messages.success(request, f"Producto '{producto.nombre}' desactivado correctamente")
	
	except Exception as e:
		logger.error(f"Error al desactivar producto {id_producto}: {str(e)}")
		messages.error(request, "Error al desactivar el producto")
 
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
			try:
				with transaction.atomic():
					proveedor = form.save()
					messages.success(
						request, 
						f"Proveedor creado correctamente"
					)
					logger.info(f"Proveedor creado: {proveedor.razon_social}")
					return redirect('list_proveedores')
			except ValidationError as e:
				messages.error(request, f"Error de validación: {e}")
			except Exception as e:
				messages.error(request, "Error interno del servidor")
				logger.error(f"Error al crear proveedor: {e}")
		else:
			messages.error(request, "Error en el formulario al registrar proveedor")
	else:
		form = ProveedorForm()
	context = {'form_proveedor': form}
	return render(request, 'proveedor/registrar.html', context)


@login_required(login_url='login/')
@permission_required('compras.change_proveedor', raise_exception=True)
def editar_proveedor(request, id_proveedor):
	
	# Recuperamos la instancia del proyecto
	proveedor = get_object_or_404(Proveedor, id=id_proveedor)
	logger.debug(f"Proveedor a editar: {proveedor}")
	print(f"DEBUG: Proveedor: {proveedor}")
	print(f"DEBUG: nro_documento: {proveedor.nro_documento}")
	print(f"DEBUG: tipo_documento: {proveedor.tipo_documento}")

	if request.method == "GET":
		# Actualizamos el formulario con los datos recibidos
		print("DEBUG: Creando formulario...")
		form = ProveedorForm(instance=proveedor)
		print("DEBUG: Formulario creado exitosamente")
		logger.debug(f"Formulario inicializado para proveedor {id_proveedor}")
	else:
		form = ProveedorForm(request.POST,instance=proveedor)
		logger.debug(f"Datos POST recibidos para proveedor {id_proveedor}: {request.POST}")

		if form.is_valid():
	  
			try:
				with transaction.atomic():
					proveedor_actualizado = form.save()
					messages.success(
						request, 
						f"Proveedor actualizado correctamente"
					)
					logger.info(f"Proveedor creado: {proveedor_actualizado.razon_social}")
					return redirect('list_proveedores')
 
			except ValidationError as e:
				messages.error(request, f"Error de validación: {e}")
	
			except Exception as e:
				messages.error(request, "Error interno del servidor")
				logger.error(f"Error al actualizar proveedor {id_proveedor}: {e}")
		else:
			messages.error(request, "Por favor corrija los errores del formulario")
			
	context = {'form_proveedor': form}
	return render(request, 'proveedor/editar.html',context)

@login_required(login_url='login/')
@permission_required('compras.delete_proveedor', raise_exception=True)
def inactivar_proveedor(request,id_proveedor):
	proveedor = get_object_or_404(Proveedor, id=id_proveedor)
 
	if not proveedor.activo:
		messages.info(request, f"El proveedor ya está inactivo.")
		return redirect('list_proveedores')

	# Validar si tiene productos activos asignados
	productos_activos = proveedor.producto_set.filter(activo=True)
	productos_count = productos_activos.count()
	if productos_count > 0:
		
		mensaje_error = (
			f"No se puede desactivar el proveedor "
			f"porque tiene {productos_count} producto(s) activo(s) asignado(s)"
		)
		messages.error(request, mensaje_error)
		logger.warning(f"Intento de desactivar proveedor con productos activos: {proveedor.razon_social}")
		return redirect('list_proveedores')
	try:
		with transaction.atomic():
			proveedor.activo = False
			proveedor.save()
			
			messages.success(
				request, 
				f"El proveedor fue desactivado correctamente"
			)
			logger.info(f"Proveedor desactivado exitosamente: {proveedor.razon_social}")
			  
	except Exception as general_error:
		messages.error(request, "Error interno del servidor. Intente nuevamente.")
		logger.error(f"Error inesperado al desactivar proveedor {id_proveedor}: {general_error}")

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
	
	"""
	Vista para registrar una orden de compra con cabecera y detalle
	"""
 
	formset_compra = formset_factory(FormRegCompraDetalle, extra=0, can_delete=True)
	
	logger.info("Iniciando registro de compra cabecera y detalle")

	if request.method == 'POST':
		form_compra_cab = FormRegCompraCabecera(request.POST)
		form_compra_det = formset_compra(request.POST, prefix='form')

		logger.debug(f"Datos POST recibidos: {dict(request.POST)}")
  
		if form_compra_cab.is_valid() and form_compra_det.is_valid():
	  		
			logger.info("Formularios válidos")
   
			# CORRECCIÓN: Validar que haya detalles ANTES de guardar la cabecera
			detalles_validos = []
   
			for form_det in form_compra_det:
				if form_det.cleaned_data and not form_det.cleaned_data.get('DELETE', False):
					producto_id = form_det.cleaned_data.get('producto_id')
					cantidad = form_det.cleaned_data.get('cantidad')
					
					# Verificar que los campos obligatorios no estén vacíos
					if producto_id and cantidad:
						detalles_validos.append(form_det)
					else:
						messages.warning(request, "Detalle inválido - campos obligatorios faltantes")
						logger.warning("Detalle inválido - campos obligatorios faltantes")
	  
			logger.info(f"Total de detalles válidos: {len(detalles_validos)}")
   			
			# Si no hay detalles válidos, mostrar error y no guardar nada
			if len(detalles_validos) == 0:
				messages.warning(request, "Debe ingresar al menos un detalle de compra válido.")
				logger.warning("No se encontraron detalles válidos")
	
				context = {
					'form_compra_cab': form_compra_cab,
					'form_compra_det': form_compra_det,
					'form_compra_det_prefix': form_compra_det.prefix
				}
				return render(request, 'compras/registrar3_v2.html', context)
			
			# Si hay detalles válidos, proceder a guardar
			try:
				with transaction.atomic():
					
	 				# AHORA SÍ guardar la cabecera (después de validar que hay detalles)
					cabecera = form_compra_cab.save()
					logger.info(f"Cabecera de compra guardada: {cabecera.nro_comprobante}")					
					
	 				# Guardar los detalles válidos
					detalles_guardados = 0
					for form_det in detalles_validos:
						logger.debug(f"Procesando detalle: {form_det.cleaned_data}")
						
						producto_id = form_det.cleaned_data.get('producto_id')
						cantidad = form_det.cleaned_data.get('cantidad')
						descripcion = form_det.cleaned_data.get('descripcion')
						unidad_medida = form_det.cleaned_data.get('unidad_medida')
						precio_compra = form_det.cleaned_data.get('precio_compra')
						subtotal = form_det.cleaned_data.get('subtotal')
						
						try:
							producto_instance = Producto.objects.get(id=producto_id)
						except Producto.DoesNotExist:
							messages.error(request, f"Producto con ID {producto_id} no existe. Detalle omitido.")
							logger.error(f"Producto con ID {producto_id} no existe. Saltando detalle.")
							continue
						
	  					
		   				# Crear y guardar el detalle						
						detalle = OrdenCompraDet(
							orden_compra_cab=cabecera,
							producto=producto_instance,
							cantidad=cantidad,
							descripcion=descripcion,
							unidad_medida=unidad_medida,
							precio_compra=precio_compra,
							total_producto=subtotal,
						)
						
						logger.debug(f"Guardando detalle: {detalle}")
	  
						detalle.save()
						detalles_guardados += 1
						
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
	  
						logger.debug(f"Movimiento de stock registrado para producto {detalle.producto.nombre}")					
					
					messages.success(request, f"Compra registrada exitosamente con {detalles_guardados} detalle(s)")
					return redirect('list_compras')
				
			except Exception as e:
				logger.error(f"Error al guardar compra: {str(e)}")
				messages.error(request, f'¡Error al guardar en la base de datos! {str(e)}')
				
			
		else:
			logger.warning("Formularios inválidos")
			
   			# Recopilar errores
			errores = []
			# Errores de detalles
			for i, form in enumerate(form_compra_det, start=1):
				for field, field_errors in form.errors.items():
					for error in field_errors:
						errores.append(f"Error en el Detalle #{i}, Campo [{field}]: {error}")

			# Errores de cabecera
			for field, field_errors in form_compra_cab.errors.items():
				for error in field_errors:
					errores.append(f"Error en la cabecera: Campo [{field}]: {error}")

			# Mostrar errores
			if errores:
				messages.error(request, "\\n".join(errores))

			logger.debug(f"Errores encontrados: {errores}")

		# Renderizar el template con los errores (tanto para formularios inválidos como para falta de detalles)
		context = {
			'form_compra_cab': form_compra_cab,
			'form_compra_det': form_compra_det,
			'form_compra_det_prefix': form_compra_det.prefix
		}
		return render(request, 'compras/registrar3_v2.html', context)
			
	else:
		form_compra_cab = FormRegCompraCabecera()
		# CORRECCIÓN: También usar el mismo prefijo para GET
		form_compra_det = formset_compra(prefix='form')

	context = {
		'form_compra_cab': form_compra_cab,
		'form_compra_det': form_compra_det,
		'form_compra_det_prefix': form_compra_det.prefix
	}
	return render(request, 'compras/registrar3_v2.html', context)


@login_required(login_url='login/')
@permission_required('compras.change_ordencompracab', raise_exception=True)
@permission_required('compras.change_ordencompradet', raise_exception=True)
def editar_compra(request, id_compra):
    
    compra = get_object_or_404(OrdenCompraCab, id=id_compra)
    detalles_originales = OrdenCompraDet.objects.filter(orden_compra_cab=compra)
    
    formset_compra = formset_factory(FormEditCompraDetalle, extra=0, can_delete=True)

    if request.method == 'POST':
        form_compra_cab = FormEditCompraCabecera(request.POST, instance=compra)
        # CORREGIDO: Usar prefijo consistente
        form_compra_det = formset_compra(request.POST, prefix='form')

        logger.debug(f"Datos POST recibidos: {dict(request.POST)}")

        if form_compra_cab.is_valid() and form_compra_det.is_valid():
            logger.info("Formularios válidos para edición de compra")
            
            # NUEVO: Validar que haya detalles válidos (igual que en registrar)
            detalles_validos = []
            
            for form_det in form_compra_det:
                if form_det.cleaned_data and not form_det.cleaned_data.get('DELETE', False):
                    producto_id = form_det.cleaned_data.get('producto_id')
                    cantidad = form_det.cleaned_data.get('cantidad')
                    
                    if producto_id and cantidad:
                        detalles_validos.append(form_det)
                    else:
                        messages.warning(request, "Detalle inválido - campos obligatorios faltantes")
            
            logger.info(f"Total de detalles válidos: {len(detalles_validos)}")
            
            # NUEVO: Validar que hay al menos un detalle
            if len(detalles_validos) == 0:
                messages.warning(request, "Debe mantener al menos un detalle de compra válido.")
                logger.warning("No se encontraron detalles válidos en edición")
                
                context = {
                    'form_compra_cab': form_compra_cab,
                    'form_compra_det': form_compra_det,
                    'form_compra_det_prefix': form_compra_det.prefix
                }
                return render(request, 'compras/editar3.html', context)
            
            try:
                with transaction.atomic():
                    # 1. Revertir movimientos de stock de detalles originales
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
                    
                    # 4. Crear nuevos detalles válidos
                    detalles_guardados = 0
                    for form_det in detalles_validos:
                        logger.debug(f"Procesando detalle para guardar: {form_det.cleaned_data}")
                        
                        producto_id = form_det.cleaned_data.get('producto_id')
                        cantidad = form_det.cleaned_data.get('cantidad')
                        descripcion = form_det.cleaned_data.get('descripcion')
                        unidad_medida = form_det.cleaned_data.get('unidad_medida')
                        precio_compra = form_det.cleaned_data.get('precio_compra')
                        subtotal = form_det.cleaned_data.get('subtotal')
                        
                        try:
                            producto_instance = Producto.objects.get(id=producto_id)
                        except Producto.DoesNotExist:
                            messages.error(request, f"Producto con ID {producto_id} no existe. Detalle omitido.")
                            logger.error(f"Producto con ID {producto_id} no existe. Saltando detalle.")
                            continue
                        
                        # Crear y guardar el detalle
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
                        detalles_guardados += 1
                        
                        # 5. Registrar nuevo movimiento de stock
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

                    messages.success(request, f"Compra editada exitosamente con {detalles_guardados} detalle(s)")
                    return redirect('list_compras')
                
            except Exception as e:
                logger.error(f"Error al guardar edición de compra: {str(e)}")
                messages.error(request, f'Error al guardar en la base de datos: {str(e)}')
        
        else:
            logger.warning("Formularios inválidos para edición de compra")
            
            # MEJORADO: Recopilar errores igual que en registrar
            errores = []
            
            # Errores de detalles
            for i, form in enumerate(form_compra_det, start=1):
                for field, field_errors in form.errors.items():
                    for error in field_errors:
                        errores.append(f"Error en el Detalle #{i}, Campo [{field}]: {error}")

            # Errores de cabecera
            for field, field_errors in form_compra_cab.errors.items():
                for error in field_errors:
                    errores.append(f"Error en la cabecera: Campo [{field}]: {error}")

            # Mostrar errores
            if errores:
                messages.error(request, "\\n".join(errores))

            logger.debug(f"Errores encontrados: {errores}")

        # Renderizar con errores
        context = {
            'form_compra_cab': form_compra_cab,
            'form_compra_det': form_compra_det,
            'form_compra_det_prefix': form_compra_det.prefix
        }
        return render(request, 'compras/editar3.html', context)
        
    else:
        # GET request - cargar datos existentes
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
        # CORREGIDO: Usar prefijo consistente también en GET
        form_compra_det = formset_compra(initial=detalle_inicial, prefix='form')

    context = {
        'form_compra_cab': form_compra_cab,
        'form_compra_det': form_compra_det,
        'form_compra_det_prefix': form_compra_det.prefix
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
	logger.debug(f"Productos encontrados para '{q}': {data}")
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
    """
    Vista para inactivar una compra y reversar los movimientos de stock
    """
    
    compra_cab = get_object_or_404(OrdenCompraCab, id=id_compra)
    
    if not compra_cab.activo:
        messages.warning(request, "Esta compra ya está inactivada.")
        return redirect('list_compras')
    
    try:
        with transaction.atomic():
            
            detalles_compra = OrdenCompraDet.objects.filter(orden_compra_cab=compra_cab)
            
            logger.info(f"Inactivando compra {compra_cab.nro_comprobante} con {detalles_compra.count()} detalles")
            
            # Reversar los movimientos de stock
            for detalle in detalles_compra:
                registrar_movimiento_stock(
                    producto=detalle.producto,
                    cantidad=detalle.cantidad,
                    movimiento='REV_ENT',
                    descripcion=f"Reversión por inactivación de compra: {compra_cab.nro_comprobante}",
                    ajuste=None,
                    fecha_mov_producto=None,
                    compra_cab=compra_cab,
                    venta_cab=None
                )
                
                detalle.activo = False
                detalle.save()
                
                logger.debug(f"Stock revertido y detalle inactivado para producto {detalle.producto.nombre}: -{detalle.cantidad}")
            
            compra_cab.activo = False
            compra_cab.save()
            
            logger.info(f"Compra {compra_cab.nro_comprobante} inactivada exitosamente")
            
            messages.success(
                request, 
                f"La compra fue inactivada correctamente. "
                f"Se revirtieron {detalles_compra.count()} movimientos de stock."
            )
    
    except Exception as e:
        logger.error(f"Error al inactivar compra {compra_cab.nro_comprobante}: {str(e)}")
        messages.error(request, f'Error al inactivar la compra: {str(e)}')
    
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
 
	print(f"Generando PDF para reporte de compras: tipo={tipo_reporte}, año={anio}, mes={mes}")
 
	logger.info(f"Generando PDF para reporte de compras: tipo={tipo_reporte}, año={anio}, mes={mes}")
	
	# Validación básica
	if not anio:
		messages.error(request, 'Debe seleccionar al menos el año')
		#return render(request, 'reportes/rep_compras_mens_anual.html', {})

	# Filtrar compras (igual que en la función original)
	compras = OrdenCompraCab.objects.filter(activo=True)
	
	# Definir nombres de meses una sola vez
	meses_nombres = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
					 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
	
	if tipo_reporte == 'mensual' and mes:
		logger.info(f"Generando reporte mensual para {mes}/{anio}")
		compras = compras.filter(
			fecha_compra__year=anio,
			fecha_compra__month=mes
		)
		grupo = 'fecha_compra__day'
		nombre_mes = meses_nombres[int(mes)-1]
		titulo_grafico = f'Compras Diarias - {nombre_mes} {anio}'
		periodo = f"{nombre_mes} {anio}"
		etiqueta_total = f"Total compras del mes"
		etiqueta_promedio = f"Promedio diario del mes"
		encabezado_tabla = "Días del Mes"  # ← AGREGAR ESTA LÍNEA
	else:
		logger.info(f"Generando reporte anual para {anio}")
		compras = compras.filter(fecha_compra__year=anio)
		grupo = 'fecha_compra__month'
		titulo_grafico = f'Compras Mensuales - Año {anio}'
		periodo = f"Año {anio}"
		etiqueta_total = f"Total compras del año"
		etiqueta_promedio = f"Promedio mensual del año"
		encabezado_tabla = "Meses del Año"  # ← AGREGAR ESTA LÍNEA

	# Agrupar datos para el gráfico (igual que en la función original)
	datos_grafico = compras.values(grupo).annotate(
		total_compras=Sum('total')
	).order_by(grupo)

	# Preparar datos para el gráfico
	if tipo_reporte == 'mensual':
		categorias = [f'Día {item[grupo]}' for item in datos_grafico]
	else:
		categorias = [meses_nombres[item[grupo]-1] for item in datos_grafico]
	
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

	# CORRECCIÓN: Agregar información más específica
	cantidad_compras = compras.count()
	
	# Preparar el contexto para el PDF
	context = {
		'grafico': grafico_base64,
		'tipo_reporte': tipo_reporte,
		'periodo': periodo,
		'total_general': total_general,
		'promedio': promedio,
		'cantidad_compras': cantidad_compras,
		'etiqueta_total': etiqueta_total,
		'etiqueta_promedio': etiqueta_promedio,
		'encabezado_tabla': encabezado_tabla,  # Nueva variable para el encabezado
		'fecha_generacion': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
		'datos': zip(categorias, montos),  # Para la tabla de datos
	}

	# Configurar la respuesta PDF
	template_path = 'reportes/rep_compras_mens_anual_pdf.html'
	response = HttpResponse(content_type='application/pdf')
	nombre_archivo = f"compras_{'Mensual' if tipo_reporte == 'mensual' else 'anual'}_{anio}"
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
