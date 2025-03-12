from django import forms
from .models import Producto, Compra

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'cantidad_en_stock', 'activo']
        

class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = ['producto', 'cantidad', 'precio_compra', 'fecha_compra', 'proveedor']