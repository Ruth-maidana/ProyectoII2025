from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.http import HttpResponse, JsonResponse

from apps.compras.models import Producto
from .models import Cliente, VentaCabecera, VentaDetalle
from .forms import ClienteViewForm, FormEditarCliente, FormEditarVentaCabecera, FormRegistrarCliente, VentaForm, FormRegVentaCabecera, FormRegVentaDetalle, FormEditarVentaDetalle
from django.forms import formset_factory, inlineformset_factory
from django.db.models import Q
from apps.inventarios.utils import registrar_movimiento_stock
from django.db import transaction 
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required,permission_required

# Create your views here.

#@login_required(login_url='/login_user')
#@permission_required('oficina.add_oficina', raise_exception=True)

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


#@login_required(login_url='/login_user')
#@permission_required('oficina.change_oficina', raise_exception=True)
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


#@login_required(login_url='/login_user')
#@permission_required('oficina.delete_oficina', raise_exception=True)
def inactivar_cliente(request, id_cliente):
    cliente = Cliente.objects.get(id=id_cliente)
    cliente.activo = False
    messages.success(request, "Cliente eliminado correctamente")
    cliente.save()
    return redirect('list_clientes')


#@login_required(login_url='/login_user')
#@permission_required('oficina.view_oficina', raise_exception=True)
def listar_cliente(request):
    clientes = Cliente.objects.all().order_by('id')
    clientes_forms = []
    for cliente in clientes:
        formulario = ClienteViewForm(instance=cliente)
        clientes_forms.append({
            'cliente': cliente,
            'form': formulario
        })

    '''clientes_forms = [
        {'cliente': cliente, 'form': ClienteViewForm(instance=cliente)}
        for cliente in clientes
    ]'''
    return render(request, 'clientes/listar.html', {'Clientes': clientes, 'clientes_forms': clientes_forms})


def registrar_venta(request):
    formset_venta = formset_factory(FormRegVentaDetalle, extra=0, can_delete=True)
    if request.method == 'POST':
        form_venta_cab = FormRegVentaCabecera(request.POST)
        form_venta_det = formset_venta(request.POST)

        # Imprimir los datos enviados al backend
        print("Datos enviados al backend:")
        print(request.POST)
        print("Detalles de la venta:")
        # Imprimir los datos de cada detalle de la venta
        for i, form_det in enumerate(form_venta_det):
            print(f"Form Detalle #{i}: {form_det}")

        if form_venta_cab.is_valid() and form_venta_det.is_valid():
            try:
                with transaction.atomic():
                    # Guardar la cabecera de la venta
                    cabecera = form_venta_cab.save()
                    print(f"Cabecera de venta guardada: {cabecera}")
                    
                    # Guardar los detalles de la venta
                    for form_det in form_venta_det:
                        producto_id = form_det.cleaned_data.get('producto_id')
                        cantidad = form_det.cleaned_data.get('cantidad')
                        descripcion = form_det.cleaned_data.get('descripcion')
                        unidad_medida = form_det.cleaned_data.get('unidad_medida')
                        precio_venta = form_det.cleaned_data.get('precio_unit_venta')
                        subtotal = form_det.cleaned_data.get('subtotal')
                        producto_instance = Producto.objects.get(id=producto_id)
                        print(f"Producto ID: {producto_id}, Cantidad: {cantidad}, Descripción: {descripcion}, Unidad de Medida: {unidad_medida}, Precio Unitario: {precio_venta}, Subtotal: {subtotal}")
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
                        print(f"Detalle: {detalle}")
                        detalle.save()
                        
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
                        

                    messages.success(request, "Venta registrada exitosamente")
                    
                    return redirect('list_ventas')
                
            except Exception as e:
                print(f'Error: {e}')  # Log the error
                messages.error(request, '¡Error al guardar en la base de datos!')
                print('Error de integridad')
            
        else:
            print(form_venta_cab.errors)
            print(form_venta_det.errors)
            messages.error(request, '¡Hubo un error al registrar la venta!')
    else:
        form_venta_cab = FormRegVentaCabecera()
        form_venta_det = formset_venta()

    context = {
        'form_venta_cab': form_venta_cab,
        'form_venta_det': form_venta_det,
    }
    return render(request, 'ventas/registrar2.html', context)


def editar_venta(request, id_venta):
    venta = get_object_or_404(VentaCabecera, id=id_venta)
    

    VentaDetalleFormSet = inlineformset_factory(
        VentaCabecera,
        VentaDetalle,
        form=FormEditarVentaDetalle,  # Custom form for editing
        extra=0,
        can_delete=True
    )

    if request.method == 'POST':
        form_venta_cab = FormEditarVentaCabecera(request.POST, instance=venta)
        form_venta_det = VentaDetalleFormSet(request.POST, instance=venta)

        if form_venta_cab.is_valid() and form_venta_det.is_valid():
            cabecera = form_venta_cab.save()  # Cambiado para usar el método save() del formulario
            for form_det in form_venta_det:
                producto_id = form_det.cleaned_data.get('producto_id')
                cantidad = form_det.cleaned_data.get('cantidad')
                descripcion = form_det.cleaned_data.get('descripcion')
                unidad_medida = form_det.cleaned_data.get('unidad_medida')
                precio_venta = form_det.cleaned_data.get('precio_unit_venta')
                subtotal = form_det.cleaned_data.get('subtotal')
                producto_instance = Producto.objects.get(id=producto_id)
                print(f"Producto ID: {producto_id}, Cantidad: {cantidad}, Descripción: {descripcion}, Unidad de Medida: {unidad_medida}, Precio Unitario: {precio_venta}, Subtotal: {subtotal}")
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
                print(f"Detalle: {detalle}")
                detalle.save()
            messages.success(request, "¡La venta fue actualizada exitosamente!")
            return redirect('list_ventas')
        else:
            messages.error(request, "¡Hubo un error al actualizar la venta! Verifica los datos ingresados.")
    else:
        form_venta_cab = FormEditarVentaCabecera(instance=venta)
        form_venta_det = VentaDetalleFormSet(instance=venta)

    context = {
        'form_venta': form_venta_cab,
        'form_venta_det': form_venta_det,
    }
    return render(request, 'ventas/editar2.html', context)



def editar_venta_v2(request, id_venta):
    venta = get_object_or_404(VentaCabecera, id=id_venta)
    VentaDetalleFormSet = inlineformset_factory(
        VentaCabecera,
        VentaDetalle,
        form=FormEditarVentaDetalle,  # Custom form for editing
        extra=0,
        can_delete=True
    )

    if request.method == 'POST':
        form_venta_cab = FormEditarVentaCabecera(request.POST, instance=venta)
        form_venta_det = VentaDetalleFormSet(request.POST, instance=venta)

        if form_venta_cab.is_valid() and form_venta_det.is_valid():
            form_venta_cab.save()  # Cambiado para usar el método save() del formulario
            form_venta_det.save()
            print(form_venta_cab)
            print(form_venta_det)
            messages.success(request, "¡La venta fue actualizada exitosamente!")
            return redirect('list_ventas')
        else:
            messages.error(request, "¡Hubo un error al actualizar la venta! Verifica los datos ingresados.")
    else:
        form_venta_cab = FormEditarVentaCabecera(instance=venta)
        form_venta_det = VentaDetalleFormSet(instance=venta)

    context = {
        'form_venta': form_venta_cab,
        'form_venta_det': form_venta_det,
    }
    return render(request, 'ventas/editar.html', context)


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


def listar_ventas(request):
    ventas = VentaCabecera.objects.prefetch_related('detalles').all()  # Usar related_name definido
    print("Ventas con detalles prefetch_related:")
    for venta in ventas:
        print(f"Venta ID: {venta.id}, Detalles: {list(venta.detalles.all())}")
    context = {'Ventas': ventas}
    return render(request, 'ventas/listar.html', context)


def reg_venta_modelo(request):
    if request.method == 'POST':
        form_reg_venta_model = VentaForm(request.POST)
        if form_reg_venta_model.is_valid():
            form_reg_venta_model.save()
    else:
        form_reg_venta_model = VentaForm()

    context = {
        'form': form_reg_venta_model,
    }
    return render(request, 'ventas/modelo.html', context)


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


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Cambia 'home' por la URL a donde quieras redirigir
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')

    return render(request, 'usuario/login.html')


@login_required(login_url='login/')
def index(request):
    return render(request, 'index.html', {})



