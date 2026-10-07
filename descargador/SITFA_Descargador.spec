# Distribución Windows sin Python instalado; la extensión mantiene instalación manual.
from PyInstaller.utils.hooks import collect_data_files
datas=collect_data_files('reportlab')+collect_data_files('PIL')
datas+=[('extension','extension')]
a=Analysis(['descargador.py'],pathex=[],binaries=[],datas=datas,hiddenimports=['xlrd','openpyxl','tzdata'],hookspath=[],runtime_hooks=[],excludes=[])
pyz=PYZ(a.pure)
exe=EXE(pyz,a.scripts,[],exclude_binaries=True,name='SITFA_Descargador',debug=False,strip=False,upx=False,console=False)
coll=COLLECT(exe,a.binaries,a.datas,strip=False,upx=False,name='SITFA_Descargador')
