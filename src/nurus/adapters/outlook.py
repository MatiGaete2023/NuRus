from __future__ import annotations

import platform

from nurus.domain.models import Product, ProductStatus


class OutlookUnavailable(RuntimeError):
    pass


def create_draft(product: Product) -> Product:
    """Crea un borrador, nunca envía. El llamador debe confirmar previamente."""
    if product.status.value != "ready":
        raise ValueError("Solo se pueden crear productos revisados y completos.")
    if not product.recipient:
        raise ValueError("No se crea Outlook sin destinatario; complete el producto primero.")
    if platform.system() != "Windows":
        raise OutlookUnavailable("Outlook Object Model solo se prueba en Windows con Outlook clásico.")
    try:
        import win32com.client  # type: ignore[import-not-found]
    except ImportError as exc:
        raise OutlookUnavailable("Instale pywin32 en el equipo Windows autorizado.") from exc
    outlook = win32com.client.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)
    mail.To, mail.CC = product.recipient, product.cc
    mail.Subject, mail.Body = product.rendered_subject, product.rendered_body
    mail.Save()
    product.status = ProductStatus.CREATED
    return product
