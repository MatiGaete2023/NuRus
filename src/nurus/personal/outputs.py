"""Salidas desde el trabajo compartido. No modifica RUS ni envía correos."""
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from hashlib import sha256
from pathlib import Path
from string import Formatter
from uuid import uuid4
import json
import re

from nurus.domain.models import Product, ProductKind, ProductStatus, Template
from nurus.adapters.outlook import save_draft, DraftSaveUncertain
from nurus.rus.columns import normalize
from nurus.rus.rules import tribunal
from nurus.services.file_output import write_new_file
from .config import CC, emails

@dataclass
class Draft:
    subject: str
    body: str
    to: str = ''
    cc: str = CC
    attachments: list = field(default_factory=list)
    required: bool = False
    key: str = ''

def value(work,row,key):
    return str(row.values.get(work.mapping.get(key,''),'') or '')

def resolve_contact(cfg,name):
    key=normalize(name)
    aliases={normalize(k):normalize(v) for k,v in cfg['aliases'].items()}
    key=aliases.get(key,key)
    found={v for k,v in cfg['contactos'].items() if normalize(k)==key and v.strip()}
    return next(iter(found)) if len(found)==1 else ''

def import_contacts(cfg,path):
    import pandas as pd
    frame=pd.read_excel(path,dtype=str).fillna('')
    columns={normalize(c):c for c in frame.columns}
    name=next((columns[k] for k in ('nombre','programa','nombre programa') if k in columns),None)
    address=next((columns[k] for k in ('mail','correo','email','correo electronico') if k in columns),None)
    if not name or not address:raise ValueError('El catastro necesita columnas Nombre/Programa y Mail/Correo.')
    candidates=dict(cfg['contactos']);conflicts=[]
    for record in frame.to_dict('records'):
        n=str(record[name]).strip();m='; '.join(emails(record[address]))
        if not n:continue
        previous={v for k,v in candidates.items() if normalize(k)==normalize(n)}
        if previous and previous!={m}:conflicts.append(n);continue
        candidates[n]=m
    return candidates,conflicts

def _table(work,rows,path):
    from openpyxl import Workbook
    from openpyxl.styles import Font
    book=Workbook();sheet=book.active;sheet.title='Nómina'
    headers=['RIT','TRIBUNAL','RUT','NOMBRE','PROGRAMA','VENCIMIENTO / ESPERA','OBSERVACION']
    sheet.append(headers)
    for row in rows:
        sheet.append([value(work,row,k) for k in ('rit','tribunal','rut','nombre','programa')]+[value(work,row,'vencimiento') or value(work,row,'espera'),str(row.review.get('OBSERVACION') or row.observation)])
        for cell in sheet[sheet.max_row]:cell.data_type='s'
    sheet.freeze_panes='A2';sheet.auto_filter.ref=sheet.dimensions
    for cell in sheet[1]:cell.font=Font(bold=True)
    for col in ('A','B','C','D','E','F','G'):sheet.column_dimensions[col].width=25 if col!='G' else 65
    write_new_file(Path(path),book.save)
    return str(path)

def prepare_drafts(work,kind,*,modalities='',period='',confirmed_scope=False,selected=None,directory=None,manual_selection=False):
    work.refresh()
    cfg=work.config
    tpl=cfg['correos']['plantillas'][kind]
    general=kind in {'espera','cumplimiento','informes'}
    if general and not confirmed_scope:raise ValueError('Confirma el alcance efectivamente revisado en RUS antes del correo informativo.')
    if general and kind.upper()!=work.mode:raise ValueError('La pestaña del correo no corresponde al trabajo actual.')
    if tpl.get('usa_modalidades') and not modalities.strip():raise ValueError('Indica las modalidades efectivamente comprendidas.')
    groups=defaultdict(list)
    for row in work.rows:
        if row.excluded or (selected is not None and row.id not in selected):continue
        if not general and kind not in {'especial','proyectos'} and kind not in row.actions and not (manual_selection and selected is not None):continue
        if kind=='proyectos' and row.id not in {r.get('record_id') for r in work.receipts.values() if r.get('kind')=='word'}:continue
        court=tribunal(value(work,row,'tribunal')) or value(work,row,'tribunal')
        program=value(work,row,'programa') if kind.startswith('programa_') else ''
        groups[(court,normalize(program))].append(row)
    output=[]
    for (court,_),rows in groups.items():
        court_cfg=cfg['correos']['tribunales'].get(court,{'nombre':court,'para':[]})
        program=value(work,rows[0],'programa')
        context={'TRIBUNAL':court_cfg['nombre'],'PROGRAMA':program,'FECHA':date.today().strftime('%d/%m/%Y'),
                 'ALCANCE_MODALIDADES':modalities,'PERIODO':period,'TABLA_REGISTROS':'\n'.join(value(work,r,'rit')+' — '+value(work,r,'nombre') for r in rows)}
        for text in (tpl['asunto'],tpl['cuerpo']):
            for _,key,_,_ in Formatter().parse(text):
                if key and not context.get(key,'').strip():raise ValueError('Completa '+key+' para esta plantilla.')
        to=resolve_contact(cfg,program) if kind.startswith('programa_') else '; '.join(court_cfg['para'])
        draft=Draft(tpl['asunto'].format_map(context),tpl['cuerpo'].format_map(context),to,
                    '; '.join(emails(CC+';'+cfg['correos'].get('cc_adicional',''))),required=tpl['adjunto']=='obligatorio')
        if cfg.get('firma'):draft.body+='\n\n'+cfg['firma']
        if draft.required:
            folder=Path(directory or Path(work.output).parent);folder.mkdir(parents=True,exist_ok=True)
            draft.attachments=[_table(work,rows,folder/('Nomina_'+uuid4().hex[:10]+'.xlsx'))]
        draft.key=sha256((kind+'|'+','.join(r.id for r in rows)+'|'+draft.subject).encode()).hexdigest()
        output.append(draft)
    return output

def create_draft(work,draft,*,confirmed=False):
    if not confirmed:raise ValueError('Revisa destinatarios, texto y adjuntos antes de crear el borrador.')
    if not draft.key:draft.key=sha256((draft.subject+'|'+draft.body+'|'+draft.to).encode()).hexdigest()
    if draft.key in work.receipts:raise ValueError('Este borrador ya se creó o su guardado quedó incierto; revisa Outlook antes de repetir.')
    to='; '.join(emails(draft.to));cc='; '.join(emails(CC+';'+draft.cc))
    if draft.required and not draft.attachments:raise ValueError('Este correo requiere adjunto.')
    attachments=[]
    for file in draft.attachments:
        path=Path(file).resolve()
        if not path.is_file():raise ValueError('Adjunto no disponible: '+str(path))
        attachments.append((str(path),sha256(path.read_bytes()).hexdigest()))
    tpl=Template('personal','Correo revisado',ProductKind.EMAIL,'','',())
    product=Product(ProductKind.EMAIL,tpl,{},recipient=to,cc=cc,attachments=attachments,required_attachment=draft.required,
                    status=ProductStatus.READY,rendered_subject=draft.subject,rendered_body=draft.body)
    work.receipts[draft.key]={'kind':'draft','state':'saving'}
    if getattr(work,'storage_directory',None):work.save(work.storage_directory)
    try:
        receipt=save_draft(product,confirmed=True,account_key=work.config.get('cuenta_outlook') or None,preserve_signature=True)
    except DraftSaveUncertain:
        work.receipts[draft.key]={'kind':'draft','state':'uncertain'}
        if getattr(work,'storage_directory',None):work.save(work.storage_directory)
        raise
    except Exception:
        work.receipts.pop(draft.key,None)
        if getattr(work,'storage_directory',None):work.save(work.storage_directory)
        raise
    work.receipts[draft.key]={'kind':'draft','state':'created','entry_id':receipt.entry_id,'store_id':receipt.store_id}
    if getattr(work,'storage_directory',None):work.save(work.storage_directory)
    return receipt

def fill_docx(template,destination,values):
    """Sustituye tokens entre runs sin reconstruir párrafos ni eliminar estilos."""
    from zipfile import ZipFile, ZIP_DEFLATED
    from lxml import etree as ET
    token=re.compile(r'\{\{([A-Z_]+)\}\}')
    ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    with ZipFile(template) as source:
        content={item.filename:source.read(item.filename) for item in source.infolist()}
    for name,data in list(content.items()):
        if not name.startswith('word/') or not name.endswith('.xml'):continue
        root=ET.fromstring(data,parser=ET.XMLParser(resolve_entities=False,no_network=True))
        changed=False
        for paragraph in root.findall('.//w:p',ns):
            nodes=paragraph.findall('.//w:t',ns)
            full=''.join(n.text or '' for n in nodes)
            for match in reversed(list(token.finditer(full))):
                key=match.group(1)
                replacement=str(values.get(key,'')).strip()
                if not replacement:raise ValueError('Falta la variable Word: '+key)
                pos=0;parts=[]
                for node in nodes:
                    length=len(node.text or '');parts.append((node,pos,pos+length));pos+=length
                affected=[(n,a,b) for n,a,b in parts if a<match.end() and b>match.start()]
                first,a,b=affected[0];last,la,lb=affected[-1]
                prefix=(first.text or '')[:match.start()-a]
                suffix=(last.text or '')[match.end()-la:]
                first.text=prefix+replacement+(suffix if first is last else '')
                first.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
                for node,_,_ in affected[1:]:node.text=suffix if node is last else ''
                changed=True
        if changed:content[name]=ET.tostring(root,encoding='utf-8',xml_declaration=True)
    def write(path):
        with ZipFile(path,'w',ZIP_DEFLATED) as out:
            for name,data in content.items():out.writestr(name,data)
    write_new_file(Path(destination),write)
    return str(destination)

def word_values(work,row):
    from nurus.rus.rules import format_date, as_date
    durations=[str(v) for k,v in row.values.items() if normalize(k) in ('duracion','plazo','vigencia')]
    vals={key.upper():value(work,row,key) for key in ('rit','rut','nombre','programa')}
    resolution=as_date(row.values.get(work.mapping.get('resolucion','')))
    vals.update(FECHA=format_date(date.today()),FECHA_RESOLUCION=resolution.strftime('%d/%m/%Y') if resolution else '',DURACION=durations[0] if len(durations)==1 else '')
    return vals

def template_variables(path):
    from zipfile import ZipFile
    from lxml import etree as ET
    result=set()
    with ZipFile(path) as z:
        for name in z.namelist():
            if name.startswith('word/') and name.endswith('.xml'):
                root=ET.fromstring(z.read(name),parser=ET.XMLParser(resolve_entities=False,no_network=True))
                for p in root.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
                    text=''.join(p.itertext())
                    result.update(re.findall(r'\{\{([A-Z_]+)\}\}',text))
    return result

def generate_word(work,row,kind,template_dir,destination,*,confirmed=False,extra=None):
    if not confirmed:raise ValueError('Verifica primer pide cuenta y antecedentes de la carpeta judicial.')
    if row.excluded:raise ValueError('La fila está excluida del seguimiento.')
    work.refresh()
    court=tribunal(value(work,row,'tribunal'))
    if not court or kind not in {'PC_IE','PC_INFO','NOMENCL'}:raise ValueError('Tribunal o tipo de proyecto no reconocido.')
    template=Path(template_dir)/court/(kind+'.docx')
    if not template.exists():raise ValueError(f'Sin plantilla {court}/{kind}. Incorpora la matriz Word correspondiente en Configuración.')
    vals=word_values(work,row)
    if extra:vals.update(extra)
    result=fill_docx(template,destination,vals)
    work.receipts[uuid4().hex]={'kind':'word','record_id':row.id,'path':result,'type':kind}
    return result
