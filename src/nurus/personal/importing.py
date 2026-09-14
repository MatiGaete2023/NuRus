"""Lectura de planillas revisadas con encabezados desplazados y alias RUS."""
from io import BytesIO
from pathlib import Path
from hashlib import sha256
from nurus.rus.columns import map_columns, normalize, ColumnMappingError

class SheetChoice(ValueError):
    def __init__(self,names):
        self.names=list(names)
        super().__init__('El libro contiene varias tablas: '+', '.join(self.names))

def read_external(path,mode='ESPERA',sheet=None):
    import pandas as pd
    path=Path(path).resolve()
    content=path.read_bytes()
    requested=str(mode).upper()
    distinctive={'ESPERA':'espera','CUMPLIMIENTO':'dias_cumpl','INFORMES':'vencimiento'}
    candidates=[]
    with pd.ExcelFile(BytesIO(content),engine='xlrd' if path.suffix.lower()=='.xls' else 'openpyxl') as book:
        for name in book.sheet_names:
            if sheet and name!=sheet:continue
            preview=pd.read_excel(book,sheet_name=name,header=None,nrows=60,dtype=object,keep_default_na=False)
            for i,values in enumerate(preview.itertuples(index=False,name=None)):
                headers=[str(v).strip() if str(v).strip() else '__col_'+str(j) for j,v in enumerate(values)]
                if len({normalize(h) for h in headers})!=len(headers):continue
                try:requested_mapping=map_columns(headers,requested)
                except ColumnMappingError:continue
                if not all(requested_mapping.get(k) for k in ('rit','tribunal','nombre')):continue
                detected=requested
                mapping=requested_mapping
                # La modalidad elegida por el usuario manda. Solo inferimos otra cuando
                # el libro carece de la columna distintiva solicitada y hay una única
                # modalidad inequívoca en los encabezados.
                if distinctive[requested] not in requested_mapping:
                    inferred=[]
                    for candidate in ('ESPERA','CUMPLIMIENTO','INFORMES'):
                        try:candidate_mapping=map_columns(headers,candidate)
                        except ColumnMappingError:continue
                        if distinctive[candidate] in candidate_mapping:
                            inferred.append((candidate,candidate_mapping))
                    if len(inferred)==1:
                        detected,mapping=inferred[0]
                # Los campos humanos usan el mismo nombre interno cualquiera sea su alias.
                human={}
                for key,aliases in {'OBSERVACION':('observacion','observaciones'),'FECHA_OBS':('fecha_obs','fecha obs','fecha observacion'),'TT':('tt',),'CC':('cc',),'RES':('res','resolucion generada')}.items():
                    found=[h for h in headers if normalize(h) in {normalize(a) for a in aliases}]
                    if len(found)==1:human[key]=found[0]
                candidates.append((name,i+1,headers,mapping,detected,human))
                break
        if not candidates:raise ValueError('No se encontró una tabla con RIT, TRIBUNAL y NOMBRE en las primeras 60 filas. Revisa la hoja y sus encabezados.')
        if len(candidates)>1:
            preferred=[c for c in candidates if normalize(c[0])==normalize(requested)]
            if len(preferred)!=1:raise SheetChoice(c[0] for c in candidates)
            chosen=preferred[0]
        else:chosen=candidates[0]
        name,header,headers,mapping,detected,human=chosen
        frame=pd.read_excel(book,sheet_name=name,header=None,skiprows=header,dtype=object,keep_default_na=False)
        records=[]
        for offset,vals in enumerate(frame.itertuples(index=False,name=None),header+1):
            row={h:vals[j] if j<len(vals) else '' for j,h in enumerate(headers)}
            if not str(row.get(mapping['rit'],'')).strip() or not str(row.get(mapping['nombre'],'')).strip():continue
            review={key:row.get(col,'') for key,col in human.items()}
            records.append((offset,row,review))
    return dict(path=str(path),content=content,digest=sha256(content).hexdigest(),sheet=name,header=header,mapping=mapping,mode=detected,records=records)
