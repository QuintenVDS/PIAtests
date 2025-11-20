import sys
import types
import importlib
import os
from pathlib import Path
import pytest

def test_moderator_can_read_guest_filename_from_logs(monkeypatch, tmp_path):
    #fake ExifTool implementation
    class FakeExif:
        def __init__(self):
            self.running = False

        def start(self):
            self.running = True

        def execute(self, *a, **kw):
            return None

        def terminate(self):
            self.running = False

    fake_mod = types.ModuleType("exiftool")
    fake_mod.ExifTool = FakeExif
    monkeypatch.setitem(sys.modules, "exiftool", fake_mod)
    monkeypatch.setenv("BASE_LOGS", str(tmp_path))

    #inject minimal django.settings
    django_conf = types.ModuleType("django.conf")
    django_conf.settings = types.SimpleNamespace(LOGS_ROOT=str(tmp_path))
    monkeypatch.setitem(sys.modules, "django", types.ModuleType("django"))
    monkeypatch.setitem(sys.modules, "django.conf", django_conf)

    import api.util as util
    importlib.reload(util)

    #guest uploads
    guest_upload = tmp_path / "guest_upload.jpg"
    guest_upload.write_text("fakejpg")
    path = str(guest_upload)
    util.write_metadata(path, {"dummy": "value"}, use_sidecar=False)

    #moderator reads logs
    log = Path(tmp_path) / "ownphotos.log"
    assert log.exists(), "Log file was not created"
    log_content = log.read_text()

    #privacy requirement: moderator must NOT see literal filename
    assert path not in log_content, f"Plaintext filename found in logs (privacy issue). Log content:\n{log_content}"