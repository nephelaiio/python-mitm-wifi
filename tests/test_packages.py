import pytest
import importlib

from unittest.mock import call
import mitm_wifi.packages


def test_install_mock(mocker):
    run = mocker.patch("mitm_wifi.util.run", return_value="success")
    importlib.reload(mitm_wifi.packages)
    mitm_wifi.packages.install()
    run.assert_called_once_with(f"apt-get install -y hostapd dnsmasq")


def test_configure_mock(mocker):
    run = mocker.patch("mitm_wifi.util.run", return_value="success")
    importlib.reload(mitm_wifi.packages)
    mitm_wifi.packages.configure()
    calls = [
        call("systemctl unmask hostapd"),
        call("systemctl disable hostapd"),
        call("systemctl unmask dnsmasq"),
        call("systemctl disable dnsmasq"),
    ]
    run.assert_has_calls(calls)


def test_restart_mock(mocker):
    run = mocker.patch("mitm_wifi.util.run", return_value="success")
    importlib.reload(mitm_wifi.packages)
    mitm_wifi.packages.restart("hostapd")
    run.assert_called_once_with(f"systemctl restart hostapd")
