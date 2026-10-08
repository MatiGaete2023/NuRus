import json,sys
from pathlib import Path
import pytest
from nurus.personal.integral_contract import validate,REQUIRED
from nurus.personal.bitacora_link import verify_reply
from hashlib import sha256


def cli(tmp_path,data,exit_code=0):
    script=tmp_path/'fixture.py'
    script.write_text('import pathlib,sys\npathlib.Path(sys.argv[-1]).write_text('+repr(json.dumps(data))+')\nsys.exit('+str(exit_code)+')',encoding='utf-8')
    return [sys.executable,str(script)]


def test_actual_cli_exchange_requires_all_three_protocols(tmp_path):
    data={'tipo':'CSMP_RUS_CAPACIDADES','protocolos':REQUIRED,'escritura_rus':False,'version':'2.7.0','commit':'fixture'}
    assert validate(cli(tmp_path,data),tmp_path/'requests')==data


@pytest.mark.parametrize('change',[
    {'protocolos':{'bitacoras_lectura':1}}, {'escritura_rus':True},
    {'tipo':'OTRO'}, {'version':None}, {'commit':''},
])
def test_incompatible_executable_is_rejected_before_launch(tmp_path,change):
    data={'tipo':'CSMP_RUS_CAPACIDADES','protocolos':REQUIRED,'escritura_rus':False,'version':'2.7.0','commit':'fixture',**change}
    with pytest.raises(ValueError,match='no acredita'):validate(cli(tmp_path,data),tmp_path/'requests')


def test_failed_executable_is_rejected_even_if_it_writes_json(tmp_path):
    with pytest.raises(ValueError,match='no acredita'):validate(cli(tmp_path,{},1),tmp_path/'requests')


def test_return_must_match_the_executable_used_for_the_request(tmp_path):
    folder=tmp_path/'request';lot=folder/'lotes'/'lot';lot.mkdir(parents=True)
    manifest=lot/'bitacoras.json';manifest.write_text(json.dumps({'origen':{'version':'2.7.0','commit':'fixture'}}))
    reply={'id':'fixture','manifest':str(manifest),'sha256':sha256(manifest.read_bytes()).hexdigest()}
    (folder/'respuesta.json').write_text(json.dumps(reply))
    request={'id':'fixture','folder':str(folder),'descargador':{'version':'2.7.0','commit':'fixture'}}
    assert verify_reply(request)==manifest.resolve()
    request['descargador']['commit']='otro'
    with pytest.raises(ValueError,match='otro descargador'):verify_reply(request)
