import pytest
from django.core.exceptions import ValidationError
from apps.compras.models import Proveedor

@pytest.mark.django_db
class TestProveedor:

    def test_creacion_proveedor_valido(self):
        prov = Proveedor.objects.create(
            razon_social="Mi Empresa",
            nro_documento="123456",
            codigo_pais="+595",
            num_tel="98765432",
            correo="test@mail.com",
            descripcion="Proveedor de prueba",
            tipo_documento="RUC"
        )
        assert prov.razon_social == "MI EMPRESA"  # debe estar en mayúsculas
        assert prov.telefono_completo == "+595 98765432"

    def test_numero_paraguay_invalido(self):
        prov = Proveedor(
            razon_social="Proveedor Py",
            nro_documento="123",
            codigo_pais="+595",
            num_tel="12345",  # menos de 8
            correo="prov@mail.com",
            descripcion="Test",
            tipo_documento="RUC"
        )
        with pytest.raises(ValidationError) as excinfo:
            prov.full_clean()
        assert "mínimo 8 dígitos" in str(excinfo.value)

    def test_numero_usa_invalido(self):
        prov = Proveedor(
            razon_social="Proveedor USA",
            nro_documento="456",
            codigo_pais="+1",
            num_tel="123456",  # no tiene 10
            correo="usa@mail.com",
            descripcion="Test",
            tipo_documento="RUC"
        )
        with pytest.raises(ValidationError) as excinfo:
            prov.full_clean()
        assert "exactamente 10 dígitos" in str(excinfo.value)

    def test_razon_social_unica_case_insensitive(self):
        Proveedor.objects.create(
            razon_social="Proveedor Uno",
            nro_documento="111",
            codigo_pais="+595",
            num_tel="12345678",
            correo="uno@mail.com",
            descripcion="Test",
            tipo_documento="RUC"
        )
        prov2 = Proveedor(
            razon_social="proveedor uno",
            nro_documento="222",
            codigo_pais="+595",
            num_tel="87654321",
            correo="dos@mail.com",
            descripcion="Otro",
            tipo_documento="CI"
        )
        with pytest.raises(ValidationError) as excinfo:
            prov2.full_clean()
        assert "Ya existe un proveedor con este nombre." in str(excinfo.value)
