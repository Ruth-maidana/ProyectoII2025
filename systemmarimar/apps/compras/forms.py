from django import forms
from django.forms import inlineformset_factory
from .models import Producto, OrdenCompraCab, OrdenCompraDet, Categoria, Proveedor
from apps.compras.utils import validar_stock_compra
from django.core.exceptions import ValidationError



class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']
        exclude = ['fecha_insercion', 'activo']  # Excluir el campo fecha_insercion

        
        '''def clean_nombre(self):
            nombre = self.cleaned_data['nombre'].strip().upper()  # Convertir a mayúsculas
            print('Entro en el form '+nombre)
            if Categoria.objects.filter(nombre=nombre).exists():
                raise forms.ValidationError("Ya existe una categoría con este nombre.")
            return nombre'''
            
        '''def clean_nombre(self):
            nombre = self.cleaned_data['nombre']
            if Categoria.objects.filter(nombre__iexact=nombre).exists():
                raise forms.ValidationError('Este nombre ya existe (sin distinguir mayúsculas o minúsculas).')
            return nombre'''


class CategoriaEditForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']
        exclude = ['fecha_insercion', 'activo']  # Excluir el campo fecha_insercion

class CategoriaViewForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion', 'fecha_insercion', 'activo']
        
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'disabled': True}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'disabled': True}),
            'fecha_insercion': forms.TextInput(attrs={'class': 'form-control', 'disabled': True}),
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
        exclude = ['fecha_insercion', 'activo']  # Excluir el campo fecha_insercion
        
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
            'iva': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control'}),
            'unidad_medida': forms.Select(attrs={'class': 'form-control'}),
            #'activo': forms.CheckboxInput(attrs={'class': 'form-control'}),
            #'categoria': forms.Select(attrs={'class': 'form-control'}),
            #'proveedor': forms.Select(attrs={'class': 'form-control'}),
        }
        
class ProductoViewForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['categoria','proveedor', 'nombre', 'descripcion', 'cantidad_en_stock','activo', 'fecha_insercion']   
        
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'disabled': True}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'disabled': True}),
            'cantidad_en_stock': forms.NumberInput(attrs={'class': 'form-control','disabled': True}),
            'categoria': forms.Select(attrs={'class': 'form-control','disabled': True}),
            'proveedor': forms.Select(attrs={'class': 'form-control','disabled': True}),
            'fecha_insercion': forms.TextInput(attrs={'class': 'form-control', 'disabled': True}),
            'activo': forms.TextInput(attrs={'class': 'form-control', 'disabled': True}),
        }
        

#-------------------------------------------------------------------


class ProveedorForm(forms.ModelForm):
    #nro_documento = forms.CharField(widget=forms.HiddenInput(), required=False)
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
        model = Proveedor
        fields = [
            'razon_social', 
            'direccion', 
            'num_tel',
            'correo',
            'descripcion',
            'tipo_documento',
        ]
        exclude = ['fecha_insercion', 'activo','nro_documento']  # Excluir nro_documento porque será calculado
        
        labels = {
            'razon_social': 'Nombre del Proveedor',
            'descripcion': 'Descripción',
            'direccion': 'Dirección',
            'num_tel': 'Teléfono',
            'correo': 'Email',
            'tipo_documento': 'Tipo de Documento'
        }
        
        widgets = {
            'razon_social': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'num_tel': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
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
        instance.nro_documento = cleaned_data.get('nro_documento')  # Asignar el valor calculado
        if commit:
            instance.save()
        return instance

class ProveedorViewForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['razon_social','nro_documento', 'direccion', 'num_tel', 'correo', 'descripcion','activo', 'fecha_insercion']   
        
        widgets = {
            'razon_social': forms.TextInput(attrs={'class': 'form-control', 'disabled': True}),
            'nro_documento': forms.TextInput(attrs={'class': 'form-control', 'disabled': True}), 
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'disabled': True}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'disabled': True}),
            'num_tel': forms.TextInput(attrs={'class': 'form-control', 'disabled': True}),
            'correo': forms.TextInput(attrs={'class': 'form-control', 'disabled': True}),
            'fecha_insercion': forms.TextInput(attrs={'class': 'form-control', 'disabled': True}),
            'activo': forms.TextInput(attrs={'class': 'form-control', 'disabled': True}),
        }


class ProveedorEditForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = [
            'razon_social', 
            'direccion', 
            'num_tel',
            'correo',
            'descripcion',
            'nro_documento',
            'tipo_documento'
            
        ]
        exclude = ['fecha_insercion', 'activo']  # Excluir nro_documento porque será calculado
        
        labels = {
            'razon_social': 'Nombre del Proveedor',
            'descripcion': 'Descripción',
            'direccion': 'Dirección',
            'num_tel': 'Teléfono',
            'correo': 'Email',
            'tipo_documento': 'Tipo de Documento',
            'nro_documento':'Nro. Documento'
        }
        
        widgets = {
            'razon_social': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'num_tel': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'nro_documento': forms.TextInput(attrs={'class': 'form-control','readonly': True}),
            'tipo_documento': forms.TextInput(attrs={'class': 'form-control','readonly': True}),  
        }


class CompraCabEditForm(forms.ModelForm):
        
    class Meta:
        model = OrdenCompraCab
        
        fields = [
            'nro_comprobante', 
            'fecha_compra', 
            'proveedor',  
            'total',
            'forma_pago',
            'descuento',
            'iva_diez',
            'iva_cinco'
        ]
        
        exclude = ['activo', 'fecha_insercion']  # Excluir el campo fecha_insercion
        
        labels = {
            'nro_comprobante':'Numero de Comprobante',
            'fecha_compra':'Fecha de Compra',
            'proveedor':'Proveedor',
            'total':'Total Gral.',
            'forma_pago':'Forma de Pago',
            'descuento':'Descuento',
            'iva_diez':'IVA 10%',
            'iva_cinco':'IVA 5%'
        }
        
        widgets = {
            'nro_comprobante':forms.TextInput(attrs={'class':'form-control'}),
            'fecha_compra':forms.DateInput(attrs={'class':'form-control'}),
            'proveedor':forms.Select(attrs={'class':'form-control'}),
            'total':forms.NumberInput(attrs={'class':'form-control'}),
            'forma_pago':forms.Select(attrs={'class':'form-control'}),
            'descuento':forms.NumberInput(attrs={'class':'form-control'}),
            'iva_diez':forms.NumberInput(attrs={'class':'form-control'}),
            'iva_cinco':forms.NumberInput(attrs={'class':'form-control'}),
        }
        



class CompraCabForm(forms.ModelForm):
        
    class Meta:
        model = OrdenCompraCab
        
        fields = [
            'nro_comprobante', 
            'fecha_compra', 
            'proveedor',  
            'total',
            'forma_pago',
            'descuento',
            'iva_diez',
            'iva_cinco'
        ]
        
        exclude = ['activo', 'fecha_insercion']  # Excluir el campo fecha_insercion
        
        labels = {
            'nro_comprobante':'Numero de Comprobante',
            'fecha_compra':'Fecha de Compra',
            'proveedor':'Proveedor',
            'total':'Total Gral.',
            'forma_pago':'Forma de Pago',
            'descuento':'Descuento',
            'iva_diez':'IVA 10%',
            'iva_cinco':'IVA 5%'
        }
        
        widgets = {
            'nro_comprobante':forms.TextInput(attrs={'class':'form-control','required':'El campo nro. orden es requerido'}),
            'fecha_compra':forms.DateInput(attrs={'class':'form-control','type':'date','required':'El campo fecha de compra es requerido'}),
            'proveedor':forms.Select(attrs={'class':'form-control','required':'El campo proveedor es requerido'}),
            'total':forms.NumberInput(attrs={'class':'form-control'}),
            'forma_pago':forms.Select(attrs={'class':'form-control','required':'El campo forma de pago es requerido'}),
            'descuento':forms.NumberInput(attrs={'class':'form-control','required':'El campo descuento es requerido'}),
            'iva_diez':forms.NumberInput(attrs={'class':'form-control','required':'El campo iva es requerido'}),
            'iva_cinco':forms.NumberInput(attrs={'class':'form-control','required':'El campo iva es requerido'}),
        }
        
        
class CompraDetForm(forms.ModelForm):
    
    '''def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.producto:
            self.fields['precio_compra'].initial = self.instance.producto.precio_compra
            self.fields['unidad_medida'].initial = self.instance.producto.unidad_medida
            self.fields['descripcion'].initial = self.instance.producto.descripcion'''
    
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.filter(activo=True),  # Filtrar solo los activos
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Seleccione un producto",  # Puedes personalizar el texto del placeholder
    )
    
    '''cantidad = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        initial=0,
        min_value=0
    )'''
    
    class Meta:
        model = OrdenCompraDet
        
        fields = [
            'producto',
            'cantidad',
            'precio_compra',
            'unidad_medida',
            #'descuento',
            'total_producto',
            'descripcion'
        ]
        
        label = {
            #'producto':'Producto',
            'cantidad':'Cantidad',
            'precio_compra':'Precio Compra',
            'unidad_medida':'Unidad de Medida',
            #'descuento':'Descuento',
            'total_producto':'Total',
            'descripcion':'Descripcion'
        }
        
        widgets = {
            #'producto':forms.Select(attrs={'class':'form-control','required':'El campo producto es requerido'}),
            'cantidad':forms.NumberInput(attrs={'class':'form-control','required':'El campo precio de compra es requerido'}),
            'precio_compra':forms.NumberInput(attrs={'class':'form-control','required':'El campo precio de compra es requerido'}),
            'unidad_medida':forms.Select(attrs={'class':'form-control','required':'El campo unidad de medida es requerido'}),
            #'descuento':forms.NumberInput(attrs={'class':'form-control','required':'El campo descuento es requerido'}),
            'total_producto':forms.NumberInput(attrs={'class':'form-control','required':'El campo total es requerido'}),
            'descripcion':forms.TextInput(attrs={'class':'form-control','required':'El campo descripcion es requerido'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')
        cantidad = cleaned_data.get('cantidad')  # Valor por defecto si no se proporciona cantidad
            
        if producto and cantidad:
            try:
                validar_stock_compra(producto, cantidad)  # Función de utils.py
            except ValidationError as e:
                self.add_error('cantidad', e)  # ¡Error vinculado al campo!
            
            # Calcular el total del producto
        '''precio_compra = cleaned_data.get('precio_compra')
            total_producto = precio_compra * cantidad
            cleaned_data['total_producto'] = total_producto'''
       
        return cleaned_data
   
#inlienformset_factory es una funcion que permite crear un formulario de detalle de una cabecera
#en este caso se esta creando un formulario de detalle de una orden de compra   
CompraFormset = inlineformset_factory(OrdenCompraCab, OrdenCompraDet, form=CompraDetForm, extra=1,can_delete=True)




class FiltroComprasForm(forms.Form):
    fecha_inicio = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    fecha_fin = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    proveedor = forms.ModelChoiceField(queryset=Proveedor.objects.all(), required=False)


class FormRegCompraCabecera(forms.ModelForm):
    
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
        
        exclude = ['fecha_insercion','activo']
        
        labels = {
            'fecha_compra':'Fecha de Compra',
            'nro_comprobante':'Nro. Comprobante',
            'forma_pago':'Forma de Pago',
        }
        
        widgets = {
            'fecha_compra': forms.DateTimeInput(attrs={'class': 'form-control','type': 'date'}),
            'forma_pago': forms.Select(attrs={'class': 'form-control'}),
            'nro_comprobante': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
        
class FormRegCompraDetalle(forms.Form):
                                    
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
        
        if cantidad is None or cantidad <= 0:
            self.add_error('cantidad',"La cantidad debe ser un número entero mayor a cero.")
            return cleaned_data  # Retornar aquí para evitar continuar con la validación
        
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
        
        exclude = ['fecha_insercion','activo']
        
        labels = {
            'fecha_compra':'Fecha de Compra',
            'nro_comprobante':'Nro. Comprobante',
            'forma_pago':'Forma de Pago',
        }
        
        widgets = {
            'fecha_compra': forms.DateInput(attrs={'class': 'form-control'}),
            'forma_pago': forms.Select(attrs={'class': 'form-control'}),
            'nro_comprobante': forms.TextInput(attrs={'class': 'form-control','readonly': 'readonly'}),
        }
        
        
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
        
        if cantidad is None or cantidad <= 0:
            self.add_error('cantidad',"La cantidad debe ser un número entero mayor a cero.")
            return cleaned_data  # Retornar aquí para evitar continuar con la validación
        
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