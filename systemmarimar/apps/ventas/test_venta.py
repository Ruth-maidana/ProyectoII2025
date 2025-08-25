from django.test import TestCase
from decimal import Decimal
from apps.compras.models import Categoria, Producto, Proveedor
from .models import Cliente
from .forms import FormRegVentaDetalle

class ValidacionCantidadVentaTestCase(TestCase):
    def setUp(self):
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
            descripcion="Categoría para pruebas"
        )
        self.producto = Producto.objects.create(
            categoria=self.categoria,
            proveedor=self.proveedor,
            nombre="Producto Test",
            descripcion="Producto para pruebas",
            precio_compra=Decimal("100.00"),
            precio_venta=Decimal("150.00"),
            iva=Decimal("10.00"),
            unidad_medida='UNIDADES',
            cantidad_en_stock=10,
        )
        self.cliente = Cliente.objects.create(
            nombre="Cliente Test",
            nro_documento="1234567",
            direccion="Calle Cliente",
            num_tel="+595981111111",
            correo="cliente@test.com"
        )

    def test_no_permite_cantidad_negativa_en_venta(self):
        data = {
            'producto_id': self.producto.id,
            'cantidad': -2,  # Cantidad negativa
            'descripcion': 'Venta con cantidad negativa',
            'unidad_medida': 'UNIDADES',
            'precio_unit_venta': Decimal("150.00"),
            'subtotal': Decimal("-300.00"),
        }
        form = FormRegVentaDetalle(data)
        self.assertFalse(form.is_valid())
        self.assertIn('cantidad', form.errors)
        
    
    def test_no_permite_vender_mas_que_stock_disponible(self):
        data = {
            'producto_id': self.producto.id,
            'cantidad': 20,  # Mayor que el stock disponible (10)
            'descripcion': 'Venta con cantidad mayor al stock',
            'unidad_medida': 'UNIDADES',
            'precio_unit_venta': Decimal("150.00"),
            'subtotal': Decimal("3000.00"),
        }
        form = FormRegVentaDetalle(data)
        self.assertFalse(form.is_valid())
        self.assertIn('cantidad', form.errors)
        
        
    def test_no_permite_campos_vacios(self):
        data = {
            'producto_id': '',  # Campo vacío
            'cantidad': '',    # Campo vacío
            'descripcion': '', # Campo vacío
            'unidad_medida': '', # Campo vacío
            'precio_unit_venta': '', # Campo vacío
            'subtotal': '', # Campo vacío
        }
        form = FormRegVentaDetalle(data)
        self.assertFalse(form.is_valid())
        self.assertIn('producto_id', form.errors)
        self.assertIn('cantidad', form.errors)
        self.assertIn('unidad_medida', form.errors)
        self.assertIn('precio_unit_venta', form.errors)
        self.assertIn('subtotal', form.errors)