from decimal import Decimal
from django import forms
from django.forms import inlineformset_factory
from .models import Producto, OrdenCompraCab, OrdenCompraDet, Categoria, Proveedor
from apps.compras.utils import validar_stock_compra
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']

class CategoriaEditForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']

class CategoriaViewForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion', 'activo']
        
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'disabled': True}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'disabled': True}),
            'activo': forms.TextInput(attrs={'class': 'form-control', 'disabled': True}),
        }

#-------------------------------------------------------------------

class ProductoForm(forms.ModelForm):
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.filter(activo=True),  # Filtrar solo los activos
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Seleccione una categoría",  # Puedes personalizar el texto del placeholder
    )
    proveedor = forms.ModelChoiceField(
        queryset=Proveedor.objects.filter(activo=True),  # Filtrar solo los activos
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Seleccione un proveedor",  # Puedes personalizar el texto del placeholder
    )
    
    class Meta:
        model = Producto
        fields = [
            'nombre', 
            'descripcion', 
            'cantidad_en_stock',
            'categoria',
            'proveedor',
            'precio_compra',
            'iva',
            'precio_venta',
            'unidad_medida',
        ]
        
        labels = {
            'nombre':'Nombre del Producto',
            'descripcion':'Descripcion',
            'cantidad_en_stock':'Cantidad en Stock',
            'categoria':'Categoria',
            'proveedor':'Proveedor',
            'precio_compra':'Precio Compra',
            'iva':'Tipo IVA',
            'precio_venta':'Precio Venta',
            'unidad_medida':'Unidad de Medida'
        }
        
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'cantidad_en_stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio_compra': forms.NumberInput(attrs={'class': 'form-control'}),
            'iva': forms.Select(attrs={'class': 'form-control'}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control'}),
            'unidad_medida': forms.Select(attrs={'class': 'form-control'})
        }
        
class ProductoViewForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['categoria','proveedor', 'nombre', 'descripcion', 'cantidad_en_stock','activo']   
        
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'disabled': True}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'disabled': True}),
            'cantidad_en_stock': forms.NumberInput(attrs={'class': 'form-control','disabled': True}),
            'categoria': forms.Select(attrs={'class': 'form-control','disabled': True}),
            'proveedor': forms.Select(attrs={'class': 'form-control','disabled': True}),
            'activo': forms.TextInput(attrs={'class': 'form-control', 'disabled': True}),
        }
        

#-------------------------------------------------------------------


class ProveedorForm(forms.ModelForm):
    
    documento = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Documento'}),
        label="Documento",
        help_text="Solo números, sin el dígito verificador"
    )
    digito_verificador = forms.ChoiceField(
        choices=[(str(i), str(i)) for i in range(10)],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="DV",
        required=False,  # No obligatorio por defecto
        help_text="Solo requerido para RUC"
    )

    class Meta:
        model = Proveedor
        fields = [
            'razon_social', 
            'representante',
            'direccion', 
            'codigo_pais',
            'num_tel',
            'correo',
            'descripcion',
            'tipo_documento',
        ]
        
        # SonarQube: exclude es necesario aquí porque nro_documento se calcula 
        # dinámicamente en base a documento + digito_verificador
        exclude = ['nro_documento'] 
        
        labels = {
            'razon_social': 'Nombre del Proveedor',
            'descripcion': 'Descripción',
            'direccion': 'Dirección',
            'codigo_pais': 'Prefijo Tel.',
            'num_tel': 'Teléfono',
            'correo': 'Email',
            'tipo_documento': 'Tipo de Documento',
            'representante': 'Representante Legal'
        }
        
        widgets = {
            'representante': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del representante legal'}),
            'razon_social': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Razón social'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control','rows': 3,'placeholder': 'Descripción del proveedor'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección'}),
            'codigo_pais': forms.Select(attrs={'class': 'form-control'}),
            'num_tel': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Ej: 981234567'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control','placeholder': 'correo@ejemplo.com'}),
            'tipo_documento': forms.Select(attrs={'class': 'form-control', 'onchange': 'toggleDigitoVerificador(this)'}),
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
        if Proveedor.objects.filter(nro_documento__iexact=nro_documento).exists():
            raise forms.ValidationError({'documento': 'Ya existe un proveedor con este número de documento.'})

        # Asignar el número de documento calculado al cleaned_data
        cleaned_data['nro_documento'] = nro_documento
        return cleaned_data

    def save(self, commit=True):
        # Sobrescribir el método save para guardar nro_documento
        instance = super().save(commit=False)
        cleaned_data = self.cleaned_data
        
        # Asignar el valor calculado
        instance.nro_documento = cleaned_data.get('nro_documento')  
        
        if commit:
            instance.save()
        return instance

class ProveedorViewForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['razon_social','nro_documento', 'direccion', 'num_tel', 'correo', 'descripcion','activo']   
        
        widgets = {
            'razon_social': forms.TextInput(attrs={'class': 'form-control', 'disabled': True}),
            'nro_documento': forms.TextInput(attrs={'class': 'form-control', 'disabled': True}), 
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'disabled': True}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'disabled': True}),
            'num_tel': forms.TextInput(attrs={'class': 'form-control', 'disabled': True}),
            'correo': forms.TextInput(attrs={'class': 'form-control', 'disabled': True}),
            'activo': forms.TextInput(attrs={'class': 'form-control', 'disabled': True}),
        }


class ProveedorEditForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = [
            'razon_social', 
            'direccion', 
            'codigo_pais',
            'num_tel',
            'correo',
            'descripcion',
            'nro_documento',
            'tipo_documento'
            
        ]
        
        labels = {
            'razon_social': 'Nombre del Proveedor',
            'descripcion': 'Descripción',
            'direccion': 'Dirección',
            'codigo_pais': 'Prefijo Tel.',
            'num_tel': 'Teléfono',
            'correo': 'Email',
            'tipo_documento': 'Tipo de Documento',
            'nro_documento':'Nro. Documento'
        }
        
        widgets = {
            'razon_social': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo_pais': forms.Select(attrs={'class': 'form-control'}),
            'num_tel': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'nro_documento': forms.TextInput(attrs={'class': 'form-control','readonly': True}),
            'tipo_documento': forms.TextInput(attrs={'class': 'form-control','readonly': True}),  
        }
        
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Si estamos editando, separar el número existente
        if self.instance and self.instance.pk and self.instance.num_tel:
            tel_completo = self.instance.num_tel
            
            # Buscar el prefijo en el número completo
            for prefijo, _ in self.PREFIJO_CHOICES:
                if tel_completo.startswith(prefijo):
                    self.fields['prefijo_tel'].initial = prefijo
                    self.fields['numero_tel'].initial = tel_completo.replace(prefijo, '')
                    break



class FormRegCompraCabecera(forms.ModelForm):
    
    iva_diez = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly','step': '0.01'}),
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
    
    proveedor = forms.ModelChoiceField(
        queryset=Proveedor.objects.filter(activo=True),
        empty_label="Seleccione un proveedor",
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Proveedor",
        to_field_name="id"  # Ensure the correct field is used for the value
    )
    
    descuento = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01','min': '0'}),
        label="Descuento",
        initial=0.0,
        min_value=0.0,
        decimal_places=2,
        max_digits=10
    )
    
    total = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly','step': '0.01'}),
        label="Total",
        initial=0.0,
        min_value=0.0,
        decimal_places=2,
        max_digits=100
    )
    
    class Meta:
        model = OrdenCompraCab
        
        
        fields = [
                'fecha_compra',
                'nro_comprobante',
                'proveedor',
                'total',
                'iva_diez',
                'iva_cinco',
                'descuento',
                'forma_pago'
            ]
        
        labels = {
            'fecha_compra':'Fecha',
            'nro_comprobante':'Nro. Comprobante',
            'forma_pago':'Forma de Pago',
        }
        
        widgets = {
            'fecha_compra': forms.DateTimeInput(attrs={'class': 'form-control','type': 'date'}),
            'forma_pago': forms.Select(attrs={'class': 'form-control'}),
            'nro_comprobante': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Ej: OC-2025-001'}),
        }
        
    '''def clean_nro_comprobante(self):
        """Validar que el número de comprobante sea único"""
        nro_comprobante = self.cleaned_data.get('nro_comprobante')
        
        if not nro_comprobante:
            raise ValidationError("El número de comprobante es obligatorio.")
        
        # Verificar unicidad
        existing = OrdenCompraCab.objects.filter(nro_comprobante__iexact=nro_comprobante)
        
        # Si estamos editando, excluir el registro actual
        if self.instance and self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)
        
        if existing.exists():
            raise ValidationError("Ya existe una orden con este número de comprobante.")
        
        return nro_comprobante.upper()  
    
    def clean_descuento(self):
        """Validar que el descuento no sea mayor al total"""
        descuento = self.cleaned_data.get('descuento', Decimal('0.0'))
        total = self.cleaned_data.get('total', Decimal('0.0'))
        
        if descuento < 0:
            raise ValidationError("El descuento no puede ser negativo.")
        
        if total > 0 and descuento > total:
            raise ValidationError("El descuento no puede ser mayor al total.")
        
        return descuento
    
    
    def clean(self):
        """Validaciones adicionales de la orden"""
        cleaned_data = super().clean()
        proveedor = cleaned_data.get('proveedor')
        total = cleaned_data.get('total', Decimal('0.0'))
        
        # Verificar que el proveedor esté activo
        if proveedor and not proveedor.activo:
            raise ValidationError({
                'proveedor': 'No se puede crear una orden para un proveedor desactivado.'
            })
            
        # Validar que el total sea mayor a 0 (para órdenes nuevas)
        if not self.instance.pk and total <= 0:
            raise ValidationError({
                'total': 'El total de la orden debe ser mayor a cero.'
            })
            
        return cleaned_data'''
        
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
            raise ValidationError("El total no puede ser negativo. Verifique las cantidades de los productos.")
        
        if total == 0:
            raise ValidationError("El total debe ser mayor a cero. Agregue productos a la orden.")
            
        return total
    
    def clean_iva_cinco(self):
        """Validar IVA 5%"""
        iva_cinco = self.cleaned_data.get('iva_cinco', Decimal('0.0'))
        
        if iva_cinco < 0:
            raise ValidationError("El IVA 5% no puede ser negativo. Verifique las cantidades de los productos.")
            
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
        proveedor = cleaned_data.get('proveedor')
        total = cleaned_data.get('total', Decimal('0.0'))
        descuento = cleaned_data.get('descuento', Decimal('0.0'))
        
        # Verificar que el proveedor esté activo
        if proveedor and not proveedor.activo:
            raise ValidationError({
                'proveedor': 'No se puede crear una orden para un proveedor inactivo. Seleccione un proveedor activo.'
            })
        
        # Validar relación entre descuento y total
        if total > 0 and descuento > total:
            raise ValidationError({
                'descuento': f'El descuento ({descuento}) no puede ser mayor al total ({total}).'
            })
            
        return cleaned_data
        
class FormRegCompraDetalle(forms.Form):
    """
    Formulario para el detalle de la orden de compra
    Usa Form en lugar de ModelForm para mayor flexibilidad
    """
                                    
    producto_id = forms.IntegerField(
        widget=forms.HiddenInput(attrs={'class': 'form-control'}),
        label="Producto ID"
    )
    
    descripcion = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        label="Descripción",
        required=False
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
    
    precio_compra = forms.DecimalField(
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
    
    
    '''def clean_cantidad(self):
        """Validar cantidad"""
        cantidad = self.cleaned_data.get('cantidad')
        
        if cantidad is None or cantidad <= 0:
            raise ValidationError("La cantidad debe ser un número entero mayor a cero.")
        
        return cantidad
    
    def clean_producto_id(self):
        """Validar que el producto existe y está activo"""
        producto_id = self.cleaned_data.get('producto_id')
        
        if not producto_id:
            raise ValidationError("Debe seleccionar un producto.")
        
        try:
            producto = Producto.objects.get(id=producto_id)
            if not producto.activo:
                raise ValidationError("No se puede agregar un producto desactivado.")
            return producto_id
        except Producto.DoesNotExist:
            raise ValidationError("Producto no encontrado.")'''
    
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
    
    def clean_precio_compra(self):
        """Validar precio de compra"""
        precio = self.cleaned_data.get('precio_compra')
        
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
    

class FormEditCompraCabecera(forms.ModelForm):
    
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
    
    proveedor = forms.ModelChoiceField(
        queryset=Proveedor.objects.filter(activo=True),
        empty_label="Seleccione un proveedor",
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Proveedor",
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
    
    class Meta:
        model = OrdenCompraCab
        
        
        fields = [
                'fecha_compra',
                'nro_comprobante',
                'proveedor',
                'total',
                'iva_diez',
                'iva_cinco',
                'descuento',
                'forma_pago'
            ]
        
        labels = {
            'fecha_compra':'Fecha',
            'nro_comprobante':'Nro. Comprobante',
            'forma_pago':'Forma de Pago',
        }
        
        widgets = {
            'fecha_compra': forms.DateInput(attrs={'class': 'form-control'}),
            'forma_pago': forms.Select(attrs={'class': 'form-control'}),
            'nro_comprobante': forms.TextInput(attrs={'class': 'form-control','readonly': 'readonly'}),
        }
        
    def clean_nro_comprobante(self):
        """Validar que el número de comprobante sea único"""
        nro_comprobante = self.cleaned_data.get('nro_comprobante')
        
        if not nro_comprobante:
            raise ValidationError("El número de comprobante es obligatorio.")
        
        # Verificar unicidad
        existing = OrdenCompraCab.objects.filter(nro_comprobante__iexact=nro_comprobante)
        
        # Si estamos editando, excluir el registro actual
        if self.instance and self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)
        
        if existing.exists():
            raise ValidationError("Ya existe una orden con este número de comprobante.")
        
        return nro_comprobante.upper()      
        
        
class FormEditCompraDetalle(forms.Form):
                                    
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
    
    precio_compra = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 
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
        if not self._validar_cantidad(cantidad, cleaned_data):
            return cleaned_data
          
        # Validar producto
        producto = self._validar_producto(producto_id, cleaned_data)
        if not producto:
            return cleaned_data
        
        # Validar stock
        self._validar_stock(producto, cantidad)
        
        return cleaned_data
    
    
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