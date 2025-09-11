from django.urls import path

from .import views

urlpatterns = [

    #path("registrar", views.registrar_compra, name="registrar_compra"),
    path("registrar_compra", views.registrar_compra_cab_det_version_act_v2, name="reg_compra"),
    path("registrar_producto", views.registrar_producto, name="reg_producto"),
    path("registrar_categoria", views.registrar_categoria, name="reg_categoria"),
    path("registrar_proveedor", views.registrar_proveedor, name="reg_proveedor"),
    path('buscar-productos/', views.buscar_productos, name='buscar_productos'),

    #----------------------------------------------------------------
    path("editar_producto/<id_producto>/", views.editar_producto, name="edit_producto"),
    path("editar_categoria/<id_categoria>/", views.editar_categoria, name="edit_categoria"),
    path("editar_proveedor/<id_proveedor>/", views.editar_proveedor, name="edit_proveedor"),
    path("editar_compra/<id_compra>/", views.editar_compra, name="edit_compra"),
    #path("editar_compra_detalle/<id_compra_detalle>/", views.editar_compra_detalle, name="edit_compra_detalle"),
    #----------------------------------------------------------------
    path("categoria/inactivar/<id_categoria>/", views.inactivar_categoria, name="inact_categoria"),
    path("proveedor/inactivar/<id_proveedor>/", views.inactivar_proveedor, name="inact_proveedor"),
    path("producto/inactivar/<id_producto>/", views.inactivar_producto, name="inact_producto"),
    path("compra/inactivar/<id_compra>/", views.inactivar_compra, name="inact_compra"),
    #path('obtener_datos_producto/', views.obtener_datos_producto, name='obtener_datos_producto'),
    
    #----------------------------------------------------------------
    path("listar_proveedores/", views.listar_proveedores, name="list_proveedores"),
    path("listar_productos/", views.listar_productos, name="list_productos"),
    path("listar_categorias/", views.listar_categorias, name="list_categorias"),
    path("listar_compras/", views.listar_compras, name="list_compras"),
    path("reporte_compras/", views.reporte_compras, name="reporte_compras"),
    path("reporte_compras_pdf/", views.exportar_compras_pdf, name="reporte_compras_pdf"),
    path("reporte_compras_mens_anual/", views.rep_compras_mensual_anual_v2, name="reporte_compra_men_anual"),
    path("reporte_compras_mens_anual_pdf/", views.exportar_compras_mensual_anual_pdf, name="rep_compra_men_anual_pdf"),
    
]