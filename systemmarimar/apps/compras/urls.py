from django.urls import path

from .import views

urlpatterns = [

    #path("registrar", views.registrar_compra, name="registrar_compra"),
    path("registrar_compra", views.registrar_compra_cab_det_version_act, name="reg_compra"),
    path("registrar_producto", views.registrar_producto, name="reg_producto"),
    path("registrar_categoria", views.registrar_categoria, name="reg_categoria"),
    path("registrar_proveedor", views.registrar_proveedor, name="reg_proveedor"),
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
    path("compra/inactivar/<id_producto>/", views.inactivar_producto, name="inact_compra"),
    
    
    #----------------------------------------------------------------
    path("listar_proveedores/", views.listar_proveedores, name="list_proveedores"),
    path("listar_productos/", views.listar_productos, name="list_productos"),
    path("listar_categorias/", views.listar_categorias, name="list_categorias"),
    path("listar_compras/", views.listar_compras, name="list_compras"),
    #path("listar_compras_detalle/", views.listar_compras_detalle, name="list_compras_detalle"),
    #path("listar_compras_detalle/<int:id>/", views.registrar_compra_cab_det, name="list_compras_detalle_id"),
    #path('export/pdf/', views.export_pdf, name='export_pdf'),
    #path('export/excel/', views.export_excel, name='export_excel'),
    
    
]