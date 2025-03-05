from django import forms


'''class FormRegistrarCliente(forms.ModelForm):
    
    class Meta:
        model = Cliente
        
         
        fields = [
            'nombre',
			'apellido',
            'nro_documento',
            'nacionalidad',
            'estado_civil',
            'num_tel',
            'correo',
            'direccion',
            #'activo',
		]
        
        labels = {
            'nombre':'Nombre',
            'apellido':'Apellido',
            'nro_documento':'Nro. Documento',
            'nacionalidad':'Nacionalidad',
            'estado_civil':'Estado Civil',
            'num_tel':'Num.Telefono',
            'correo':'Correo',
            'direccion':'Direccion',
            #'fecha_insercion':'Fecha de Insercion',
		}
        
        widgets = {
            'nombre':forms.TextInput(attrs={'class':'form-control'}),
            'apellido':forms.TextInput(attrs={'class':'form-control'}),
            'nro_documento':forms.TextInput(attrs={'class':'form-control'}),
            'nacionalidad':forms.TextInput(attrs={'class':'form-control'}),
            'estado_civil':forms.TextInput(attrs={'class':'form-control'}),
            'num_tel':forms.TextInput(attrs={'class':'form-control'}),
            'correo':forms.EmailInput(attrs={'class':'form-control'}),
            'direccion':forms.TextInput(attrs={'class':'form-control'}),
            #'fecha_insercion': forms.DateInput(attrs={'class':'form-control'}),
            #'activo':forms.CheckboxInput(attrs={'class':'form-control'}),
		}
        
        
class FormEditarCliente(forms.ModelForm):
    
    class Meta:
        model = Cliente
        
         
        fields = [
            'nombre',
			'apellido',
            'nro_documento',
            'nacionalidad',
            'estado_civil',
            'num_tel',
            'correo',
            'direccion',
            #'activo',
		]
        
        labels = {
            'nombre':'Nombre',
            'apellido':'Apellido',
            'nro_documento':'Nro. Documento',
            'nacionalidad':'Nacionalidad',
            'estado_civil':'Estado Civil',
            'num_tel':'Num.Telefono',
            'correo':'Correo',
            'direccion':'Direccion',
            #'fecha_insercion':'Fecha de Insercion',
		}
        
        widgets = {
            'nombre':forms.TextInput(attrs={'class':'form-control'}),
            'apellido':forms.TextInput(attrs={'class':'form-control'}),
            'nro_documento':forms.TextInput(attrs={'class':'form-control'}),
            'nacionalidad':forms.TextInput(attrs={'class':'form-control'}),
            'estado_civil':forms.TextInput(attrs={'class':'form-control'}),
            'num_tel':forms.TextInput(attrs={'class':'form-control'}),
            'correo':forms.EmailInput(attrs={'class':'form-control'}),
            'direccion':forms.TextInput(attrs={'class':'form-control'}),
            #'fecha_insercion': forms.DateInput(attrs={'class':'form-control'}),
            #'activo':forms.CheckboxInput(attrs={'class':'form-control'}),
		}'''