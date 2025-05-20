from django.test import TestCase
from .models import Cliente
from django.core.exceptions import ValidationError

class VentasTestCase(TestCase):

    def setUp(self):
        # Crear datos iniciales para las pruebas
        self.cliente = Cliente.objects.create(
            nombre="Cliente Test",
            nro_documento="123456789",
            direccion="Calle Falsa 123",
            num_tel="+595981234567",
            correo="cliente@test.com"
        )
        
    def test_insertar_cliente_correctamente(self):
        cliente = Cliente.objects.create(
            nombre="Nuevo Cliente",
            nro_documento="987654321",
            direccion="Calle Nueva 456",
            num_tel="+595987654321",
            correo="nuevo_cliente@test.com"
        )
        self.assertEqual(cliente.nombre, "Nuevo Cliente")
        self.assertEqual(cliente.nro_documento, "987654321")
        print('Test Unitario insertar Cliente ')


    def test_editar_cliente_correctamente(self):
        self.cliente.nombre = "Cliente Editado"
        self.cliente.direccion = "Calle Editada 789"
        self.cliente.save()
        self.assertEqual(self.cliente.nombre, "Cliente Editado")
        self.assertEqual(self.cliente.direccion, "Calle Editada 789")
        print('Test Unitario editar Cliente ')

    def test_insertar_cliente_sin_datos_obligatorios(self):
        with self.assertRaises(ValidationError):
            cliente = Cliente(
                nombre="",  # Nombre vacío
                nro_documento="",  # Documento vacío
                correo="correo_invalido"
            )
            cliente.full_clean()  # Validar errores antes de guardar
        print('Test Validacion de datos Cliente')

    def test_integral_crear_y_editar_cliente(self):
        # Crear un cliente
        cliente = Cliente.objects.create(
            nombre="Cliente Integral",
            nro_documento="111222333",
            direccion="Calle Integral 123",
            num_tel="+595999888777",
            correo="integral@test.com"
        )
        self.assertEqual(cliente.nombre, "Cliente Integral")
        self.assertEqual(cliente.nro_documento, "111222333")

        # Editar el cliente
        cliente.nombre = "Cliente Integral Editado"
        cliente.direccion = "Calle Integral Editada 456"
        cliente.save()

        # Verificar los cambios
        cliente_actualizado = Cliente.objects.get(id=cliente.id)
        self.assertEqual(cliente_actualizado.nombre, "Cliente Integral Editado")
        self.assertEqual(cliente_actualizado.direccion, "Calle Integral Editada 456")
        print('Test Integral Cliente ')
