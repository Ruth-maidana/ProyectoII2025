from django.test import TestCase
from .models import Proveedor, Categoria, Producto, OrdenCompraCab, OrdenCompraDet
from decimal import Decimal

class PruebasIntegrales(TestCase):

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
            total_producto=Decimal("90.00")
        )
        OrdenCompraDet.objects.create(
            orden_compra_cab=compra,
            producto=self.producto,
            descripcion="Detalle 2",
            cantidad=2,
            unidad_medida="Unidad",
            precio_compra=Decimal("50.00"),
            descuento=Decimal("0.00"),
            total_producto=Decimal("100.00")
        )
        total = sum(detalle.total_producto for detalle in compra.ordencompradet_set.all())
        self.assertEqual(total, Decimal("190.00"))

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