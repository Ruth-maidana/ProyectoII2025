import pytest
from django.core.exceptions import ValidationError
from apps.compras.models import Categoria, Proveedor

@pytest.mark.django_db
class TestCategoria:

    def test_creacion_categoria_valida(self):
        cat = Categoria.objects.create(nombre="Electronica", descripcion="Equipos")
        assert cat.nombre == "ELECTRONICA"  # debe guardar en mayúsculas
        assert cat.activo is True

    def test_nombre_unico_case_insensitive(self):
        Categoria.objects.create(nombre="Electronica")
        cat2 = Categoria(nombre="electronica")
        with pytest.raises(ValidationError) as excinfo:
            cat2.full_clean()
        assert "Ya existe una categoría con este nombre." in str(excinfo.value)

    def test_no_se_puede_deshabilitar_con_productos_activos(self, django_db_setup, django_db_blocker):
        with django_db_blocker.unblock():
            # Crear proveedor primero (requerido para Producto)
            proveedor = Proveedor.objects.create(
                razon_social="Proveedor Test",
                nro_documento="12345678",
                correo="test@proveedor.com",
                descripcion="Proveedor de prueba",
                tipo_documento="RUC",
                num_tel="123456789"
            )
            
            # Crear categoría
            cat = Categoria.objects.create(nombre="Ropa")
            
            # Crear producto con proveedor asignado
            cat.producto_set.create(
                nombre="Pantalón",
                proveedor=proveedor,
                precio_compra=50000.00,
                precio_venta=75000.00,
                iva=10,
                cantidad_en_stock=10,
                unidad_medida="UNIDADES",
                activo=True
            )

            # Intentar desactivar la categoría
            cat.activo = False
            with pytest.raises(ValidationError) as excinfo:
                cat.full_clean()
            assert "No se puede desactivar" in str(excinfo.value)