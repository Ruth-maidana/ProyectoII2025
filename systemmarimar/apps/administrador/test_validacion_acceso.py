'''from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class LoginTestCase(TestCase):
    def setUp(self):
        self.username = "usuario_test"
        self.password = "password123"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            is_active=True
        )

    def test_login_correcto(self):
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': self.password
        })
        # Redirige a 'home' si el login es exitoso
        self.assertRedirects(response, reverse('home'))

    def test_login_incorrecto(self):
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': 'incorrecto'
        })
        # Debe quedarse en la página de login y mostrar mensaje de error
        self.assertContains(response, "Usuario o contraseña incorrectos", status_code=200)'''
        
        
        
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class LoginUserTests(TestCase):

    def setUp(self):
        """Crea usuarios para pruebas"""
        self.active_user = User.objects.create_user(username='user_activo', password='pass123')
        self.inactive_user = User.objects.create_user(username='user_inactivo', password='pass123', is_active=False)

    def test_login_correcto(self):
        """Debe autenticar al usuario activo y redirigir a 'home'"""
        response = self.client.post(reverse('login'), {
            'username': 'user_activo',
            'password': 'pass123',
        })
        self.assertRedirects(response, reverse('home'))

    def test_login_inactivo(self):
        """Usuario inactivo debería mostrar error y no permitir login"""
        response = self.client.post(reverse('login'), {
            'username': 'user_inactivo',
            'password': 'pass123',
        }, follow=True)
        self.assertContains(response, "Su cuenta está inactiva. Contacte al administrador.")

    def test_login_incorrecto(self):
        """Usuario o contraseña incorrectos deberían mostrar error"""
        response = self.client.post(reverse('login'), {
            'username': 'user_activo',
            'password': 'contraseña_incorrecta',
        }, follow=True)
        self.assertContains(response, "Usuario o contraseña incorrectos. Intente nuevamente.")

    def test_campos_vacios(self):
        """Debe mostrar error al enviar campos vacíos"""
        response = self.client.post(reverse('login'), {
            'username': '', 'password': ''
        }, follow=True)
        self.assertContains(response, "Por favor, complete todos los campos")

