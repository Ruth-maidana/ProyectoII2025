from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.compras.models import Categoria, Producto, Proveedor
from .models import MovimientoStock
from .forms import AjusteStockForm
from .utils import registrar_movimiento_stock
from decimal import Decimal

class AjusteStockTestCase(TestCase):
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

    def test_ajuste_stock(self):
        # Estado inicial
        print(f"Stock inicial: {self.producto.cantidad_en_stock}")

        # Datos para el ajuste
        data = {
            'ajuste': 'REPOSICION',
            'cantidad': 5,
            'producto': self.producto.id,
            'descripcion': 'Ajuste de prueba',
            'movimiento': 'ENTRADA'
        }
        
        form = AjusteStockForm(data)
        self.assertTrue(form.is_valid(), f"Errores en el formulario: {form.errors}")

        # Registrar el movimiento de stock
        registrar_movimiento_stock(
            producto=self.producto,
            cantidad=form.cleaned_data['cantidad'],
            movimiento=form.cleaned_data['movimiento'],
            descripcion=form.cleaned_data['descripcion'],
            ajuste=form.cleaned_data['ajuste'],
            fecha_mov_producto=None,
            compra_cab=None,
            venta_cab=None
        )

        # Refrescar el producto desde la base de datos
        self.producto.refresh_from_db()
        print(f"Stock después del ajuste: {self.producto.cantidad_en_stock}")

        # Verificar el movimiento registrado
        movimiento = MovimientoStock.objects.filter(producto=self.producto).last()
        print(f"Movimiento registrado: {movimiento}")

        self.assertEqual(self.producto.cantidad_en_stock, 15)
        self.assertIsNotNone(movimiento)
        self.assertEqual(movimiento.cantidad, 5)
        self.assertEqual(movimiento.movimiento, 'ENTRADA')


