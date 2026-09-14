"""Importación y actualización local de matrices proporcionadas por el usuario."""
from pathlib import Path
from zipfile import ZipFile
from io import BytesIO
from docx import Document
import re
import shutil
from nurus.rus.columns import normalize

BUNDLED_REVISION='2026-09-14-matrices-1'

def install_bundled_templates(source,directory,revision=BUNDLED_REVISION):
    """Instala una revisión de matrices una sola vez y respalda las anteriores.

    Tras registrar la revisión, los inicios posteriores solo reponen archivos ausentes;
    por ello una edición manual posterior no se sobrescribe automáticamente.
    """
    source=Path(source);root=Path(directory);root.mkdir(parents=True,exist_ok=True)
    marker=root/'.bundled_revision'
    previous=marker.read_text(encoding='utf-8').strip() if marker.exists() else ''
    migrating=previous!=revision
    installed=[];backups=[];preserved=[]
    if source.exists():
        for path in sorted(source.rglob('*.docx')):
            relative=path.relative_to(source);target=root/relative;target.parent.mkdir(parents=True,exist_ok=True)
            if not target.exists():
                shutil.copyfile(path,target);installed.append(str(target));continue
            if not migrating:
                preserved.append(str(target));continue
            if target.read_bytes()==path.read_bytes():
                preserved.append(str(target));continue
            backup=target.with_name(target.stem+'.pre_'+revision.replace('-','_')+'.bak.docx')
            if not backup.exists():shutil.copyfile(target,backup)
            backups.append(str(backup));shutil.copyfile(path,target);installed.append(str(target))
    if migrating:
        temp=marker.with_suffix('.tmp');temp.write_text(revision,encoding='utf-8');temp.replace(marker)
    return {'revision':revision,'installed':installed,'backups':backups,'preserved':preserved}

def import_templates(path,directory):
    root=Path(directory);pending={};unmatched=[]
    with ZipFile(path) as archive:
        for item in archive.infolist():
            if item.is_dir() or not item.filename.lower().endswith('.docx'):continue
            name=normalize(item.filename.replace('_',' ').replace('\\','/')).upper()
            courts=[c for c in ('LAJA','MULCHEN','TOME') if re.search(r'\b'+c+r'\b',name)]
            kinds=[k for k,pattern in [('PC_IE',r'\bPC IE\b'),('PC_INFO',r'\bPC INFO\b'),('NOMENCL',r'\bNOMENCL(?:ATURA)?\b')] if re.search(pattern,name)]
            if len(courts)!=1 or len(kinds)!=1:unmatched.append(item.filename);continue
            if item.file_size>20_000_000:raise ValueError('Matriz demasiado grande: '+item.filename)
            content=archive.read(item)
            Document(BytesIO(content)) # valida DOCX antes de sustituir cualquier matriz
            key=(courts[0],kinds[0])
            if key in pending:raise ValueError('Hay dos matrices para '+('/'.join(key))+'. Conserva una versión por tipo.')
            pending[key]=content
    imported=[]
    for (court,kind),content in pending.items():
        target=root/court/(kind+'.docx');target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():shutil.copyfile(target,target.with_suffix('.bak.docx'))
        temp=target.with_suffix('.tmp');temp.write_bytes(content);temp.replace(target)
        imported.append(str(target))
    return {'imported':imported,'unmatched':unmatched}
