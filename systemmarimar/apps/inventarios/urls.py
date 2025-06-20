from django.urls import path

from .import views

urlpatterns = [

    path("listar_stock", views.listar_movimientos_version_act, name="list_movimientos"),
    path("ajustar_stock", views.ajustar_stock, name="ajust_stock"),
    path("configurar_stock", views.configurar_stock, name="config_stock"),
    path('api/stock-bajo/', views.api_stock_bajo, name='api_stock_bajo'),
    path('producto_mas_vendidos/', views.productos_mas_vendidos_v2, name='mas_vendidos'),
    
    path('valor_inventario/', views.valor_inventario_gral_v3, name='valor_inventario'),
    path('exportar-pdf/', views.exportar_inventario_pdf, name='exportar_inventario_pdf'),
    path('exportar-grafico-pdf/', views.exportar_grafico_pdf_v2, name='exportar_grafico_pdf'),
    path('exportar-grafico-mas-vendido-pdf/', views.exportar_productos_mas_vendidos_pdf, name='exp_graf_prod_mas_vendido_pdf'),
    path('valor_inventario_historico/', views.valor_inventario_historico, name='inventario_historico'),
    path('exportar_inventario_historico_pdf/', views.exportar_inventario_historico_pdf, name='exp_inventario_historico_pdf'),
    
    path('inventory-summary/', views.inventory_summary, name='inventory_summary'),
    path('stock-critico/', views.lista_stock_critico, name='lista_stock_critico'),
    path('movimientos/', views.movimientos_recientes, name='movimientos_recientes'),
    path('inventory-abc/', views.analisis_abc, name='inventory_abc'),
    path('rotacion-inventario/', views.api_rotacion_inventario, name='api_rotacion'),
    #path('inventory-reabastecimiento/', views.prediccion_reabastecimiento, name='reabastecimiento'),
    
    
    #path('valor_monetario_inventario/', views.valor_inventario, name='valor_monetario_inventario'),
    
    #path('api/stock-bajo/', views.pantalla_stock, name='api_stock_bajo'),
    

]

    