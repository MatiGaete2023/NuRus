from nurus.personal.diagnostics import format_installation_info,installation_info


def test_reports_effective_exe_and_frozen_module_path():
    info=installation_info(executable=r'C:\release\CSMP_Integral.exe',
        personal_module=r'C:\release\CSMP_Integral\_internal\nurus\personal\__init__.py',
        frozen=True,version='0.4.0.dev18',commit='abcdef1234567890')
    assert info['origin']=='EXE congelado'
    rendered=format_installation_info(info)
    assert 'Commit fuente: abcdef123456' in rendered
    assert 'C:\\release\\CSMP_Integral.exe' in rendered
    assert 'C:\\release\\CSMP_Integral\\_internal\\nurus\\personal' in rendered


def test_distinguishes_installed_virtualenv_from_source_checkout():
    installed=installation_info(executable=r'C:\app\.venv-csmp\Scripts\python.exe',
        personal_module=r'C:\app\.venv-csmp\Lib\site-packages\nurus\personal\__init__.py',
        frozen=False,version='0.4.0.dev18',commit='')
    source=installation_info(executable=r'C:\Python\python.exe',
        personal_module=r'C:\work\csmp\src\nurus\personal\__init__.py',
        frozen=False,version='0.4.0.dev18',commit='')
    assert installed['origin']=='Paquete instalado'
    assert source['origin']=='Código fuente'
    assert 'Commit fuente: No declarado' in format_installation_info(source)
