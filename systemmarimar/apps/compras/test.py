from django.test import TestCase
from .models import Proveedor, Categoria, Producto, OrdenCompraCab, OrdenCompraDet
from django.core.exceptions import ValidationError
from decimal import Decimal

class ComprasTestCase(TestCase):

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
        self.producto = Producto.objects.create(
            categoria=self.categoria,
            proveedor=self.proveedor,
            nombre="Producto Test",
            descripcion="Descripción del producto",
            precio=Decimal("100.00"),
            cantidad_en_stock=10
        )

    # Pruebas Unitarias

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
        self.assertEqual(proveedor.razon_social, "PROVEEDOR NUEVO")  # Validar que se guarda en mayúsculas

    def test_crear_categoria_correctamente(self):
        categoria = Categoria.objects.create(
            nombre="Nueva Categoría",
            descripcion="Descripción de la nueva categoría"
        )
        self.assertEqual(categoria.nombre, "NUEVA CATEGORÍA")  # Validar que se guarda en mayúsculas

    def test_crear_categoria_sin_nombre_debe_fallar(self):
        with self.assertRaises(ValidationError):
            categoria = Categoria(nombre="")
            categoria.full_clean()  # Validar errores antes de guardar

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

    def test_registrar_producto_con_datos_incorrectos(self):
        with self.assertRaises(ValidationError):
            producto = Producto(
                categoria=self.categoria,
                proveedor=self.proveedor,
                nombre="",  # Nombre vacío
                descripcion="Producto inválido",
                precio=Decimal("-10.00"),  # Precio negativo
                cantidad_en_stock=-5  # Cantidad negativa
            )
            producto.full_clean()  # Validar errores antes de guardar

    def test_validar_errores_al_registrar_proveedor_incompleto(self):
        with self.assertRaises(ValidationError):
            proveedor = Proveedor(
                razon_social="",  # Campo obligatorio vacío
                nro_documento="",
                correo="correo_invalido"
            )
            proveedor.full_clean()  # Validar errores antes de guardar

    def test_registrar_compra_con_productos_validos(self):
        compra = OrdenCompraCab.objects.create(
            nro_comprobante="001-001-0000001",
            proveedor=self.proveedor,
            total=Decimal("200.00"),
            forma_pago="EFECTIVO"
        )
        detalle = OrdenCompraDet.objects.create(
            orden_compra_cab=compra,
            producto=self.producto,
            descripcion="Detalle de prueba",
            cantidad=2,
            unidad_medida="Unidad",
            precio_compra=Decimal("100.00"),
            descuento=Decimal("0.00"),
            total_producto=Decimal("200.00")
        )
        self.assertEqual(detalle.orden_compra_cab, compra)
        self.assertEqual(detalle.total_producto, Decimal("200.00"))

    def test_calculo_total_compra(self):
        compra = OrdenCompraCab.objects.create(
            nro_comprobante="001-001-0000002",
            proveedor=self.proveedor,
            total=Decimal("0.00"),
            forma_pago="TRANSFERENCIA"
        )
        OrdenCompraDet.objects.create(
            orden_compra_cab=compra,
            producto=self.producto,
            descripcion="Detalle 1",
            cantidad=1,
            unidad_medida="Unidad",
            precio_compra=Decimal("100.00"),
            descuento=Decimal("10.00"),
            total_producto=Decimal("90.00")  # Paréntesis corregido aquí
        )
        OrdenCompraDet.objects.create(
            orden_compra_cab=compra,
            producto=self.producto,
            descripcion="Detalle 2",
            cantidad=2,
            unidad_medida="Unidad",
            precio_compra=Decimal("50.00"),
            descuento=Decimal("0.00"),
            total_producto=Decimal("100.00")  # Paréntesis corregido aquí
        )
        total = sum(detalle.total_producto for detalle in compra.ordencompradet_set.all())
        self.assertEqual(total, Decimal("190.00"))


    # Pruebas de Integración

    def test_registrar_compra_y_verificar_productos_asociados(self):
        compra = OrdenCompraCab.objects.create(
            nro_comprobante="001-001-0000003",
            proveedor=self.proveedor,
            total=Decimal("300.00"),
            forma_pago="EFECTIVO"
        )
        detalle1 = OrdenCompraDet.objects.create(
            orden_compra_cab=compra,
            producto=self.producto,
            descripcion="Detalle 1",
            cantidad=3,
            unidad_medida="Unidad",
            precio_compra=Decimal("100.00"),
            descuento=Decimal("0.00"),
            total_producto=Decimal("300.00")
        )
        self.assertIn(detalle1, compra.ordencompradet_set.all())

    def test_registrar_producto_y_verificar_categoria_asociada(self):
        producto = Producto.objects.create(
            categoria=self.categoria,
            proveedor=self.proveedor,
            nombre="Producto Categoría",
            descripcion="Producto asociado a categoría",
            precio=Decimal("150.00"),
            cantidad_en_stock=20
        )
        self.assertEqual(producto.categoria, self.categoria)