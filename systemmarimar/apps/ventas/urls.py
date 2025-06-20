from django.urls import path

from .import views

urlpatterns = [

    path("registrar_cliente", views.registrar_cliente, name="reg_cliente"),
    path("editar_cliente/<id_cliente>/", views.editar_cliente, name="edit_cliente"),
    path("listar_clientes/", views.listar_cliente, name="list_clientes"),
    path("cliente/inactivar/<id_cliente>/", views.inactivar_cliente, name="inact_cliente"),
    
    path("registrar_venta", views.registrar_venta, name="reg_venta"),
    path("editar_venta/<id_venta>/", views.editar_venta_v3, name="edit_venta"),  #editar_venta_v2
    path("listar_ventas/", views.listar_ventas, name="list_ventas"),
    path("venta/inactivar/<id_venta>/", views.inactivar_venta, name="inact_venta"),
    path('venta/buscar-productos/', views.buscar_productos, name='venta_buscar_productos'),
    
    path('reporte_ventas/', views.reporte_ventas, name='reporte_ventas'),
    path('reporte_ventas_pdf/', views.exportar_ventas_pdf, name='reporte_ventas_pdf'),
    path('reporte_ventas_mens_anual/', views.rep_ventas_mensual_anual, name='reporte_venta_men_anual'),
    path('reporte_ventas_mens_anual_pdf/', views.exportar_ventas_mensual_anual_pdf, name='exp_ventas_mens_anual_pdf'),
    path('config_timbrado_numeracion/', views.registrar_config_tim_num, name='config_timbrado_num'),
]