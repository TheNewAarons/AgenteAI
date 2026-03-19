import pytest
import os
from app.tools.security import is_safe_path
from app.tools.implementations import create_file, run_command

def test_is_safe_path():
    # Asumiendo que el entorno de test está en el repo
    assert is_safe_path("app.py") is True
    assert is_safe_path("/etc/passwd") is False
    assert is_safe_path("../../../etc/passwd") is False

def test_create_file_security():
    result = create_file("/tmp/hacked.txt", "content")
    assert "ERROR: Acceso denegado" in result

def test_run_command_security():
    result = run_command("rm -rf /")
    assert "ERROR: Comando bloqueado" in result
    
    result = run_command("sudo ls")
    assert "ERROR: Comando bloqueado" in result
