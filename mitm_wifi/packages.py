#!/usr/bin/env python3

from .util import run
from .handlers import add as add_handler
from .logger import logger

from netaddr import IPNetwork
from textwrap import dedent

services: list[str] = ["hostapd", "dnsmasq"]
packages: list[str] = []


def install(packages: list[str] = packages + services):
    logger.info("installing packages ...")
    run(f"apt-get install -y {' '.join(packages)}")


def configure(services: list[str] = services):
    logger.info("configuring services ...")
    for service in services:
        run(f"systemctl unmask {service}")
        run(f"systemctl disable {service}")


def restart(service: str):
    run(f"systemctl restart {service}")


def write_config(filename: str, content: str):
    content = dedent(content).strip("\n")
    with open(filename, "w") as f:
        f.write(content)


def start_hostapd(iface: str, ssid: str = "mitm", password: str = "12345678"):
    service_name = "hostapd"
    service_config = f"/etc/hostapd/{iface}.conf"
    logger.info(f"starting {service_name} for interface {iface}")
    write_config(
        service_config,
        f"""
        interface={iface}
        driver=nl80211
        country_code=CR
        ssid={ssid}
        hw_mode=g
        wpa=2
        wpa_passphrase={password}
        wpa_key_mgmt=WPA-PSK
        channel=6
        macaddr_acl=0
        auth_algs=1
        """,
    )
    run(f"systemctl start {service_name}@{iface}")
    add_handler(lambda: stop_service(service_name, iface, [service_config]))


def start_dnsmasq(iface: str, ipaddr: str):
    service_name = "dnsmasq"
    service_default = f"/etc/default/dnsmasq.{iface}"
    service_config = f"/etc/dnsmasq.{iface}.conf"
    try:
        network = IPNetwork(ipaddr)
        gateway = network[1]
        iprange = f"{network[2]},{network[-2]}"
        logger.info(f"starting {service_name} for interface {iface}")
        write_config(
            service_default,
            f"""
            DNSMASQ_OPTS="--conf-file=/etc/dnsmasq.{iface}.conf --bind-interfaces"
            """,
        )
        write_config(
            service_config,
            f"""
            interface={iface}
            dhcp-range={iprange},12h
            dhcp-option=3,{gateway}
            dhcp-option=6,{gateway}
            log-facility=/var/log/dnsmasq.log
            log-async
            log-queries
            log-dhcp
            """,
        )
        run(f"ip address add {gateway}/24 dev {iface}")
    except:
        logger.error(f"invalid ip address: {ipaddr}")
        exit(1)
    run(f"systemctl start {service_name}@{iface}")
    run(f"iptables -t nat -A POSTROUTING -o {iface} -j MASQUERADE")
    add_handler(
        lambda: stop_service(service_name, iface, [service_default, service_config])
    )
    add_handler(lambda: run(f"iptables -t nat -D POSTROUTING -o {iface} -j MASQUERADE"))


def stop_service(name: str, iface: str, config_files: list[str]):
    logger.info(f"stopping service {name} for interface {iface}")
    run(f"systemctl stop {name}@{iface}")
    for config in config_files:
        run(f"rm -f {config}")
