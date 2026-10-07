import unittest
from lxml import html
from vinculos import calls,extract,match_rows


def listing(court='777',duplicate=False):
    row=f'''<tr><td>X-1-2026</td><td>11111111-1</td><td>Persona ficticia</td><td>PRM Centro ficticio</td><td>
        <a onclick="ShowHistoria('{court}','X-1-2026','100')">Causa</a>
        <a onclick="ShowObservaciones('100','{court}','200','12','3','0')">Obs</a>
        <a onclick="ShowInformesProgramados('100','300','{court}','400','X-1-2026','01/01/2026','PRM Centro ficticio','Persona ficticia','12','3','200','0')">Inf</a>
        </td></tr>'''
    return html.fromstring('<table><thead><tr><th>RIT</th><th>RUT</th><th>Nombre</th><th>Derivación</th><th>Acciones</th></tr></thead><tbody>'+row+(row.replace("'200'","'201'") if duplicate else '')+'</tbody></table>')


class BindingTests(unittest.TestCase):
    def test_literals_respect_punctuation_and_do_not_execute(self):
        self.assertEqual(calls('ShowObservaciones("texto (con, comas)","123")','ShowObservaciones'),[['texto (con, comas)','123']])
        self.assertEqual(calls("ShowObservaciones(__import__('os'),123)",'ShowObservaciones'),[])
        self.assertEqual(calls('ShowObservaciones(document.value,123)','ShowObservaciones'),[])

    def test_actual_ingreso_ids_and_calendar_are_consistent(self):
        found=extract(listing(),'777');self.assertEqual(len(found),1)
        self.assertEqual(found[0]['ingreso_id'],'200');self.assertEqual(found[0]['centro_id'],'400');self.assertEqual(found[0]['persona_id'],'300')
        self.assertEqual(extract(listing(court='888'),'777'),[])

    def test_binding_uses_full_identity_and_rejects_ambiguous_ingresos(self):
        headers=('RIT','RUT','NOMBRE','NOMBRE CENTRO')
        rows=[(2,('X-1-2026','11.111.111-1','Persona ficticia','PRM Centro ficticio')),
              (3,('X-1-2026','11111111-1','Otra persona','PRM Centro ficticio'))]
        columns,output=match_rows(headers,rows,extract(listing(),'777'),'777');ingreso=columns.index('SITFA_INGRESO_RUS')
        self.assertEqual(output[0][1][ingreso],'200');self.assertEqual(output[1][1][-1],'Sin vínculo comprobado')
        _,output=match_rows(headers,rows[:1],extract(listing(duplicate=True),'777'),'777')
        self.assertEqual(output[0][1][-1],'Identidad ambigua');self.assertEqual(output[0][1][ingreso],'')
