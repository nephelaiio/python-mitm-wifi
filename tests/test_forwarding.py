import os
import pytest

from pathlib import Path
from mitm_wifi.forwarding import enable
from mitm_wifi.handlers import (
    get as get_handlers,
    clear as clear_handlers,
    flush as flush_handlers,
)


@pytest.fixture(autouse=True)
def clear():
    clear_handlers()
    yield
    flush_handlers()


def test_forward_file_present(tmp_path: Path):
    procpath = tmp_path / "ip_forward"
    procpath.touch()
    procfile = procpath.absolute().absolute().as_posix()
    enable(procfile)
    assert os.path.exists(procfile)
    assert procpath.read_text() == "1"


def test_forward_file_absent(tmp_path: Path):
    # Create a temporary directory to simulate non-existent file
    procpath = tmp_path / "ip_forward"
    procpath.unlink(missing_ok=True)
    procfile = procpath.absolute().absolute().as_posix()
    with pytest.raises(AssertionError) as e:
        enable(procfile)
    assert str(e.value) == "Your system does not support IP forwarding"


def test_forward_file_noop(tmp_path: Path):
    procpath = tmp_path / "ip_forward"
    procpath.write_text("1")
    procfile = procpath.absolute().absolute().as_posix()
    handlers = get_handlers()
    assert len(handlers) == 0
    enable(procfile)
    handlers = get_handlers()
    assert len(handlers) == 0
    assert os.path.exists(procfile)
    assert procpath.read_text() == "1"
