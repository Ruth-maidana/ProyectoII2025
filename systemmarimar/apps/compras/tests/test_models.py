# tests/test_models.py
import pytest
from django.core.exceptions import ValidationError
from apps.compras.models import Categoria, Proveedor, Producto

@pytest.mark.django_db
class TestCategoria:

    def test_nombre_se_guarda_en_mayusculas(self):
        cat = Categoria.objects.create(nombre="ropa", descripcion="Ropa de moda")
        assert cat.nombre == "ROPA"

    def test_nombre_duplicado(self):
        Categoria.objects.create(nombre="CALZADO")
        cat2 = Categoria(nombre="calzado")  # mismo nombre diferente case
        with pytest.raises(ValidationError):
            cat2.full_clean()

    def test_no_permite_desactivar_si_tiene_productos(self):
        cat = Categoria.objects.create(nombre="JUGUETES", descripcion="Juguetes para niños")
        prov = Proveedor.objects.create(
            razon_social="Proveedor Uno",
            nro_documento="12345",
            correo="prov1@test.com",
            num_tel="12345678",
            tipo_documento="RUC",
            descripcion="Proveedor de juguetes"
        )
        Producto.objects.create(
            categoria=cat,
            proveedor=prov,
            nombre="Pelota",
            precio_compra=10,
            precio_venta=20,
            cantidad_en_stock=5,
            unidad_medida="UNIDADES",
            iva=10
        )
        cat.activo = False
        with pytest.raises(ValidationError):
            cat.full_clean()


@pytest.mark.django_db
class TestProveedor:

    def test_razon_social_mayusculas(self):
        prov = Proveedor.objects.create(
            razon_social="mi proveedor",
            nro_documento="111",
            correo="correo@test.com",
            num_tel="12345678",
            tipo_documento="RUC",
            descripcion="Proveedor de servicios"
        )
        assert prov.razon_social == "MI PROVEEDOR"

    def test_telefono_completo(self):
        prov = Proveedor.objects.create(
            razon_social="Test",
            nro_documento="222",
            correo="correo2@test.com",
            num_tel="98765432",
            tipo_documento="CI",
            codigo_pais="+595",
            descripcion="Proveedor de servicios"
        )
        assert prov.telefono_completo == "+595 98765432"

    def test_validacion_numero_usa(self):
        prov = Proveedor(
            razon_social="Proveedor USA",
            nro_documento="333",
            correo="correo3@test.com",
            num_tel="12345",  # solo 5 dígitos, inválido para USA
            tipo_documento="CI",
            codigo_pais="+1",
            descripcion="Proveedor de servicios"
        )
        with pytest.raises(ValidationError):
            prov.full_clean()


@pytest.mark.django_db
class TestProducto:

    def test_nombre_mayusculas(self, db):
        cat = Categoria.objects.create(nombre="BEBIDAS", descripcion="Bebidas varias")
        prov = Proveedor.objects.create(
            razon_social="Proveedor Bebidas",
            nro_documento="444",
            correo="correo4@test.com",
            num_tel="12345678",
            tipo_documento="RUC",
            descripcion="Proveedor de bebidas"
        )
        prod = Producto.objects.create(
            categoria=cat,
            proveedor=prov,
            nombre="coca cola",
            precio_compra=10,
            precio_venta=15,
            cantidad_en_stock=20,
            unidad_medida="UNIDADES",
            iva=10
        )
        assert prod.nombre == "COCA COLA"

    def test_total_inventario(self, db):
        cat = Categoria.objects.create(nombre="ALIMENTOS", descripcion="Alimentos varios")
        prov = Proveedor.objects.create(
            razon_social="Proveedor Alimentos",
            nro_documento="555",
            correo="correo5@test.com",
            num_tel="12345678",
            tipo_documento="RUC",
            descripcion="Proveedor de alimentos"
        )
        prod = Producto.objects.create(
            categoria=cat,
            proveedor=prov,
            nombre="Arroz",
            precio_compra=50,
            precio_venta=100,
            cantidad_en_stock=10,
            unidad_medida="KILOGRAMOS",
            iva=10
        )
        assert prod.total_inventario == 1000
