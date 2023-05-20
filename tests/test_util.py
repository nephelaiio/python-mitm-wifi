import pytest

from mitm_wifi.util import run


def test_run_success():
    assert run("echo hello") == "hello\n"


def test_run_failure():
    with pytest.raises(Exception):
        run("exit 1")
