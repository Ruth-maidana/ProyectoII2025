from django.urls import path

from .import views

urlpatterns = [
    path('login/', views.login_user, name='login'),
    path("", views.index, name="home"),
    path('listar_usuario/',views.listar_usuarios,name="list_users"),
    path('logout_user/',views.logout_user,name="logout"),
    path('reset_password/<id_usuario>/', views.reset_password, name="reset_password"),
    path('delete_usuario/<id_usuario>/', views.delete_usuario, name="delete_user"),
    path('editar_contraseña/<id_usuario>/',views.editar_contraseña,name="edit_password"),
    path('registrar_usuario/',views.registrar_usuario,name="register_user"),
    path('editar_usuario/<id_usuario>/', views.editar_usuario, name="edit_user"),
    path('crear_grupo/', views.crear_grupo, name="create_group"),
    path('listar_grupos/', views.listar_grupos, name="list_groups"),
    #path('editar_grupo/<id_grupo>/', views.editar_grupo, name="edit_group"),
    path('grupo/<int:grupo_id>/actualizar-permisos/', views.actualizar_permisos_grupo, name='actualizar_permisos_grupo'),

]

