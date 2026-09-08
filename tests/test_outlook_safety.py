from __future__ import annotations

import sys
import types

import pytest

from nurus.adapters import outlook as outlook_adapter
from nurus.domain.models import Product, ProductKind, ProductStatus, Template
from nurus.services.rendering import prepare


def _product_without_recipient() -> Product:
    template = Template(
        "mail", "Correo", ProductKind.EMAIL,
        "Ingreso {TRIBUNAL}", "Hola {PROGRAMA}",
        ("TRIBUNAL", "PROGRAMA"), "published"
    )
    return prepare(
        Product(
            ProductKind.EMAIL,
            template,
            {"TRIBUNAL": "Laja", "PROGRAMA": "PRM"},
        )
    )


def test_create_draft_requires_explicit_confirmation():
    product = _product_without_recipient()
    with pytest.raises(ValueError, match="Confirma explícitamente"):
        outlook_adapter.create_draft(product)


def test_create_draft_allows_empty_recipient_and_never_sends(monkeypatch):
    product = _product_without_recipient()
    assert product.status is ProductStatus.READY

    class FakeMail:
        def __init__(self):
            self.To = None
            self.CC = None
            self.Subject = None
            self.Body = None
            self.saved = False
            self.send_called = False

        def Save(self):
            self.saved = True

        def Send(self):
            self.send_called = True
            raise AssertionError("NuRus no puede llamar Send")

    mail = FakeMail()

    class FakeOutlook:
        def CreateItem(self, kind):
            assert kind == 0
            return mail

    client_module = types.ModuleType("win32com.client")
    client_module.Dispatch = lambda name: FakeOutlook()
    win32com_module = types.ModuleType("win32com")
    win32com_module.client = client_module
    monkeypatch.setitem(sys.modules, "win32com", win32com_module)
    monkeypatch.setitem(sys.modules, "win32com.client", client_module)
    monkeypatch.setattr(outlook_adapter.platform, "system", lambda: "Windows")

    result = outlook_adapter.create_draft(product, confirmed=True)

    assert result.status is ProductStatus.CREATED
    assert mail.saved is True
    assert mail.send_called is False
    assert mail.To == ""
    assert mail.CC == ""
