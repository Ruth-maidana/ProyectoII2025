from django import forms
from django.core.exceptions import ValidationError
from .models import MovimientoStock, ConfiguracionStock
from apps.compras.models import Producto

        
class ConfiguracionStockForm(forms.ModelForm):
    
    class Meta:
        model = ConfiguracionStock
        fields = ['cantidad_maxima', 'descripcion', 'frecuencia_notificacion']
        
        # Definición de etiquetas para los campos del formulario
        labels = {
            'cantidad_maxima': 'Cantidad Minima de Stock',
            'descripcion': 'Mensaje de Notificación',
            'frecuencia_notificacion': 'Frecuencia de Notificación (en segundos)',
        }
        
        widgets = {
            'cantidad_maxima': forms.NumberInput(attrs={'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'frecuencia_notificacion': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class AjusteStockForm(forms.Form):
    #class Meta:
        #model = MovimientoStock
        
    ajuste = forms.ChoiceField(
        choices=MovimientoStock.TIPO_AJUSTE,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Tipo de Ajuste'
    )
    cantidad = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label='Cantidad'
    )
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Producto'
    )
    descripcion = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Descripción',
        required=False
    )
    movimiento = forms.ChoiceField(
        choices=MovimientoStock.TIPO_MOVIMIENTO,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Tipo de Movimiento'
    )
    
    
    '''fields = ['ajuste', 'cantidad', 'producto', 'descripcion','movimiento']
    
    # Definición de etiquetas para los campos del formulario
    labels = {
        'ajuste': 'Tipo de Ajuste',
        'cantidad': 'Cantidad',
        'producto': 'Producto',
        'descripcion': 'Descripción',
        'movimiento': 'Tipo de Movimiento',
    }
    
    widgets = {
        'ajuste': forms.Select(attrs={'class': 'form-control'}),
        'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
        'producto': forms.Select(attrs={'class': 'form-control'}),
        'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
        'movimiento': forms.Select(attrs={'class': 'form-control'}),
    }'''