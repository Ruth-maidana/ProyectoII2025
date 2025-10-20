from decimal import Decimal
from django import forms
from .models import Cliente,VentaCabecera,VentaDetalle, ConfigTimbradoNumeracion
from apps.compras.models import Producto  # Importar el modelo Producto
from apps.compras.utils import validar_stock_venta

from django.core.exceptions import ValidationError



class FormConfigTimbradoNumeracion(forms.ModelForm):
    class Meta:
        model = ConfigTimbradoNumeracion
        fields = ['numero_timbrado', 'fecha_inicio', 'fecha_fin', 'nro_inicial', 'nro_final', 'establecimiento', 'punto_expedicion']

class FormRegistrarCliente(forms.ModelForm):
    documento = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Documento'}),
        label="Documento"
    )
    digito_verificador = forms.ChoiceField(
        choices=[(str(i), str(i)) for i in range(10)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="DV",
        required=False  # No obligatorio por defecto
    )
    
    class Meta:
        model = Cliente
        
         
        fields = [
            'nombre',
			'apellido',
            'nacionalidad',
            'estado_civil',
            'codigo_pais',
            'num_tel',
            'correo',
            'direccion',
            'tipo_documento'
		]
        
        exclude = ['nro_documento']
        
        labels = {
            'nombre':'Nombre',
            'apellido':'Apellido',
            'nacionalidad':'Nacionalidad',
            'estado_civil':'Estado Civil',
            'num_tel':'Num.Telefono',
            'codigo_pais':'Código País',
            'correo':'Correo',
            'direccion':'Direccion',
            'tipo_documento':'Tipo de Documento'
		}
        
        widgets = {
            'nombre':forms.TextInput(attrs={'class':'form-control'}),
            'apellido':forms.TextInput(attrs={'class':'form-control'}),
            'tipo_documento':forms.Select(attrs={'class':'form-control'}),
            'nacionalidad':forms.TextInput(attrs={'class':'form-control'}),
            'estado_civil':forms.Select(attrs={'class':'form-control'}),
            'num_tel':forms.TextInput(attrs={'class':'form-control','placeholder': 'Ejemplo: 981234567'}),
            'codigo_pais':forms.Select(attrs={'class':'form-control','placeholder': '+595'}),
            'correo':forms.EmailInput(attrs={'class':'form-control'}),
            'direccion':forms.TextInput(attrs={'class':'form-control'}),
		}
        
    def clean(self):
        cleaned_data = super().clean()
        documento = cleaned_data.get('documento')
        digito_verificador = cleaned_data.get('digito_verificador')
        tipo_documento = cleaned_data.get('tipo_documento')
        
        # Concatenar documento y dígito verificador solo si el tipo de documento es RUC
        if tipo_documento == 'RUC':
            if not digito_verificador:
                raise forms.ValidationError("Debe seleccionar un dígito verificador para el RUC.")
            nro_documento = f"{documento}-{digito_verificador}"
        else:
            nro_documento = documento  # Solo el documento para CI

        # Validar si el número de documento ya existe
        if Cliente.objects.filter(nro_documento__iexact=nro_documento).exists():
            raise forms.ValidationError({'documento': 'Ya existe un cliente con este número de documento.'})

        # Asignar el número de documento calculado al cleaned_data
        cleaned_data['nro_documento'] = nro_documento
        return cleaned_data

    def save(self, commit=True):
        # Sobrescribir el método save para guardar nro_documento
        instance = super().save(commit=False)
        cleaned_data = self.cleaned_data
        instance.nro_documento = cleaned_data.get('nro_documento')  # Asignar el valor calculado
        if commit:
            instance.save()
        return instance
        
        
class FormEditarCliente(forms.ModelForm):
    
    class Meta:
        model = Cliente
        
         
        fields = [
            'nombre',
			'apellido',
            'tipo_documento',
            'nro_documento',
            'nacionalidad',
            'estado_civil',
            'num_tel',
            'correo',
            'direccion',
		]
        
        labels = {
            'nombre':'Nombre',
            'apellido':'Apellido',
            'tipo_documento':'Tipo de Documento',
            'nro_documento':'Nro. Documento',
            'nacionalidad':'Nacionalidad',
            'estado_civil':'Estado Civil',
            'num_tel':'Num.Telefono',
            'correo':'Correo',
            'direccion':'Direccion',
		}
        
        widgets = {
            'nombre':forms.TextInput(attrs={'class':'form-control'}),
            'apellido':forms.TextInput(attrs={'class':'form-control'}),
            'tipo_documento':forms.TextInput(attrs={'class':'form-control','readonly': True}),
            'nro_documento':forms.TextInput(attrs={'class':'form-control','readonly': True}),
            'nacionalidad':forms.TextInput(attrs={'class':'form-control'}),
            'estado_civil':forms.Select(attrs={'class':'form-control'}),
            'num_tel':forms.TextInput(attrs={'class':'form-control'}),
            'correo':forms.EmailInput(attrs={'class':'form-control'}),
            'direccion':forms.TextInput(attrs={'class':'form-control'}),
		}
        
class ClienteViewForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'nro_documento','nacionalidad','estado_civil','num_tel','correo', 'activo']
        
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'disabled': True}),
            'apellido': forms.TextInput(attrs={'class': 'form-control', 'disabled': True}),
            'nro_documento': forms.TextInput(attrs={'class': 'form-control', 'disabled': True}),
            'nacionalidad': forms.TextInput(attrs={'class': 'form-control', 'disabled': True}),
            'estado_civil': forms.TextInput(attrs={'class': 'form-control', 'disabled': True}),
            'num_tel': forms.TextInput(attrs={'class': 'form-control', 'disabled': True}),
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'disabled': True}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'disabled': True}),
            #'fecha_insercion': forms.TextInput(attrs={'class': 'form-control', 'disabled': True}),
            'activo': forms.TextInput(attrs={'class': 'form-control', 'disabled': True}),
        }

class FormRegVentaCabecera(forms.ModelForm):
    
    iva_diez = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        label="IVA 10%",
        initial=0.0,
        decimal_places=2,
        min_value=0.0,
        max_digits=10
    )
    
    iva_cinco = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly','step': '0.01'}),
        label="IVA 5%",
        initial=0.0,
        min_value=0.0,
        decimal_places=2,
        max_digits=10
    )
    
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.filter(activo=True),
        empty_label="Seleccione un cliente",
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Cliente",
        to_field_name="id"  # Ensure the correct field is used for the value
    )
    
    descuento = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label="Descuento",
        initial=0.0,
        min_value=0.0,
        decimal_places=2,
        max_digits=10
    )
    
    total = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        label="Total",
        initial=0.0,
        min_value=0.0,
        decimal_places=2,
        max_digits=100
    )
    
    CONDICION_VENTA_CHOICES = (
        ('Contado','Contado'),
    )
    
    condicion_venta = forms.ChoiceField(
        choices=CONDICION_VENTA_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),  # Mantén consistencia con tu template
        initial='Contado',
        label="Condición de Venta"
    )
    
    nota_remision = forms.CharField(required=False,
                                    widget=forms.TextInput(attrs={'class': 'form-control'}),
                                    label="Nota de Remisión")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize the display of the cliente field to show "nombre apellido"
        self.fields['cliente'].queryset = Cliente.objects.filter(activo=True)
        self.fields['cliente'].label_from_instance = lambda obj: f"{obj.nombre} {obj.apellido}"

    class Meta:
        model = VentaCabecera
        
        
        fields = [
                'fecha_venta',
                'nro_comprobante',
                'vendedor',
                'cliente',
                'total',
                'forma_pago',
                'iva_diez',
                'iva_cinco',
                'descuento',
                'forma_pago',
                'timbrado',
                'nota_remision',
                'condicion_venta'
        ]
                
        labels = {
            'fecha_venta':'Fecha de Venta',
            'nro_comprobante':'Nro. Comprobante',
            'vendedor':'Vendedor',
            'forma_pago':'Forma de Pago',
            'timbrado':'Timbrado',
            #'nota_remision':'Nota de Remisión',
        }
        
        widgets = {
            'timbrado': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'fecha_venta': forms.DateTimeInput(attrs={'class': 'form-control','readonly': 'readonly'}),
            'vendedor': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'forma_pago': forms.Select(attrs={'class': 'form-control'}),
            'nro_comprobante': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }
    
    def clean_descuento(self):
        """Validar que el descuento sea válido"""
        descuento = self.cleaned_data.get('descuento', Decimal('0.0'))
        
        if descuento < 0:
            raise ValidationError("El descuento no puede ser negativo.")
        
        return descuento
    
    def clean_total(self):
        """Validar que el total sea positivo"""
        total = self.cleaned_data.get('total', Decimal('0.0'))
        
        if total < 0:
            raise forms.ValidationError("El total no puede ser negativo. Verifique las cantidades de los productos.")
        
        if total == 0:
            raise forms.ValidationError("El total debe ser mayor a cero. Agregue productos a la orden.")
            
        return total
    
    def clean_iva_cinco(self):
        """Validar IVA 5%"""
        iva_cinco = self.cleaned_data.get('iva_cinco', Decimal('0.0'))
        
        if iva_cinco < 0:
            raise forms.ValidationError("El IVA 5% no puede ser negativo. Verifique las cantidades de los productos.")
            
        return iva_cinco
    
    def clean_iva_diez(self):
        """Validar IVA 10%"""
        iva_diez = self.cleaned_data.get('iva_diez', Decimal('0.0'))
        
        if iva_diez < 0:
            raise ValidationError("El IVA 10% no puede ser negativo. Verifique las cantidades de los productos.")
            
        return iva_diez
    
    def clean(self):
        """Validaciones adicionales de la orden"""
        cleaned_data = super().clean()
        cliente = cleaned_data.get('cliente')
        total = cleaned_data.get('total', Decimal('0.0'))
        descuento = cleaned_data.get('descuento', Decimal('0.0'))
        
        # Verificar que el proveedor esté activo
        if cliente and not cliente.activo:
            raise ValidationError({
                'cliente': 'No se puede registrar una venta para un cliente inactivo. Seleccione un cliente activo.'
            })
        
        # Validar relación entre descuento y total
        if total > 0 and descuento > total:
            raise ValidationError({
                'descuento': f'El descuento ({descuento}) no puede ser mayor al total ({total}).'
            })
            
        return cleaned_data
    
    
class FormRegVentaDetalle(forms.Form):
                                    
    producto_id = forms.IntegerField(
        widget=forms.HiddenInput(attrs={'class': 'form-control'}),
        label="Producto ID"
    )
    
    descripcion = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        label="Descripción"
    )
    
    cantidad = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'step': '1'
        }),
        label="Cantidad",
        min_value=1,
        initial=1
    )
    
    unidad_medida = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control ', 'readonly': 'readonly'}),
        label="Unidad de Medida"
    )
    
    precio_unit_venta = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 
            'readonly': 'readonly',
            'step': '0.01'
        }),
        label="Precio Unitario",
        initial=0.0,
        min_value=0.0,
        decimal_places=2,
        max_digits=100
    )
    
    subtotal = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 
            'readonly': 'readonly',
            'step': '0.01'
        }),
        label="Subtotal",
        initial=0.0,
        min_value=0.0,
        decimal_places=2,
        max_digits=100
    )
    
    
    def clean_cantidad(self):
        """Validar cantidad con mensajes más específicos"""
        cantidad = self.cleaned_data.get('cantidad')
        
        if cantidad is None:
            raise ValidationError("La cantidad es obligatoria.")
            
        if cantidad <= 0:
            raise ValidationError(f"La cantidad debe ser mayor a cero. Valor ingresado: {cantidad}")
        
        # Validar que sea un número entero positivo
        if not isinstance(cantidad, int) and not cantidad.is_integer():
            raise ValidationError("La cantidad debe ser un número entero.")
        
        return cantidad
    
    
    def clean_precio_unit_venta(self):
        """Validar precio de venta"""
        precio = self.cleaned_data.get('precio_unit_venta')
        
        if precio is None:
            raise ValidationError("El precio de compra es obligatorio.")
            
        if precio <= 0:
            raise ValidationError(f"El precio debe ser mayor a cero. Valor ingresado: {precio}")
            
        return precio
    
    def clean_subtotal(self):
        """Validar subtotal"""
        subtotal = self.cleaned_data.get('subtotal')
        
        if subtotal is not None and subtotal < 0:
            raise ValidationError("El subtotal no puede ser negativo. Verifique la cantidad y el precio.")
            
        return subtotal
    
    def clean(self):
        cleaned_data = super().clean()
        cantidad = cleaned_data.get('cantidad')
        producto_id = cleaned_data.get('producto_id')
    
        # Validar producto
        if not producto_id:
            self.add_error('producto_id', "Debe seleccionar un producto.")
        else:
            try:
                producto = Producto.objects.get(id=producto_id)
                
                # Validar stock solo si encontramos el producto y tenemos cantidad
                if cantidad and producto.cantidad_en_stock < cantidad:
                    mensaje = f"No hay suficiente stock para el producto '{producto.nombre}'. Stock disponible: {producto.cantidad_en_stock}."
                    self.add_error('cantidad', mensaje)
                    
            except Producto.DoesNotExist:
                self.add_error('producto_id', "Producto no encontrado.")
    
        return cleaned_data

    
class FormEditVentaDetalle(forms.Form):
                                    
    producto_id = forms.IntegerField(
        widget=forms.HiddenInput(attrs={'class': 'form-control'}),
        label="Producto ID"
    )
    
    producto_nombre = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        label="Producto"
    )
    
    producto_iva = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        label="IVA Producto",
        initial=0.0,
        min_value=0.0
    )
    
    descripcion = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        label="Descripción"
    )
    
    cantidad = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control cantidad',
            'min': '1',
            'step': '1'
        }),
        label="Cantidad",
        min_value=1,
        initial=1
    )
    
    unidad_medida = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control ', 'readonly': 'readonly'}),
        label="Unidad de Medida"
    )
    
    precio_unit_venta = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control precio_unit_venta', 
            'readonly': 'readonly',
            'step': '0.01'
        }),
        label="Precio Unitario",
        initial=0.0,
        min_value=0.0
    )
    
    subtotal = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 
            'readonly': 'readonly',
            'step': '0.01'
        }),
        label="Subtotal",
        initial=0.0,
        min_value=0.0
    )
    
    def clean(self):
        cleaned_data = super().clean()
        cantidad = cleaned_data.get('cantidad')
        producto_id = cleaned_data.get('producto_id')
        
        # Validar cantidad
        if cantidad is None or cantidad <= 0:
            self.add_error('cantidad', "La cantidad debe ser un número entero mayor a cero.")
        
        # Validar producto solo si la cantidad es válida
        elif not producto_id:
            self.add_error('producto_id', "Debe seleccionar un producto.")
        
        else:
            # Intentar obtener el producto y validar stock
            try:
                producto = Producto.objects.get(id=producto_id)
                
                # Validar stock disponible
                if producto.cantidad_en_stock < cantidad:
                    mensaje = f"No hay suficiente stock para el producto '{producto.nombre}'. Stock disponible: {producto.cantidad_en_stock}."
                    self.add_error('cantidad', mensaje)
                    
            except Producto.DoesNotExist:
                self.add_error('producto_id', "Producto no encontrado.")
        
        return cleaned_data
    
class FormEditarVentaCabecera(forms.ModelForm):
    iva_diez = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        label="IVA 10%",
        initial=0.0,
        min_value=0.0
    )
    
    iva_cinco = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        label="IVA 5%",
        initial=0.0,
        min_value=0.0
    )
    
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.filter(activo=True),
        empty_label="Seleccione un cliente",
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Cliente",
        to_field_name="id"  # Ensure the correct field is used for the value
    )
    
    descuento = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label="Descuento",
        initial=0.0,
        min_value=0.0
    )
    
    total = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        label="Total",
        initial=0.0,
        min_value=0.0
    )
    
    condicion_venta = forms.ChoiceField(
        choices=[('contado','Contado')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),  # Mantén consistencia con tu template
        label="Condición de Venta",
        
    )
    
    nota_remision = forms.CharField(required=False,
                                    widget=forms.TextInput(attrs={'class': 'form-control'}),
                                    label="Nota de Remisión")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize the display of the cliente field to show "nombre apellido"
        self.fields['cliente'].queryset = Cliente.objects.filter(activo=True)
        self.fields['cliente'].label_from_instance = lambda obj: f"{obj.nombre} {obj.apellido}"

    class Meta:
        model = VentaCabecera
        
        
        fields = [
                'fecha_venta',
                'nro_comprobante',
                'condicion_venta',
                'vendedor',
                'cliente',
                'total',
                'forma_pago',
                'iva_diez',
                'iva_cinco',
                'descuento',
                'forma_pago',
                'timbrado',
                'nota_remision',
        ]
                
        labels = {
            'fecha_venta':'Fecha de Venta',
            'nro_comprobante':'Nro. Comprobante',
            'vendedor':'Vendedor',
            'forma_pago':'Forma de Pago',
            'timbrado':'Timbrado',
            
        }
        
        widgets = {
            'nro_comprobante': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'fecha_venta': forms.DateTimeInput(attrs={'class': 'form-control','readonly': 'readonly'}),
            'vendedor': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'forma_pago': forms.Select(attrs={'class': 'form-control'}),
            'timbrado': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            
        }
        
        
    def _validar_cantidad(self, cantidad, cleaned_data):
        """Valida que la cantidad sea válida."""
        if cantidad is None or cantidad <= 0:
            self.add_error('cantidad', "La cantidad debe ser un número entero mayor a cero.")
            return False
        return True
    
    
    def _validar_producto(self, producto_id, cleaned_data):
        """Valida que el producto exista."""
        if not producto_id:
            self.add_error('producto_id', "Debe seleccionar un producto.")
            return None
            
        try:
            return Producto.objects.get(id=producto_id)
        except Producto.DoesNotExist:
            self.add_error('producto_id', "Producto no encontrado.")
            return None
    
    def _validar_stock(self, producto, cantidad):
        """Valida que haya suficiente stock."""
        if producto.cantidad_en_stock < cantidad:
            mensaje = f"No hay suficiente stock para el producto '{producto.nombre}'. Stock disponible: {producto.cantidad_en_stock}."
            self.add_error('cantidad', mensaje) # ¡Error vinculado al campo!
    
    
    def clean_descuento(self):
        """Validar que el descuento sea válido"""
        descuento = self.cleaned_data.get('descuento', Decimal('0.0'))
        
        if descuento < 0:
            raise ValidationError("El descuento no puede ser negativo.")
        
        return descuento
    
    def clean_total(self):
        """Validar que el total sea positivo"""
        total = self.cleaned_data.get('total', Decimal('0.0'))
        
        if total < 0:
            raise forms.ValidationError("El total no puede ser negativo. Verifique las cantidades de los productos.")
        
        if total == 0:
            raise forms.ValidationError("El total debe ser mayor a cero. Agregue productos a la orden.")
            
        return total
    
    def clean_iva_cinco(self):
        """Validar IVA 5%"""
        iva_cinco = self.cleaned_data.get('iva_cinco', Decimal('0.0'))
        
        if iva_cinco < 0:
            raise forms.ValidationError("El IVA 5% no puede ser negativo. Verifique las cantidades de los productos.")
            
        return iva_cinco
    
    def clean_iva_diez(self):
        """Validar IVA 10%"""
        iva_diez = self.cleaned_data.get('iva_diez', Decimal('0.0'))
        
        if iva_diez < 0:
            raise ValidationError("El IVA 10% no puede ser negativo. Verifique las cantidades de los productos.")
            
        return iva_diez
    
    
    def validar_cliente_activo(self):
        cliente = self.cleaned_data.get('cliente')
        
        if cliente and not cliente.activo:
            raise ValidationError("No se puede registrar una venta para un cliente inactivo. Seleccione un cliente activo.")
        
        return cliente

