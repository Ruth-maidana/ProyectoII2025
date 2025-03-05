from django.shortcuts import render,redirect
from django.contrib import messages
#from .forms import FormRegistrarCliente,FormEditarCliente
#from .models import Cliente

# Create your views here.

#@login_required(login_url='/login_user')
#@permission_required('oficina.add_oficina', raise_exception=True)
'''
def registrar_cliente(request):
    
	if request.method == 'POST':
     
		form_reg_cliente = FormRegistrarCliente(request.POST)
  
		if form_reg_cliente.is_valid():
      
            #datetime.date.today()
            #datetime.datetime.now().date()
            #datetime.datetime.now().time()
      
			form_reg_cliente.save()
   
			messages.success(request,("Cliente Registrado Exitosamente"))
			return redirect('listar_cliente')   
 
		else:
			messages.error(request,("Error, Cliente ya registado"))   
     
	else:
		form_reg_cliente = FormRegistrarCliente()
  
	#return render(request, 'sucursal/cargar_oficina.html',{'form': form_cargar_sucursal})
	return render(request, 'clientes/registrar.html',{'form': form_reg_cliente})




#@login_required(login_url='/login_user')
#@permission_required('oficina.change_oficina', raise_exception=True)
def editar_cliente(request, id_cliente):
	
	# Recuperamos la instancia del proyecto
	instancia = Cliente.objects.get(id=id_cliente)

	if request.method == "GET":
		# Actualizamos el formulario con los datos recibidos
		form_edit_cliente = FormEditarCliente(instance=instancia)
		print("Obtiene los datos")
  
	else:
     
		form_edit_cliente = FormEditarCliente(request.POST,instance=instancia)
		print("Realiza la modificacion")
  
		if form_edit_cliente.is_valid():
      
			form_edit_cliente.save()
			print("Modificado exitosamente")
			messages.success(request,("Cliente Modificado Exitosamente"))
   
			return redirect('listar_cliente')

		else:
			messages.error(request,("Error, Verifique los campos"))
			print("Error en el campo")

   
	return render(request, 'clientes/editar.html',{'form': form_edit_cliente})



#@login_required(login_url='/login_user')
#@permission_required('oficina.delete_oficina', raise_exception=True)
def inactivar_cliente(request,id_cliente):
    
	cliente = Cliente.objects.get(id = id_cliente)
 
	cliente.activo=False
 
	messages.success(request,"Cliente eliminado correctamente")
	cliente.save()
 
	return redirect('listar_cliente')


#@login_required(login_url='/login_user')
#@permission_required('oficina.view_oficina', raise_exception=True)
def listar_cliente(request):
	#oficina = Oficina.objects.filter(activo=True)
	cliente = Cliente.objects.all()
 
	return render(request, 'clientes/listar.html',{'Cliente': cliente})
 '''
 
def index (request):
    return render(request, 'index.html',{})