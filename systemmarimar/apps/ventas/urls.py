from django.urls import path

from .import views

urlpatterns = [

    #path("registrar_venta", views.registrar_venta_cab_det, name="reg_venta"),
    path('login/', views.login_view, name='login'),
    path("", views.index, name="home"),
    #path("", views.index, name="index"),
    path("registrar_cliente", views.registrar_cliente, name="reg_cliente"),
    path("editar_cliente/<id_cliente>/", views.editar_cliente, name="edit_cliente"),
    path("editar_venta/<id_venta>/", views.editar_venta_v2, name="edit_venta"),
    path("cliente/inactivar/<id_cliente>/", views.inactivar_cliente, name="inact_cliente"),
    path("venta/inactivar/<id_venta>/", views.inactivar_venta, name="inact_venta"),
    path("listar_clientes/", views.listar_cliente, name="list_clientes"),
    #path("listar_ventas/", views.listar_ventas, name="list_ventas"),
    
    path("registrar_venta_model", views.reg_venta_modelo, name="reg_venta_model"),
    path("registrar_venta", views.registrar_venta, name="reg_venta"),
    path("listar_ventas/", views.listar_ventas, name="list_ventas"),
    #path("/buscar-productos/", views.buscar_productos, name="buscar_productos"),
    path('buscar-productos/', views.buscar_productos, name='buscar_productos'),
]