from django.shortcuts import render, redirect
from .forms import CompraForm
from .forms import ProductoForm


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


def registrar_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')
    else:
        form = ProductoForm()
    context = {'form': form}
    return render(request, 'ventas/registrar_producto.html', context)


def registrar_compra(request):
    if request.method == 'POST':
        form = CompraForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_compras')
    else:
        form = CompraForm()
    context = {'form': form}
    return render(request, 'ventas/registrar_compra.html', context)


