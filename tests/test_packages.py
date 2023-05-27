import pytest
import importlib

from unittest.mock import call
import mitm_wifi.packages
from mitm_wifi.packages import (
    install,
    configure,
    stop_service,
    restart,
    write_config,
    hostapd_config_iface,
    start_hostapd,
    stop_hostapd,
    iptables_rule_nat,
    iptables_rule_out,
)


def test_install_mock(mocker):
    run = mocker.patch("mitm_wifi.util.run", return_value="success")
    importlib.reload(mitm_wifi.packages)
    install()
    run.assert_called_once_with(f"apt-get install -y wireshark hostapd dnsmasq")


def test_configure_mock(mocker):
    run = mocker.patch("mitm_wifi.util.run", return_value="success")
    importlib.reload(mitm_wifi.packages)
    configure()
    calls = [
        call("systemctl unmask hostapd"),
        call("systemctl disable hostapd"),
        call("systemctl unmask dnsmasq"),
        call("systemctl disable dnsmasq"),
    ]
    run.assert_has_calls(calls)


def test_stop_service_mock(mocker, tmp_path):
    config_a = f"{tmp_path}/test_a.conf"
    config_b = f"{tmp_path}/test_b.conf"
    service = "hostapd"
    iface = "iface"
    run = mocker.patch("mitm_wifi.util.run", return_value="success")
    importlib.reload(mitm_wifi.packages)
    stop_service(service, iface, [config_a, config_b])
    calls = [
        call(f"systemctl stop {service}@{iface}"),
        call(f"rm -f {config_a}"),
        call(f"rm -f {config_b}"),
    ]
    run.assert_has_calls(calls)


def test_restart_mock(mocker):
    run = mocker.patch("mitm_wifi.util.run", return_value="success")
    importlib.reload(mitm_wifi.packages)
    restart("hostapd")
    run.assert_called_once_with(f"systemctl restart hostapd")


def test_write_config(tmp_path):
    conf = f"{tmp_path}/test.conf"
    write_config(conf, "test")
    with open(conf, "r") as f:
        assert f.read() == "test"


def test_hostapd_config_iface():
    iface = "test"
    config_file = hostapd_config_iface(iface)
    assert config_file == f"/etc/hostapd/{iface}.conf"


def test_start_hostapd():
    pass


def test_stop_hostapd_mock(mocker):
    service = "hostapd"
    iface = "test"
    run = mocker.patch("mitm_wifi.util.run", return_value="success")
    importlib.reload(mitm_wifi.packages)
    stop_hostapd(iface)
    calls = [
        call(f"systemctl stop {service}@{iface}"),
        call(f"rm -f /etc/hostapd/{iface}.conf"),
    ]
    run.assert_has_calls(calls)


def test_iptables_rule_nat():
    iface = "test"
    rule_create = f"iptables -t nat -A POSTROUTING -o {iface} -j MASQUERADE"
    rule_delete = f"iptables -t nat -D POSTROUTING -o {iface} -j MASQUERADE"
    assert iptables_rule_nat(iface, True) == rule_create
    assert iptables_rule_nat(iface, False) == rule_delete


def test_iptables_rule_out():
    iface_in = "test"
    iface_out = "out"
    rule_create = f"iptables -A FORWARD -i {iface_in} -o {iface_out} -j ACCEPT"
    rule_delete = f"iptables -D FORWARD -i {iface_in} -o {iface_out} -j ACCEPT"
    assert iptables_rule_out(iface_in, iface_out, True) == rule_create
    assert iptables_rule_out(iface_in, iface_out, False) == rule_delete
