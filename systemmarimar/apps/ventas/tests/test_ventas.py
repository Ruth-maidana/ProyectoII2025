from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from apps.ventas.models import Cliente, VentaCabecera, VentaDetalle
from apps.ventas.forms import (
    FormRegistrarCliente, FormEditarCliente,
    FormRegVentaCabecera, FormRegVentaDetalle,
    FormEditVentaDetalle, FormEditarVentaCabecera
)
from apps.compras.models import Producto, Categoria, Proveedor
from django.contrib.auth.models import User
import pytest

@pytest.mark.django_db
class ClienteModelTest(TestCase):
    """Tests para el modelo Cliente"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.cliente_data = {
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'nro_documento': '1234567-8',
            'nacionalidad': 'Paraguaya',
            'estado_civil': 'Soltero/a',
            'codigo_pais': '+595',
            'num_tel': '981234567',
            'correo': 'juan.perez@example.com',
            'direccion': 'Asunción, Paraguay',
            'tipo_documento': 'CI'
        }
    
    def test_crear_cliente_valido(self):
        """Test: Crear un cliente con datos válidos"""
        cliente = Cliente.objects.create(**self.cliente_data)
        self.assertEqual(cliente.nombre, 'Juan')
        self.assertEqual(cliente.apellido, 'Pérez')
        self.assertTrue(cliente.activo)
        self.assertIsNotNone(cliente.fecha_insercion)
    
    def test_telefono_completo_property(self):
        """Test: Propiedad telefono_completo"""
        cliente = Cliente.objects.create(**self.cliente_data)
        self.assertEqual(cliente.telefono_completo, '+595 981234567')
    
    def test_unique_together_telefono(self):
        """Test: Validación de unique_together para código + teléfono"""
        Cliente.objects.create(**self.cliente_data)
        
        # Intentar crear otro cliente con el mismo teléfono
        with self.assertRaises(ValidationError):
            cliente2_data = self.cliente_data.copy()
            cliente2_data['correo'] = 'otro@example.com'
            cliente2_data['nro_documento'] = '9999999-0'
            cliente2 = Cliente(**cliente2_data)
            cliente2.full_clean()
    
    def test_clean_telefono_paraguay_minimo_8_digitos(self):
        """Test: Validación de teléfono para Paraguay (mínimo 8 dígitos)"""
        cliente_data = self.cliente_data.copy()
        cliente_data['num_tel'] = '1234567'  # Solo 7 dígitos
        cliente = Cliente(**cliente_data)
        
        with self.assertRaises(ValidationError) as context:
            cliente.full_clean()
        self.assertIn('num_tel', context.exception.message_dict)
    
    def test_clean_telefono_usa_exactamente_10_digitos(self):
        """Test: Validación de teléfono para USA (exactamente 10 dígitos)"""
        cliente_data = self.cliente_data.copy()
        cliente_data['codigo_pais'] = '+1'
        cliente_data['num_tel'] = '123456789'  # Solo 9 dígitos
        cliente = Cliente(**cliente_data)
        
        with self.assertRaises(ValidationError) as context:
            cliente.full_clean()
        self.assertIn('num_tel', context.exception.message_dict)
    
    def test_clean_telefono_latinoamerica_rango_valido(self):
        """Test: Validación de teléfono para Latinoamérica (8-11 dígitos)"""
        cliente_data = self.cliente_data.copy()
        cliente_data['codigo_pais'] = '+54'  # Argentina
        cliente_data['num_tel'] = '1234567'  # Solo 7 dígitos (inválido)
        cliente = Cliente(**cliente_data)
        
        with self.assertRaises(ValidationError) as context:
            cliente.full_clean()
        self.assertIn('num_tel', context.exception.message_dict)
    
    def test_correo_unico(self):
        """Test: Correo debe ser único"""
        Cliente.objects.create(**self.cliente_data)
        
        cliente2_data = self.cliente_data.copy()
        cliente2_data['nro_documento'] = '9999999-0'
        cliente2_data['num_tel'] = '971234567'
        
        with self.assertRaises(Exception):  # IntegrityError
            Cliente.objects.create(**cliente2_data)

@pytest.mark.django_db
class VentaCabeceraModelTest(TestCase):
    """Tests para el modelo VentaCabecera"""
    
    def setUp(self):
        """Configuración inicial"""
        self.cliente = Cliente.objects.create(
            nombre='Test',
            apellido='Cliente',
            nro_documento='1234567-8',
            nacionalidad='Paraguaya',
            estado_civil='Soltero/a',
            codigo_pais='+595',
            num_tel='981234567',
            correo='test@example.com',
            direccion='Asunción',
            tipo_documento='CI'
        )
        
        self.venta_data = {
            'nro_comprobante': '001-001-0000001',
            'condicion_venta': 'Contado',
            'timbrado': '12345678',
            'vendedor': 'Juan Vendedor',
            'cliente': self.cliente,
            'total': Decimal('100.00'),
            'forma_pago': 'EFECTIVO',
            'iva_diez': Decimal('9.09'),
            'iva_cinco': Decimal('0.00'),
            'descuento': Decimal('0.00')
        }
    
    def test_crear_venta_cabecera(self):
        """Test: Crear una venta cabecera válida"""
        venta = VentaCabecera.objects.create(**self.venta_data)
        self.assertEqual(venta.nro_comprobante, '001-001-0000001')
        self.assertTrue(venta.activo)
        self.assertIsNotNone(venta.fecha_insercion)
    
    def test_nro_comprobante_unico(self):
        """Test: Número de comprobante debe ser único"""
        VentaCabecera.objects.create(**self.venta_data)
        
        with self.assertRaises(Exception):  # IntegrityError
            VentaCabecera.objects.create(**self.venta_data)

@pytest.mark.django_db
class VentaDetalleModelTest(TestCase):
    """Tests para el modelo VentaDetalle"""
    
    def setUp(self):
        """Configuración inicial"""
        
        self.proveedor = Proveedor.objects.create(
            razon_social="mi proveedor",
            nro_documento="111",
            correo="correo@test.com",
            num_tel="12345678",
            tipo_documento="RUC",
            descripcion="Proveedor de servicios"
        )
        self.cliente = Cliente.objects.create(
            nombre='Test',
            apellido='Cliente',
            nro_documento='1234567-8',
            nacionalidad='Paraguaya',
            estado_civil='Soltero/a',
            codigo_pais='+595',
            num_tel='981234567',
            correo='test@example.com',
            direccion='Asunción',
            tipo_documento='CI',
        )
    
        
        self.venta_cab = VentaCabecera.objects.create(
            nro_comprobante='001-001-0000001',
            condicion_venta='Contado',
            timbrado='12345678',
            vendedor='Juan Vendedor',
            cliente=self.cliente,
            total=Decimal('100.00'),
            forma_pago='EFECTIVO',
            iva_diez=Decimal('9.09'),
            iva_cinco=Decimal('0.00'),
            descuento=Decimal('0.00')
        )
        
        # Crear producto
        categoria = Categoria.objects.create(nombre='Categoria Test', descripcion='Test')
        
        self.producto = Producto.objects.create(
            nombre='Producto Test',
            descripcion='Descripción test',
            categoria=categoria,
            unidad_medida='UNIDADES',
            cantidad_en_stock=100,
            precio_venta=Decimal('50.00'),
            precio_compra=Decimal('30.00'),
            iva=Decimal('10.00'),
            proveedor = self.proveedor
        )
    
    def test_crear_venta_detalle(self):
        """Test: Crear un detalle de venta"""
        detalle = VentaDetalle.objects.create(
            venta_cab=self.venta_cab,
            producto=self.producto,
            cantidad=5,
            descripcion='Test producto',
            unidad_medida='UNIDADES',
            precio_unit_venta=Decimal('100.00'),
            subtotal=Decimal('500.00')
        )
        self.assertEqual(detalle.cantidad, 5)
        self.assertTrue(detalle.activo)
        self.assertEqual(detalle.venta_cab, self.venta_cab)

@pytest.mark.django_db
class FormRegistrarClienteTest(TestCase):
    """Tests para FormRegistrarCliente"""
    
    def test_form_valido_con_ruc(self):
        """Test: Formulario válido con RUC"""
        form_data = {
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'tipo_documento': 'RUC',
            'documento': '1234567',
            'digito_verificador': '8',
            'nacionalidad': 'Paraguaya',
            'estado_civil': 'Soltero/a',
            'codigo_pais': '+595',
            'num_tel': '981234567',
            'correo': 'juan@example.com',
            'direccion': 'Asunción'
        }
        form = FormRegistrarCliente(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Verificar que se concatenó correctamente
        cliente = form.save()
        self.assertEqual(cliente.nro_documento, '1234567-8')
    
    def test_form_valido_con_ci(self):
        """Test: Formulario válido con CI"""
        form_data = {
            'nombre': 'María',
            'apellido': 'González',
            'tipo_documento': 'CI',
            'documento': '9876543',
            'nacionalidad': 'Paraguaya',
            'estado_civil': 'Casado/a',
            'codigo_pais': '+595',
            'num_tel': '971234567',
            'correo': 'maria@example.com',
            'direccion': 'Luque'
        }
        form = FormRegistrarCliente(data=form_data)
        self.assertTrue(form.is_valid())
        
        cliente = form.save()
        self.assertEqual(cliente.nro_documento, '9876543')
    
    def test_form_ruc_sin_digito_verificador(self):
        """Test: Error cuando RUC no tiene dígito verificador"""
        form_data = {
            'nombre': 'Test',
            'apellido': 'User',
            'tipo_documento': 'RUC',
            'documento': '1234567',
            'nacionalidad': 'Paraguaya',
            'estado_civil': 'Soltero/a',
            'codigo_pais': '+595',
            'num_tel': '981234567',
            'correo': 'test@example.com',
            'direccion': 'Asunción'
        }
        form = FormRegistrarCliente(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
    
    def test_form_documento_duplicado(self):
        """Test: Error cuando el documento ya existe"""
        # Crear cliente existente
        Cliente.objects.create(
            nombre='Existing',
            apellido='Client',
            nro_documento='1234567-8',
            nacionalidad='Paraguaya',
            estado_civil='Soltero/a',
            codigo_pais='+595',
            num_tel='981234567',
            correo='existing@example.com',
            direccion='Asunción',
            tipo_documento='RUC'
        )
        
        # Intentar crear otro con el mismo documento
        form_data = {
            'nombre': 'New',
            'apellido': 'Client',
            'tipo_documento': 'RUC',
            'documento': '1234567',
            'digito_verificador': '8',
            'nacionalidad': 'Paraguaya',
            'estado_civil': 'Soltero/a',
            'codigo_pais': '+595',
            'num_tel': '971234567',
            'correo': 'new@example.com',
            'direccion': 'Asunción'
        }
        form = FormRegistrarCliente(data=form_data)
        self.assertFalse(form.is_valid())

@pytest.mark.django_db
class FormRegVentaDetalleTest(TestCase):
    """Tests para FormRegVentaDetalle"""
    
    def setUp(self):
        """Configuración inicial"""
        
        self.proveedor = Proveedor.objects.create(
            razon_social="mi proveedor",
            nro_documento="111",
            correo="correo@test.com",
            num_tel="12345678",
            tipo_documento="RUC",
            descripcion="Proveedor de servicios"
        )
        
        categoria = Categoria.objects.create(nombre='Cat', descripcion='Test')
        
        self.producto = Producto.objects.create(
            nombre='Producto Test',
            descripcion='Desc',
            categoria=categoria,
            unidad_medida='UNIDADES',
            cantidad_en_stock=50,
            precio_venta=Decimal('100.00'),
            precio_compra=Decimal('30.00'),
            iva=Decimal('10.00'),
            proveedor = self.proveedor
        )
    
    def test_form_valido(self):
        """Test: Formulario válido"""
        form_data = {
            'producto_id': self.producto.id,
            'descripcion': 'Test',
            'cantidad': 5,
            'unidad_medida': 'UNIDADES',
            'precio_unit_venta': Decimal('100.00'),
            'subtotal': Decimal('500.00')
        }
        form = FormRegVentaDetalle(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_clean_cantidad_negativa(self):
        """Test: Cantidad negativa debe fallar"""
        form_data = {
            'producto_id': self.producto.id,
            'descripcion': 'Test',
            'cantidad': -5,
            'unidad_medida': 'UNIDADES',
            'precio_unit_venta': Decimal('100.00'),
            'subtotal': Decimal('500.00')
        }
        form = FormRegVentaDetalle(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('cantidad', form.errors)
    
    def test_clean_stock_insuficiente(self):
        """Test: Error cuando no hay suficiente stock"""
        form_data = {
            'producto_id': self.producto.id,
            'descripcion': 'Test',
            'cantidad': 100,  # Más que el stock disponible (50)
            'unidad_medida': 'UNIDADES',
            'precio_unit_venta': Decimal('100.00'),
            'subtotal': Decimal('10000.00')
        }
        form = FormRegVentaDetalle(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('cantidad', form.errors)
    
    def test_clean_producto_no_existe(self):
        """Test: Error cuando el producto no existe"""
        form_data = {
            'producto_id': 99999,
            'descripcion': 'Test',
            'cantidad': 5,
            'unidad_medida': 'UNIDADES',
            'precio_unit_venta': Decimal('100.00'),
            'subtotal': Decimal('500.00')
        }
        form = FormRegVentaDetalle(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('producto_id', form.errors)
    
    def test_clean_sin_producto_id(self):
        """Test: Error cuando no se proporciona producto_id"""
        form_data = {
            'descripcion': 'Test',
            'cantidad': 5,
            'unidad_medida': 'UNIDADES',
            'precio_unit_venta': Decimal('100.00'),
            'subtotal': Decimal('500.00')
        }
        form = FormRegVentaDetalle(data=form_data)
        self.assertFalse(form.is_valid())

@pytest.mark.django_db
class FormRegVentaCabeceraTest(TestCase):
    """Tests para FormRegVentaCabecera"""
    
    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.cliente = Cliente.objects.create(
            nombre='Test',
            apellido='Cliente',
            nro_documento='1234567-8',
            nacionalidad='Paraguaya',
            estado_civil='Soltero/a',
            codigo_pais='+595',
            num_tel='981234567',
            correo='test@example.com',
            direccion='Asunción',
            tipo_documento='CI',
            activo=True
        )
    
    def test_form_valido(self):
        """Test: Formulario de cabecera válido"""
        form_data = {
            'fecha_venta': timezone.now(),
            'nro_comprobante': '001-001-0000001',
            'vendedor': 'Test Vendedor',
            'cliente': self.cliente.id,
            'total': Decimal('100.00'),
            'forma_pago': 'EFECTIVO',
            'iva_diez': Decimal('9.09'),
            'iva_cinco': Decimal('0.00'),
            'descuento': Decimal('0.00'),
            'timbrado': '12345678',
            'condicion_venta': 'Contado'
        }
        form = FormRegVentaCabecera(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_clean_descuento_mayor_que_total(self):
        """Test: Error cuando descuento es mayor que total"""
        form_data = {
            'fecha_venta': timezone.now(),
            'nro_comprobante': '001-001-0000001',
            'vendedor': 'Test Vendedor',
            'cliente': self.cliente.id,
            'total': Decimal('100.00'),
            'forma_pago': 'EFECTIVO',
            'iva_diez': Decimal('9.09'),
            'iva_cinco': Decimal('0.00'),
            'descuento': Decimal('150.00'),  # Mayor que total
            'timbrado': '12345678',
            'condicion_venta': 'Contado'
        }
        form = FormRegVentaCabecera(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('descuento', form.errors)
    
    def test_clean_cliente_inactivo(self):
        """Test: Error cuando el cliente está inactivo"""
        self.cliente.activo = False
        self.cliente.save()
        
        form_data = {
            'fecha_venta': timezone.now(),
            'nro_comprobante': '001-001-0000001',
            'vendedor': 'Test Vendedor',
            'cliente': self.cliente.id,
            'total': Decimal('100.00'),
            'forma_pago': 'EFECTIVO',
            'iva_diez': Decimal('9.09'),
            'iva_cinco': Decimal('0.00'),
            'descuento': Decimal('0.00'),
            'timbrado': '12345678',
            'condicion_venta': 'Contado'
        }
        form = FormRegVentaCabecera(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('cliente', form.errors)
    
    def test_clean_total_cero(self):
        """Test: Error cuando el total es cero"""
        form_data = {
            'fecha_venta': timezone.now(),
            'nro_comprobante': '001-001-0000001',
            'vendedor': 'Test Vendedor',
            'cliente': self.cliente.id,
            'total': Decimal('0.00'),
            'forma_pago': 'EFECTIVO',
            'iva_diez': Decimal('0.00'),
            'iva_cinco': Decimal('0.00'),
            'descuento': Decimal('0.00'),
            'timbrado': '12345678',
            'condicion_venta': 'Contado'
        }
        form = FormRegVentaCabecera(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('total', form.errors)

@pytest.mark.django_db
class FormEditVentaDetalleTest(TestCase):
    """Tests para FormEditVentaDetalle"""
    
    def setUp(self):
        """Configuración inicial"""
        self.proveedor = Proveedor.objects.create(
            razon_social="mi proveedor",
            nro_documento="111",
            correo="correo@test.com",
            num_tel="12345678",
            tipo_documento="RUC",
            descripcion="Proveedor de servicios"
        )
        
        categoria = Categoria.objects.create(nombre='Cat', descripcion='Test')
        
        self.producto = Producto.objects.create(
            nombre='Producto Test',
            descripcion='Desc',
            categoria=categoria,
            unidad_medida='UNIDADES',
            cantidad_en_stock=50,
            precio_venta=Decimal('100.00'),
            precio_compra=Decimal('30.00'),
            iva=Decimal('10.00'),
            proveedor = self.proveedor
        )
    
    def test_form_valido(self):
        """Test: Formulario de edición válido"""
        form_data = {
            'producto_id': self.producto.id,
            'producto_nombre': 'Producto Test',
            'producto_iva': Decimal('10.00'),
            'descripcion': 'Test',
            'cantidad': 5,
            'unidad_medida': 'UNIDADES',
            'precio_unit_venta': Decimal('100.00'),
            'subtotal': Decimal('500.00')
        }
        form = FormEditVentaDetalle(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_cantidad_invalida(self):
        """Test: Error con cantidad inválida"""
        form_data = {
            'producto_id': self.producto.id,
            'producto_nombre': 'Producto Test',
            'producto_iva': Decimal('10.00'),
            'descripcion': 'Test',
            'cantidad': 0,
            'unidad_medida': 'UNIDADES',
            'precio_unit_venta': Decimal('100.00'),
            'subtotal': Decimal('0.00')
        }
        form = FormEditVentaDetalle(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('cantidad', form.errors)