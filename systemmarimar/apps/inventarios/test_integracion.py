from django.test import TestCase
from apps.compras.models import Categoria, Producto, Proveedor
from .utils import registrar_movimiento_stock
from decimal import Decimal

class IntegracionStockTestCase(TestCase):
    def setUp(self):
        # Crear proveedor para pruebas
        self.proveedor = Proveedor.objects.create(
            razon_social="Proveedor Test",
            nro_documento="123456789",
            direccion="Calle Falsa 123",
            num_tel="+595981234567",
            correo="proveedor@test.com",
            descripcion="Proveedor de prueba",
            tipo_documento="RUC"
        )
        
        # Crear categoría y producto para pruebas
        self.categoria = Categoria.objects.create(
            nombre="Categoría Test",
            descripcion="Categoría para pruebas"
        )
        
        # Crear el producto
        self.producto = Producto.objects.create(
            categoria=self.categoria,
            proveedor=self.proveedor,  # Asignar el proveedor creado
            nombre="Producto Test",
            descripcion="Producto para pruebas",
            precio_compra=Decimal("100.00"),
            precio_venta=Decimal("150.00"),
            iva=Decimal("10.00"),
            unidad_medida='UNIDADES',
            cantidad_en_stock=10,
        )

    def test_integracion_stock_despues_venta_y_compra(self):
        # Stock inicial
        stock_inicial = self.producto.cantidad_en_stock
        print(f"Stock inicial: {stock_inicial}")
        
        
        # Simular una venta (salida de stock)
        registrar_movimiento_stock(
            producto=self.producto,
            cantidad=3,
            movimiento='SALIDA',
            descripcion='Venta de prueba',
            ajuste='REPOSICION',
            fecha_mov_producto=None,
            compra_cab=None,
            venta_cab=None
        )
        
        # Verificar que el stock se haya actualizado correctamente
        self.producto.refresh_from_db()
        print(f"Stock después de la venta: {self.producto.cantidad_en_stock}")
        self.assertEqual(self.producto.cantidad_en_stock, stock_inicial - 3)

        # Simular una compra (entrada de stock)
        registrar_movimiento_stock(
            producto=self.producto,
            cantidad=7,
            movimiento='ENTRADA',
            descripcion='Compra de prueba',
            ajuste='OTRO',
            fecha_mov_producto=None,
            compra_cab=None,
            venta_cab=None
        )
        self.producto.refresh_from_db()
        print(f"Stock después de la compra: {self.producto.cantidad_en_stock}")
        self.assertEqual(self.producto.cantidad_en_stock, stock_inicial - 3 + 7)