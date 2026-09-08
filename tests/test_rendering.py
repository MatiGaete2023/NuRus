from nurus.domain.models import Product, ProductKind, ProductStatus, Template
from nurus.services.rendering import prepare, render


def email_template() -> Template:
    return Template("x", "Correo", ProductKind.EMAIL, "Ingreso {TRIBUNAL}", "Hola {PROGRAMA}", ("TRIBUNAL", "PROGRAMA"), "published")


def test_missing_recipient_is_blocked_but_preserved_for_manual_review():
    product = prepare(Product(ProductKind.EMAIL, email_template(), {"TRIBUNAL": "Laja", "PROGRAMA": "PRM"}))
    assert product.status is ProductStatus.BLOCKED
    assert any("Sin destinatario" in issue for issue in product.issues)


def test_unknown_variable_is_never_silently_consumed():
    template = Template("x", "x", ProductKind.EMAIL, "{INEXISTENTE}", "x", ("TRIBUNAL",), "published")
    subject, _, issues = render(template, {"TRIBUNAL": "Laja"})
    assert subject == "{INEXISTENTE}"
    assert issues == ["Variable no permitida: INEXISTENTE"]


def test_product_with_recipient_and_data_is_ready():
    product = prepare(Product(ProductKind.EMAIL, email_template(), {"TRIBUNAL": "Jgdo. L. y G. de Laja", "PROGRAMA": "PRM Alfa"}, recipient="prm@example.invalid"))
    assert product.status is ProductStatus.READY
    assert "Jgdo. L. y G. de Laja" in product.rendered_subject
