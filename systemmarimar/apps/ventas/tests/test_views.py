import pytest
from django.urls import reverse
from django.contrib.auth.models import User, Permission
from django.test import Client
from apps.compras.models import Categoria, Proveedor, Producto, OrdenCompraCab
from django.core.exceptions import ValidationError

@pytest.fixture
def admin_user(db):
    user = User.objects.create_user(username='admin', password='adminpass')
    user.is_staff = True
    user.is_superuser = True
    user.save()
    return user

@pytest.fixture
def client_admin(admin_user):
    client = Client()
    client.login(username='admin', password='adminpass')
    return client

@pytest.fixture
def categoria(db):
    return Categoria.objects.create(nombre="ELECTRONICA",descripcion="Productos electrónicos")

@pytest.fixture
def proveedor_ruc(db):
    return Proveedor.objects.create(
        razon_social="PROVEEDOR RUC",
        nro_documento="1234567",
        correo="ruc@test.com",
        num_tel="12345678",
        tipo_documento="RUC",
        descripcion="Proveedor de tecnología"
    )


@pytest.fixture
def proveedor_ci(db):
    return Proveedor.objects.create(
        razon_social="PROVEEDOR CI",
        nro_documento="9876543",
        correo="ci@test.com",
        num_tel="12345678",
        tipo_documento="CI",
        descripcion="Proveedor de tecnología"
    )

@pytest.fixture
def producto(db, categoria, proveedor_ruc):
    return Producto.objects.create(
        categoria=categoria,
        proveedor=proveedor_ruc,
        nombre="LAPTOP",
        precio_compra=1000,
        precio_venta=1200,
        cantidad_en_stock=10,
        unidad_medida="UNIDADES",
        iva=10
    )

def get_perm_codename(model, action):
    return f"compras.{action}_{model}"


@pytest.mark.django_db
def test_duplicacion_nombre_proveedor(client):
    url = reverse('reg_proveedor')

    # Crear proveedor inicial
    data1 = {
        "razon_social": "DUPLICADO",
        "nro_documento": "1111",
        "correo": "dup1@test.com",
        "num_tel": "12345678",
        "tipo_documento": "RUC",
        "codigo_pais": "+595",
        "descripcion": "desc"
    }
    client.post(url, data1)

    # Intentar crear proveedor con mismo nombre
    data2 = {
        "razon_social": "DUPLICADO",
        "nro_documento": "2222",
        "correo": "dup2@test.com",
        "num_tel": "87654321",
        "tipo_documento": "RUC",
        "codigo_pais": "+595",
        "descripcion": "desc2"
    }
    client.post(url, data2)

    # Verificar que no se creó el proveedor duplicado
    assert Proveedor.objects.filter(nro_documento="2222").count() == 0


@pytest.mark.django_db
def test_duplicacion_ruc_proveedor(client_admin):
    url = reverse('reg_proveedor')

    # -------------------
    # POST válido
    # -------------------
    data_valid = {
        "razon_social": "PROV1",
        "documento": "12345678",
        "digito_verificador": "1",
        "correo": "ruc1@test.com",
        "num_tel": "12345678",  # válido para Paraguay
        "tipo_documento": "RUC",
        "codigo_pais": "+595",
        "descripcion": "desc"
    }
    response_valid = client_admin.post(url, data_valid, follow=True)
    assert response_valid.status_code in [200, 302]

    # Verificar que se guardó el proveedor
    nro_documento = f"{data_valid['documento']}-{data_valid['digito_verificador']}"
    assert Proveedor.objects.filter(nro_documento=nro_documento).exists()

    # -------------------
    # POST inválido (mismo RUC)
    # -------------------
    data_invalid = data_valid.copy()
    data_invalid["razon_social"] = "PROV2"
    data_invalid["correo"] = "ruc2@test.com"
    response_invalid = client_admin.post(url, data_invalid)

    # Debe caer en form.is_valid() == False
    if response_invalid.context and "form_proveedor" in response_invalid.context:
        form_errors = response_invalid.context["form_proveedor"].errors
        assert "documento" in form_errors or "nro_documento" in form_errors

    # No debe haberse creado un nuevo proveedor con el mismo RUC
    assert Proveedor.objects.filter(nro_documento=nro_documento).count() == 1

    # -------------------
    # GET del formulario
    # -------------------
    response_get = client_admin.get(url)
    assert response_get.status_code == 200
    assert "form_proveedor" in response_get.context


@pytest.mark.django_db
def test_duplicacion_ci_proveedor(client_admin):
    url = reverse('reg_proveedor')

    # -------------------
    # POST válido (CI)
    # -------------------
    data_valid = {
        "razon_social": "PROV1",
        "documento": "CI123",
        "digito_verificador": "",  # No es obligatorio para CI
        "correo": "ci1@test.com",
        "num_tel": "12345678",     # válido para Paraguay
        "tipo_documento": "CI",
        "codigo_pais": "+595",
        "descripcion": "desc"
    }
    response_valid = client_admin.post(url, data_valid, follow=True)
    assert response_valid.status_code in [200, 302]

    # Verificar que se guardó correctamente
    nro_documento = data_valid["documento"]  # Para CI, nro_documento = documento
    assert Proveedor.objects.filter(nro_documento=nro_documento).exists()

    # -------------------
    # POST duplicado (CI)
    # -------------------
    data_duplicate = data_valid.copy()
    data_duplicate["razon_social"] = "PROV2"
    data_duplicate["correo"] = "ci2@test.com"
    response_duplicate = client_admin.post(url, data_duplicate, follow=True)

    # Revisar que el duplicado no se haya guardado
    assert Proveedor.objects.filter(nro_documento=nro_documento).count() == 1

    # Opcional: verificar que el form devolvió un error
    if response_duplicate.context and "form_proveedor" in response_duplicate.context:
        form = response_duplicate.context["form_proveedor"]
        assert "documento" in form.errors



'''
@pytest.mark.django_db
def test_duplicacion_nombre_producto(client_admin, categoria, proveedor_ruc):
    url = reverse('registrar_producto')
    data = {
        "categoria": categoria.id,
        "proveedor": proveedor_ruc.id,
        "nombre": "Duplicado",
        "precio_compra": 100,
        "precio_venta": 200,
        "cantidad_en_stock": 5,
        "unidad_medida": "UNIDADES",
        "iva": 10
    }
    client_admin.post(url, data)
    resp = client_admin.post(url, data)
    assert "Ya existe un producto con este nombre" in resp.content.decode()

@pytest.mark.django_db
def test_eliminar_categoria_asignada_a_producto(client_admin, categoria, proveedor_ruc):
    prod = Producto.objects.create(
        categoria=categoria,
        proveedor=proveedor_ruc,
        nombre="ASIGNADO",
        precio_compra=10,
        precio_venta=20,
        cantidad_en_stock=1,
        unidad_medida="UNIDADES",
        iva=10
    )
    url = reverse('inactivar_categoria', args=[categoria.id])
    resp = client_admin.post(url)
    assert "No se puede desactivar la categoría" in resp.content.decode()

@pytest.mark.django_db
def test_editar_producto_nombre_duplicado(client_admin, categoria, proveedor_ruc):
    url = reverse('registrar_producto')
    data1 = {
        "categoria": categoria.id,
        "proveedor": proveedor_ruc.id,
        "nombre": "PROD1",
        "precio_compra": 100,
        "precio_venta": 200,
        "cantidad_en_stock": 5,
        "unidad_medida": "UNIDADES",
        "iva": 10
    }
    data2 = data1.copy()
    data2["nombre"] = "PROD2"
    client_admin.post(url, data1)
    resp2 = client_admin.post(url, data2)
    prod2 = Producto.objects.get(nombre="PROD2")
    url_edit = reverse('editar_producto', args=[prod2.id])
    data_edit = data2.copy()
    data_edit["nombre"] = "PROD1"
    resp = client_admin.post(url_edit, data_edit)
    assert "Ya existe un producto con este nombre" in resp.content.decode()

@pytest.mark.django_db
def test_producto_precio_compra_negativo(client_admin, categoria, proveedor_ruc):
    url = reverse('registrar_producto')
    data = {
        "categoria": categoria.id,
        "proveedor": proveedor_ruc.id,
        "nombre": "NEGATIVO",
        "precio_compra": -10,
        "precio_venta": 100,
        "cantidad_en_stock": 1,
        "unidad_medida": "UNIDADES",
        "iva": 10
    }
    resp = client_admin.post(url, data)
    assert "precio_compra" in resp.content.decode() or "negativo" in resp.content.decode()

@pytest.mark.django_db
def test_producto_precio_venta_negativo(client_admin, categoria, proveedor_ruc):
    url = reverse('registrar_producto')
    data = {
        "categoria": categoria.id,
        "proveedor": proveedor_ruc.id,
        "nombre": "NEGATIVO2",
        "precio_compra": 10,
        "precio_venta": -100,
        "cantidad_en_stock": 1,
        "unidad_medida": "UNIDADES",
        "iva": 10
    }
    resp = client_admin.post(url, data)
    assert "precio_venta" in resp.content.decode() or "negativo" in resp.content.decode()

@pytest.mark.django_db
def test_categoria_nombre_duplicado(client_admin):
    url = reverse('registrar_categoria')
    data = {
        "nombre": "DUPLICADA",
        "descripcion": "desc"
    }
    client_admin.post(url, data)
    resp = client_admin.post(url, data)
    assert "Ya existe una categoría con este nombre" in resp.content.decode()

@pytest.mark.django_db
def test_registrar_compra_sin_proveedor(client_admin):
    url = reverse('registrar_compra_cab_det_version_act_v2')
    data = {
        "nro_comprobante": "C123",
        "fecha_compra": "2024-01-01",
        "total": 100,
        "forma_pago": "EFECTIVO",
        "descuento": 0,
        "iva_diez": 0,
        "iva_cinco": 0,
        # Falta proveedor
    }
    resp = client_admin.post(url, data)
    assert "proveedor" in resp.content.decode() or "error" in resp.content.decode().lower()

@pytest.mark.django_db
def test_registrar_compra_sin_detalle(client_admin, proveedor_ruc):
    url = reverse('registrar_compra_cab_det_version_act_v2')
    data = {
        "nro_comprobante": "C124",
        "fecha_compra": "2024-01-01",
        "proveedor": proveedor_ruc.id,
        "total": 100,
        "forma_pago": "EFECTIVO",
        "descuento": 0,
        "iva_diez": 0,
        "iva_cinco": 0,
        # Sin detalles
    }
    resp = client_admin.post(url, data)
    assert "Debe ingresar al menos un detalle de compra válido" in resp.content.decode() or "detalle" in resp.content.decode().lower()
'''