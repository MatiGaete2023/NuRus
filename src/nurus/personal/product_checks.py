"""Read-only preflight for current products and explicit effects."""
from dataclasses import dataclass, field
from pathlib import Path
from hashlib import sha256
import json
from .product_state import stale, dependency_scope
from .outputs import emails,draft_fingerprint


@dataclass
class Check:
    id: str
    label: str
    kind: str
    state: str
    target: object = None
    index: int | None = None
    path: str = ''
    issues: list = field(default_factory=list)


def project_hash(project):
    return sha256(json.dumps({'text':project.text,'values':project.values,'template_hash':project.template_hash},sort_keys=True,ensure_ascii=False,default=str).encode()).hexdigest()


def check_products(work,drafts,projects):
    checks=[]
    with dependency_scope(work):
        for index,draft in enumerate(drafts):
            issues=[]
            try:
                if not emails(draft.to):issues.append('Completar destinatario')
                emails(draft.cc)
            except ValueError as exc:issues.append(str(exc))
            if not draft.subject.strip():issues.append('Completar asunto')
            if not draft.body.strip():issues.append('Completar cuerpo')
            if not draft.roster_reviewed:issues.append('Revisar nómina y generar adjuntos')
            if draft.required and not draft.attachments:issues.append('Agregar adjunto obligatorio')
            for path in draft.attachments:
                if not Path(path).is_file():issues.append('Adjunto no disponible: '+Path(path).name)
            if work and stale(work,draft):issues.append('Actualizar producto: cambiaron sus datos o plantilla')
            receipt=None
            if work and not any(not Path(p).is_file() for p in draft.attachments):
                receipt=work.receipts.get(draft_fingerprint(draft))
            state='Por corregir' if issues else 'Listo para revisar'
            if receipt:
                state='Guardado en Outlook' if receipt.get('state')=='created' else 'Guardado incierto · comprobar Outlook'
                if receipt.get('state')!='created':issues.append('Comprobar en Outlook antes de repetir')
            checks.append(Check('draft:'+draft.product_id,draft.subject or 'Correo sin asunto','Correo',state,draft,index,issues=issues))
        for index,project in enumerate(projects):
            issues=[]
            if project.review_required:issues.append('Revisar cambios del proyecto')
            if work and stale(work,project):issues.append('Actualizar datos o matriz del proyecto')
            from .word_quality import unresolved_text,pending_fields
            matching=[]
            if work:
                for r in work.receipts.values():
                    if r.get('kind')!='word' or r.get('state')!='generated':continue
                    if r.get('product_id')==project.key and r.get('product_hash')==project_hash(project):matching.append(r)
                    elif not r.get('product_id') and set(project.record_ids)==set(r.get('record_ids',[])) and r.get('type')==project.kind:matching.append(r)
            path=next((r['path'] for r in reversed(matching) if Path(r.get('path','')).is_file()),'')
            if pending_fields(path) if path else unresolved_text(project.text):issues.append('Completar campos pendientes del documento')
            state='Por corregir' if issues else 'Generado' if path else 'Listo para generar'
            checks.append(Check('word:'+project.key,project.rit+' · '+project.kind,'Word',state,project,index,path,issues))
        if work:
            paths={getattr(work,'output',''):('Copia Excel actual','Excel',[])}
            for draft in drafts:
                for group in draft.roster:
                    path=group.get('generated','')
                    if path:paths[path]=(group['program'],'Nómina Excel',['Revisar y regenerar nómina'] if not draft.roster_reviewed or stale(work,draft) else [])
            for path,(label,kind,issues) in paths.items():
                if not path:continue
                available=Path(path).is_file()
                checks.append(Check('file:'+str(Path(path).resolve()),label,kind,'Por corregir' if issues else 'Generado' if available else 'No disponible',path=path,issues=issues if available else ['No se encuentra el archivo']))
    return checks
