from django import forms
from .models import Cliente,VentaCabecera,VentaDetalle, ConfigTimbradoNumeracion
from apps.compras.models import Producto  # Importar el modelo Producto
from apps.compras.utils import validar_stock_venta




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
        
        exclude = ['fecha_insercion','fecha_modificacion','activo','nro_documento']
        
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
            #'activo',
		]
        
        exclude = ['fecha_insercion','fecha_modificacion','activo']
        
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
        fields = ['nombre', 'apellido', 'nro_documento','nacionalidad','estado_civil','num_tel','correo','fecha_insercion', 'activo']
        
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'disabled': True}),
            'apellido': forms.TextInput(attrs={'class': 'form-control', 'disabled': True}),
            'nro_documento': forms.TextInput(attrs={'class': 'form-control', 'disabled': True}),
            'nacionalidad': forms.TextInput(attrs={'class': 'form-control', 'disabled': True}),
            'estado_civil': forms.TextInput(attrs={'class': 'form-control', 'disabled': True}),
            'num_tel': forms.TextInput(attrs={'class': 'form-control', 'disabled': True}),
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'disabled': True}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'disabled': True}),
            'fecha_insercion': forms.TextInput(attrs={'class': 'form-control', 'disabled': True}),
            'activo': forms.TextInput(attrs={'class': 'form-control', 'disabled': True}),
        }

class FormRegVentaCabecera(forms.ModelForm):
    
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
        choices=VentaCabecera.CONDICION_VENTA_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),  # Mantén consistencia con tu template
        initial='contado',
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
        
        exclude = ['fecha_insercion','fecha_modificacion','activo','estado']
        
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
            'forma_pago': forms.Select(attrs={'class': 'form-control'}),
            'nro_comprobante': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }
    
class FormRegVentaDetalle(forms.Form):
                                    
    producto_id = forms.IntegerField(
        widget=forms.HiddenInput(attrs={'class': 'form-control'}),
        label="Producto ID"
    )
    
    '''producto_nombre = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        label="Producto"
    )'''
    
    descripcion = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        label="Descripción"
    )
    
    '''cantidad = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label="Cantidad",
        min_value=1,
        initial=1
    )'''
    
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
    
    '''precio_unit_venta = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        label="Precio Unitario",
        initial=0.0,
        min_value=0.0
    )'''
    
    precio_unit_venta = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 
            'readonly': 'readonly',
            'step': '0.01'
        }),
        label="Precio Unitario",
        initial=0.0,
        min_value=0.0
    )
    
    '''subtotal = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        label="Subtotal",
        initial=0.0,
        min_value=0.0
    )'''
    
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
        print ('-----------------------------------')
        print ('Ingreso al form de detalle',cantidad)
        if cantidad is None:
            self.add_error('cantidad',"La cantidad debe ser un número entero mayor a cero.")
            return cleaned_data  # Retornar aquí para evitar continuar con la validación
        
        if cantidad == 0:
            #raise forms.ValidationError('cantidad',"La cantidad debe ser un número entero mayor a cero.")
            self.add_error('cantidad',"La cantidad debe ser un número entero mayor a cero.")
            return cleaned_data
        
        if cantidad < 0:
            #raise forms.ValidationError('cantidad',"La cantidad debe ser un número entero mayor a cero.")
            self.add_error('cantidad',"La cantidad debe ser un número entero mayor a cero.")
            return cleaned_data
        # Validar el producto
        #producto = Producto.objects.filter(id=producto_id).first()  # Obtener el producto por ID
        
        '''if not producto:
            self.add_error('producto_id',"Producto no encontrado.")'''
        
        # Validar producto
        if not producto_id:
            self.add_error('producto_id', "Debe seleccionar un producto.")
            return cleaned_data
            
        try:
            producto = Producto.objects.get(id=producto_id)
        except Producto.DoesNotExist:
            self.add_error('producto_id', "Producto no encontrado.")
            return cleaned_data
        
        if producto.cantidad_en_stock < cantidad:
            mensaje = f"No hay suficiente stock para el producto '{producto.nombre}'. Stock disponible: {producto.cantidad_en_stock}."
            self.add_error('cantidad', mensaje)  # ¡Error vinculado al campo!
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
    
    '''cantidad = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label="Cantidad",
        min_value=1,
        initial=1
    )'''
    
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
    
    '''precio_unit_venta = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        label="Precio Unitario",
        initial=0.0,
        min_value=0.0
    )'''
    
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
    
    '''subtotal = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        label="Subtotal",
        initial=0.0,
        min_value=0.0
    )'''
    
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
        
        if cantidad is None or cantidad <= 0:
            self.add_error('cantidad',"La cantidad debe ser un número entero mayor a cero.")
            return cleaned_data  # Retornar aquí para evitar continuar con la validación
        
        # Validar el producto
        #producto = Producto.objects.filter(id=producto_id).first()  # Obtener el producto por ID
        
        '''if not producto:
            self.add_error('producto_id',"Producto no encontrado.")'''
        
        # Validar producto
        if not producto_id:
            self.add_error('producto_id', "Debe seleccionar un producto.")
            return cleaned_data
            
        try:
            producto = Producto.objects.get(id=producto_id)
        except Producto.DoesNotExist:
            self.add_error('producto_id', "Producto no encontrado.")
            return cleaned_data
        
        if producto.cantidad_en_stock < cantidad:
            mensaje = f"No hay suficiente stock para el producto '{producto.nombre}'. Stock disponible: {producto.cantidad_en_stock}."
            self.add_error('cantidad', mensaje)  # ¡Error vinculado al campo!
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
        choices=VentaCabecera.CONDICION_VENTA_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),  # Mantén consistencia con tu template
        initial='contado',
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
        
        exclude = ['fecha_insercion','fecha_modificacion','activo','estado']
        
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
    
    
    
    
    
    
    
    
    
    
    

'''class FormRegVentaDetalle(forms.ModelForm):
    
    class Meta:
        model = VentaDetalle
        fields = [
            'producto',
            'monto_iva_cinco',
            'monto_iva_diez',
            'precio_unit_venta',
            'cantidad',
            'descripcion',
            'unidad_medida',
            'subtotal',
        ]
        
        exclude = ['fecha_insercion','fecha_modificacion','activo']
        
        labels = {
            'producto':'Producto',
            'cantidad':'Cantidad',
            'subtotal':'Subtotal',
            'descripcion':'Descripcion',
            'unidad_medida':'Unidad de Medida',
            'precio_unit_venta':'Precio Unitario',
            'monto_iva_diez':'IVA 10%',
            'monto_iva_cinco':'IVA 5%',
        }
        
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'subtotal': forms.NumberInput(attrs={'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'unidad_medida': forms.TextInput(attrs={'class': 'form-control'}),
            'precio_unit_venta': forms.NumberInput(attrs={'class': 'form-control'}),
            'monto_iva_diez': forms.NumberInput(attrs={'class': 'form-control'}),
            'monto_iva_cinco': forms.NumberInput(attrs={'class': 'form-control'}),
        }
'''



#--------------------------------------------------------------------

TIPO_COMPROBANTE_CHOICES = [
    ('boleta', 'Boleta'),
    ('factura', 'Factura'),
    ('ticket', 'Ticket'),
]

class VentaForm(forms.Form):
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.all(),
        label="Cliente",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    fecha = forms.DateField(
        label="Fecha de Venta",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    vendedor = forms.CharField(
        label="Vendedor",
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )
    tipo_comprobante = forms.ChoiceField(
        choices=TIPO_COMPROBANTE_CHOICES,
        label="Tipo de Comprobante",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    numero_comprobante = forms.CharField(
        label="Número de Comprobante",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    total = forms.DecimalField(
        label="Total",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )