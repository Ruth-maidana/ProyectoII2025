from django.urls import path

from .import views

urlpatterns = [

    path("listar_stock", views.listar_movimientos_version_act, name="list_movimientos"),
    path("ajustar_stock", views.ajustar_stock, name="ajust_stock"),
    path("configurar_stock", views.configurar_stock, name="config_stock"),
    path('api/stock-bajo/', views.api_stock_bajo, name='api_stock_bajo'),
    

]

    