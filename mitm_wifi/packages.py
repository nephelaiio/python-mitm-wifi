#!/usr/bin/env python3

from .util import run
from .handlers import add as add_handler
from .logger import logger

from netaddr import IPNetwork  # type: ignore
from textwrap import dedent
from pyroute2 import IPDB  # type: ignore

services: list[str] = ["hostapd", "dnsmasq"]
packages: list[str] = ["wireshark"]


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


def hostapd_config_iface(iface: str):
    return f"/etc/hostapd/{iface}.conf"


def start_hostapd(iface: str, ssid: str = "mitm", password: str = "12345678"):
    service_name = "hostapd"
    logger.info(f"starting {service_name} for interface {iface}")
    write_config(
        hostapd_config_iface(iface),
        f"""
        interface={iface}
        driver=nl80211
        ssid={ssid}
        hw_mode=g
        channel=6
        macaddr_acl=0
        auth_algs=1
        ignore_broadcast_ssid=0
        wpa=2
        wpa_passphrase={password}
        wpa_key_mgmt=WPA-PSK
        wpa_pairwise=TKIP
        rsn_pairwise=CCMP
        """,
    )
    run(f"systemctl start {service_name}@{iface}")
    print(f"Started hostapd, interface={iface}, ssid={ssid}, password={password}")
    add_handler(lambda: stop_hostapd(iface))


def stop_hostapd(iface: str):
    service_name = "hostapd"
    try:
        stop_service(service_name, iface, [hostapd_config_iface(iface)])
    except:  # noqa: E722
        logger.debug(f"failed to stop {service_name} for interface {iface}")


def iptables_rule_nat(iface_out: str, create: bool = True):
    action = "A" if create else "D"
    return f"iptables -t nat -{action} POSTROUTING -o {iface_out} -j MASQUERADE"


def iptables_rule_out(iface_in: str, iface_out: str, create: bool = True):
    action = "A" if create else "D"
    return f"iptables -{action} FORWARD -i {iface_in} -o {iface_out} -j ACCEPT"


def iptables_rule_in(iface_in: str, iface_out: str, create: bool = True):
    action = "A" if create else "D"
    return f"iptables -{action} FORWARD -i {iface_out} -o {iface_in} -j ACCEPT"


def iptables_rule_dhcp(iface_in: str, create: bool = True):
    action = "I" if create else "D"
    return f"iptables -{action} INPUT -p udp -i {iface_in} --dport 67 -j ACCEPT"


def dnsmasq_config_default(iface: str):
    return f"/etc/default/dnsmasq.{iface}"


def dnsmasq_config_iface(iface: str):
    return f"/etc/dnsmasq.{iface}.conf"


def iface_default():
    ip = IPDB()
    iface_out_index = ip.routes["default"]["oif"]
    iface_out_name = ip.interfaces[iface_out_index]["ifname"]
    return iface_out_name


def start_dnsmasq(iface: str, ipaddr: str):
    iface_in = iface
    iface_out = iface_default()
    service_name = "dnsmasq"
    try:
        network = IPNetwork(ipaddr)
        gateway = network[1]
        iprange = f"{network[2]},{network[-2]}"
        logger.info(f"starting {service_name} for interface {iface_in}")
        write_config(
            dnsmasq_config_default(iface_in),
            f"""
            DNSMASQ_OPTS="--conf-file=/etc/dnsmasq.{iface_in}.conf --bind-interfaces"
            """,
        )
        write_config(
            dnsmasq_config_iface(iface_in),
            f"""
            interface={iface_in}
            dhcp-range={iprange},12h
            dhcp-option=3,{gateway}
            dhcp-option=6,{gateway}
            log-facility=/var/log/dnsmasq.log
            log-async
            log-queries
            log-dhcp
            """,
        )
        run(f"ip address add {gateway}/24 dev {iface_in}")
    except:  # noqa: E722
        logger.error(f"invalid ip address: {ipaddr}")
        exit(1)
    run(f"systemctl start {service_name}@{iface_in}")
    run(iptables_rule_nat(iface_out))
    run(iptables_rule_out(iface_in, iface_out))
    run(iptables_rule_in(iface_in, iface_out))
    run(iptables_rule_dhcp(iface_in))
    print(f"Started dnsmasq, interface={iface}, address={ipaddr}, dhcp={iprange}")
    add_handler(lambda: stop_dnsmasq(iface_in))


def stop_dnsmasq(iface_in: str):
    iface_out = iface_default()
    service_name = "dnsmasq"
    try:
        stop_service(
            service_name,
            iface_in,
            [dnsmasq_config_default(iface_in), dnsmasq_config_iface(iface_in)],
        )
    except:  # noqa: E722
        logger.debug(f"failed to stop {service_name} for interface {iface_in}")
    try:
        run(iptables_rule_nat(iface_out, create=False))
        run(iptables_rule_out(iface_in, iface_out, create=False))
        run(iptables_rule_in(iface_in, iface_out, create=False))
        run(iptables_rule_dhcp(iface_in, create=False))
    except:  # noqa: E722
        logger.debug(f"failed to configure iptable rules for interface {iface_in}")


def stop_service(name: str, iface: str, config_files: list[str]):
    logger.info(f"stopping service {name} for interface {iface}")
    run(f"systemctl stop {name}@{iface}")
    for config in config_files:
        run(f"rm -f {config}")
