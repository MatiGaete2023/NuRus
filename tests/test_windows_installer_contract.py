from pathlib import Path


def test_windows_installer_detects_python_without_requiring_py_launcher():
    script = (Path(__file__).parents[1] / "Instalar_NuRus.bat").read_text(encoding="utf-8")
    assert "call :try_python py -3.12" in script
    assert "call :try_python python" in script
    assert "call :try_python python3.12" in script
    assert "%LOCALAPPDATA%\\Programs\\Python\\Python312\\python.exe" in script
    assert "sys.version_info[:2] == (3, 12)" in script
    assert "excel-native" in script
