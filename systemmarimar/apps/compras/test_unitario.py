from django.test import TestCase
from .models import Proveedor, Categoria, Producto
from django.core.exceptions import ValidationError
from decimal import Decimal

class PruebasUnitarias(TestCase):

    def setUp(self):
        # Crear datos iniciales para las pruebas
        self.proveedor = Proveedor.objects.create(
            razon_social="Proveedor Test",
            nro_documento="123456789",
            direccion="Calle Falsa 123",
            num_tel="+595981234567",
            correo="proveedor@test.com",
            descripcion="Proveedor de prueba",
            tipo_documento="RUC"
        )
        self.categoria = Categoria.objects.create(
            nombre="Categoría Test",
            descripcion="Descripción de la categoría"
        )

    def test_crear_proveedor_correctamente(self):
        proveedor = Proveedor.objects.create(
            razon_social="Proveedor Nuevo",
            nro_documento="987654321",
            direccion="Calle Nueva 456",
            num_tel="+595987654321",
            correo="nuevo@test.com",
            descripcion="Nuevo proveedor",
            tipo_documento="CI"
        )
        # Verificar que el proveedor fue insertado en la base de datos
        proveedor_db = Proveedor.objects.get(nro_documento="987654321")
        self.assertEqual(proveedor.razon_social, "PROVEEDOR NUEVO")  # Validar que se guarda en mayúsculas

    def test_crear_categoria_correctamente(self):
        categoria = Categoria.objects.create(
            nombre="Nueva Categoría",
            descripcion="Descripción de la nueva categoría"
        )
        self.assertEqual(categoria.nombre, "NUEVA CATEGORÍA")  # Validar que se guarda en mayúsculas

    def test_crear_producto_asociado_a_categoria(self):
        producto = Producto.objects.create(
            categoria=self.categoria,
            proveedor=self.proveedor,
            nombre="Producto Asociado",
            descripcion="Producto asociado a categoría",
            precio=Decimal("50.00"),
            cantidad_en_stock=5
        )
        self.assertEqual(producto.categoria, self.categoria)