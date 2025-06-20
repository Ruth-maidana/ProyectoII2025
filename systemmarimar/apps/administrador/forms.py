from django.contrib.auth.forms import UserCreationForm,UserChangeForm,SetPasswordForm
from cProfile import label
from logging import PlaceHolder
from django.contrib.auth.models import Group, User, Permission
from tkinter import Widget
#from tokenize import group
#from wsgiref import validate
#from xml.dom import minidom
from django import forms
from django.contrib.auth.forms import UserCreationForm,UserChangeForm,SetPasswordForm
from django.contrib.auth.forms import ReadOnlyPasswordHashField


class UsuarioForm(UserCreationForm):

	class Meta:
		model = User
  
		fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'groups']
  

class UsuarioChangeForm(UserChangeForm):
	class Meta:
		model = User
		fields = ['username', 'first_name', 'last_name', 'email', 'password','is_active', 'groups']


class SetPasswordForm(SetPasswordForm):

	class Meta:
		model = User
		fields = [
			"username",
			"new_password1",
			"new_password2",
			]
		

class UsuarioPassForm(forms.ModelForm):
	username = forms.CharField(label="Usuario",widget=forms.TextInput(attrs={"class":"form-control","placeholder":"Nombre de usuario"}))
	password1 = forms.CharField(label="Contraseña",widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder': 'Contraseña'}))
	password2 = forms.CharField(label="Confirmacion de Contraseña",widget=forms.PasswordInput(attrs={'class':'form-control',"placeholder":"Confirmacion de Contraseña"}))
	class Meta:
		model = User
		fields = [
			"username",
			"password1",
			"password2",
			#"activo",
			]



class GroupForm(forms.ModelForm):
	permissions = forms.ModelMultipleChoiceField(
		queryset=Permission.objects.all(),
		widget=forms.CheckboxSelectMultiple,
		required=False,
		label="Permisos"
	)
	class Meta:
		model = Group
		fields = ['name', 'permissions']
		labels = {
			'name': 'Nombre del Grupo',
		}
		widgets = {
			'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del Grupo'}),
		}
  
	
class GroupViewForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
		queryset=Permission.objects.all(),
		widget=forms.CheckboxSelectMultiple,
		required=False,
		label="Permisos"
	)
    
    class Meta:
        model = Group
        fields = ['name', 'permissions']
        labels = {
			'name': 'Nombre del Grupo',
		}
        widgets = {
			'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del Grupo'}),
		}