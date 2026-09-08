from __future__ import annotations

import re

from nurus.domain.models import Product, Template

TOKEN = re.compile(r"\{([A-Z_]+)\}")


def render(template: Template, context: dict[str, str]) -> tuple[str, str, list[str]]:
    issues: list[str] = []
    permitted = set(template.allowed_variables)

    def replace(match: re.Match[str]) -> str:
        name = match.group(1)
        if name not in permitted:
            issues.append(f"Variable no permitida: {name}")
            return match.group(0)
        value = str(context.get(name, "")).strip()
        if not value:
            issues.append(f"Falta dato para: {name}")
            return match.group(0)
        return value

    subject = TOKEN.sub(replace, template.subject)
    body = TOKEN.sub(replace, template.body)
    return subject, body, list(dict.fromkeys(issues))


def prepare(product: Product) -> Product:
    subject, body, issues = render(product.template, product.context)
    product.rendered_subject, product.rendered_body = subject, body
    product.issues = issues
    if product.kind.value == "email" and not product.recipient.strip():
        product.issues.append("Sin destinatario: queda disponible para completar manualmente.")
    product.mark_ready()
    return product
