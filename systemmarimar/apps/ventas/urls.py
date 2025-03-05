from django.urls import path

from .import views

urlpatterns = [

    path("", views.index, name="index"),
    #path("registrar_cliente/", views.registrar_cliente, name="reg_cliente"),
    #path("editar_cliente/<id_oficina>/", views.editar_cliente, name="edit_cliente"),
    #path("listar_cliente/", views.listar_cliente, name="listar_cliente"),
    
    
]