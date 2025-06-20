from django.shortcuts import render
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib.auth.models import Group
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from apps.administrador.forms import SetPasswordForm, UsuarioForm, UsuarioPassForm, UsuarioChangeForm, GroupForm, GroupViewForm
from django.contrib.auth.models import Group, Permission
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from django.contrib.auth.forms import SetPasswordForm

# Create your views here.


'''def login_user(request):
    if request.method == "POST":
        usuario = request.POST['username']  
        password = request.POST['password']
        user = authenticate(request, username=usuario, password=password)
        # Si existe un usuario con ese nombre y contraseña
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('home')
            else:
                return HttpResponse('Su usuario no esta activo')
                #return messages.error(request,("El usuario no esta activo"))
               
        else:
            messages.info(request,("Error al iniciar sesion, intente de nuevo"))
            return redirect('login')
    else:
        return render(request,'usuario/login.html',{})'''
    
    
def login_user(request):
    if request.method == "POST":
        usuario = request.POST.get('username', '').strip()  # Usar get() para evitar KeyError y strip() para limpiar
        password = request.POST.get('password', '').strip()
        
        # Validación básica de campos vacíos
        if not usuario or not password:
            messages.error(request, "Por favor, complete todos los campos")
            return redirect('login')
            
        user = authenticate(request, username=usuario, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Su cuenta está inactiva. Contacte al administrador.")
        else:
            messages.error(request, "Usuario o contraseña incorrectos. Intente nuevamente.")
        
        return redirect('login')
    
    return render(request, 'usuario/login.html', {})
    

@login_required(login_url='login/')
def index(request):
    return render(request, 'index.html', {})



@login_required(login_url='login/')
@permission_required('administrador.add_user', raise_exception=True)
def registrar_usuario(request):
    #registered = False
    if request.method == 'POST':

        form = UsuarioForm(request.POST)
        #form.fields['username'].help_text = None
        form.fields['password1'].help_text = None
        form.fields['password2'].help_text = None
 
        if form.is_valid():
            form2=form.save(commit=False)
            #user = form.save()
            form2.save()
            form.save_m2m()
            
            messages.success(request,"Usuario Registrado Exitosamente")
            return redirect('list_users')

        return render(request, 'administrador/crear_usuario.html',{'form': form})

    else:
        
        form = UsuarioForm()
        #form.fields['username'].help_text = None
        form.fields['password1'].help_text = None
        form.fields['password2'].help_text = None
   
    return render(request, 'administrador/crear_usuario.html',{'form': form})


@login_required(login_url='login/')
@permission_required('usuario.change_user', raise_exception=True)
def editar_usuario(request, id_usuario):
    # Recuperamos la instancia de la persona
    instancia = User.objects.get(id=id_usuario)

    if request.method == "GET":
        # Actualizamos el formulario con los datos recibidos
        form = UsuarioChangeForm(instance=instancia)
    else:
        form = UsuarioChangeForm(request.POST,instance=instancia)
        

        if form.is_valid():
            #form2=form.save(commit=False)
            #form2.save()
            #form.save_m2m()
            form.save()
            messages.success(request,("Usuario Modificado Exitosamente"))
            return redirect('list_users')

    return render(request, 'administrador/editar_usuario.html',{'form': form})


def reset_password(request, id_usuario):
    # Recuperamos la instancia de la persona
    instancia = User.objects.get(id=id_usuario)
    # Si el usuario no existe, redirigimos a la lista de usuarios
    if not instancia:
        messages.error(request,("Usuario no encontrado"))
        return redirect('list_users')
    # Si el usuario existe, mostramos el formulario de cambio de contraseña
    if request.method == 'POST':
        form = SetPasswordForm(request.user, request.POST)
        form.fields['new_password1'].help_text = None
        form.fields['new_password2'].help_text = None
        if form.is_valid():
            form.save()
            messages.success(request,("Su contraseña fue cambiado exitosamente"))
            return redirect('login')
        else:
            for error in list(form.errors.values()):
                messages.error(request,error)
    else:
        form = SetPasswordForm(request.user)
        form.fields['new_password1'].help_text = None
        form.fields['new_password2'].help_text = None
    return render(request, 'usuario/password_reset_confirm.html', {'form': form})

@login_required(login_url='login/')
@permission_required('usuario.delete_user', raise_exception=True)
def delete_usuario(request, id_usuario):
    # Recuperamos la instancia de la persona
    instancia = User.objects.get(id=id_usuario)

    if request.method == "POST":
        instancia.delete()
        messages.success(request,("Usuario eliminado exitosamente"))
        return redirect('list_users')

    return render(request, 'administrador/listar_usuario.html', {'Usuario': instancia})


@login_required(login_url='login/')
#@permission_required('usuario.view_usuario', raise_exception=True)
def listar_usuarios(request):
    usuario = User.objects.filter(is_active=True).order_by('id')
    #print(usuario)
    contexto = {'Usuarios': usuario}
    return render(request, 'administrador/listar_usuario.html', contexto) 


@login_required(login_url='login/')
def logout_user(request):

    #Si realiza el logout le muestra un mensaje
    logout(request)
    messages.info(request, ("Se encuentra desconectado"))

    #Le redirecciona al login nuevamente
    return redirect('login')



@login_required(login_url='/login_user')
#@allowed_users(allowed_roles=['Administrador'])
@permission_required('usuario.change_user', raise_exception=True)
def editar_contraseña_con_admin(request, id_usuario):
    # Recuperamos la instancia de la persona
    instancia = User.objects.get(id=id_usuario)

    if request.method == "GET":
        # Actualizamos el formulario con los datos recibidos
        form = UsuarioPassForm(instance=instancia)
    else:
        form = UsuarioPassForm(request.POST,instance=instancia)
        

        if form.is_valid():
            #form2=form.save(commit=False)
            #form2.save()
            #form.save_m2m()
            form.save()
            messages.success(request,("Contraseña Modificado Exitosamente"))
            return redirect('list_users')

    return render(request, 'usuario/user_edit.html',{'form': form})


@login_required(login_url='/login_user')
#@allowed_users(allowed_roles=['Administrador'])
@permission_required('usuario.change_user', raise_exception=True)
def editar_contraseña(request, id_usuario):
    # Recuperamos la instancia de la persona
    instancia = User.objects.get(id=id_usuario)
    #instancia.set_password()
    #instancia.save()
    #return redirect('list_users')
    if request.method == 'POST':
        form = SetPasswordForm(instancia,request.POST)
        form.fields['new_password1'].help_text = None
        form.fields['new_password2'].help_text = None
        if form.is_valid():
            form.save()
            #message = _('Status of %(discount_code)s ticket has been successfully updated.') % {'discount_code': discount.code}
            #messages.success(self.request, message)
            #message =('Contraseña del usuario %(username) ha sido cambiado exitosamente.') % {'username': instancia.username}
            messages.success(request,("La contraseña fue cambiado exitosamente para el usuario"))
            #messages.success(request, message)
            return redirect('list_users')
        else:
            for error in list(form.errors.values()):
                messages.error(request,error)
    form = SetPasswordForm(instancia)
    form.fields['new_password1'].help_text = None
    form.fields['new_password2'].help_text = None
    return render(request,'usuario/password_reset_confirm.html',{'form':form})


@login_required(login_url='/login_user')
def cambiar_contraseña(request):
    if request.method == 'POST':
        form = SetPasswordForm(request.user,request.POST)
        form.fields['new_password1'].help_text = None
        form.fields['new_password2'].help_text = None
        if form.is_valid():
            form.save()
            messages.success(request,("Su contraseña fue cambiado exitosamente"))
            return redirect('login')
        else:
            for error in list(form.errors.values()):
                messages.error(request,error)
    form = SetPasswordForm(request.user)
    form.fields['new_password1'].help_text = None
    form.fields['new_password2'].help_text = None
    return render(request,'usuario/password_reset_confirm.html',{'form':form})



@login_required(login_url='/login_user')
def cambiar_contraseña_usuario(request):
    if request.method == 'POST':
        form = SetPasswordForm(request.user,request.POST)
        form.fields['new_password1'].help_text = None
        form.fields['new_password2'].help_text = None
        if form.is_valid():
            form.save()
            messages.success(request,("Su contraseña fue cambiado exitosamente"))
            return redirect('home')
        else:
            for error in list(form.errors.values()):
                messages.error(request,error)
    form = SetPasswordForm(request.user)
    form.fields['new_password1'].help_text = None
    form.fields['new_password2'].help_text = None
    return render(request,'usuario/password_reset_confirm.html',{'form':form})


@login_required(login_url='/login_user')
def listar_grupos(request):
    grupos = Group.objects.all()
    permisos = []

    for grupo in grupos:
        permisos.append({
            'grupo': grupo,
            'permisos': grupo.permissions.all(),
        })

    contexto = {
        'Grupos': grupos,
        'Permisos': permisos,
        'perms': Permission.objects.all().order_by('name'),  # todos los permisos del sistema
    }
    return render(request, 'administrador/listar_roles.html', contexto)

@login_required(login_url='/login_user')
def crear_grupo(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,("Grupo creado exitosamente"))
            return redirect('list_groups')
    else:
        form = GroupForm()
    return render(request, 'administrador/crear_rol.html', {'form': form})



@login_required(login_url='login/')
@permission_required('auth.change_group', raise_exception=True)
def actualizar_permisos_grupo(request, grupo_id):
    grupo = get_object_or_404(Group, id=grupo_id)

    if request.method == 'POST':
        permisos_ids = request.POST.getlist('permisos')  # lista de IDs de permisos
        nuevos_permisos = Permission.objects.filter(id__in=permisos_ids)
        grupo.permissions.set(nuevos_permisos)  # actualiza permisos
        messages.success(request, f'Permisos del grupo "{grupo.name}" actualizados.')
        return redirect('listar_grupos')  # ajusta con tu nombre de URL

    return redirect('listar_grupos')



def editar_grupo(request, id_grupo):
    grupo = Group.objects.get(id=id_grupo)
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=grupo)
        if form.is_valid():
            form.save()
            messages.success(request,("Grupo modificado exitosamente"))
            return redirect('list_groups')
    else:
        form = GroupForm(instance=grupo)
    return render(request, 'administrador/editar_rol.html', {'form': form, 'grupo': grupo})