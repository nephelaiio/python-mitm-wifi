#!/usr/bin/env python

import os
import time
import subprocess
import click
import pyudev  # type: ignore

from .packages import (
    install,
    configure,
    start_hostapd,
    start_dnsmasq,
    stop_hostapd,
    stop_dnsmasq,
)
from .handlers import flush as flush_handlers
from .logger import logger

connected = False
finished = False


def configure_device(action, device, network, ssid, password):
    global finished
    global connected
    if device.device_type == "wlan":
        if action == "move":
            iface = device["INTERFACE"]
            logger.info(f"{action} {iface}")
            start_hostapd(iface, ssid, password)
            start_dnsmasq(iface, network)
            subprocess.Popen(
                ["wireshark", "-i", iface, "-k"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            connected = True
        elif action == "remove":
            iface = device["INTERFACE"]
            logger.info(f"{action} {iface}")
            if connected:
                finished = True
            else:
                stop_hostapd(iface)
                stop_dnsmasq(iface)
        else:
            logger.debug(f"Unknown action: {action}")
    else:
        logger.debug(f"Unknown device: {device}, action: {action}")


def monitor(network: str, ssid: str, password: str):
    context = pyudev.Context()
    listener = pyudev.Monitor.from_netlink(context)
    observer = pyudev.MonitorObserver(
        listener,
        lambda action, device: configure_device(
            action, device, network, ssid, password
        ),
    )
    observer.start()
    return observer


@click.command()
@click.option(
    "--ssid",
    help="WiFi network SSID",
    envvar="MITM_SSID",
    default="mitm",
    show_default=True,
    type=click.STRING,
)
@click.option(
    "--network",
    help="WiFi network subnet",
    envvar="MITM_NETWORK",
    default="192.168.127.0/24",
    type=click.STRING,
)
@click.option(
    "--password",
    help="WiFi network password",
    envvar="MITM_PASSWORD",
    default="12345678",
    show_default=False,
    type=click.STRING,
)
@click.option(
    "--verbose",
    "-v",
    count=True,
    help="Increase verbosity (specify multiple times for more)",
    type=click.INT,
)
def main(ssid: str, network: str, password: str, verbose: int):
    if verbose == 1:
        logger.setLevel("INFO")
    elif verbose > 1:
        logger.setLevel("DEBUG")
    logger.info("checking runtime privileges ...")
    if os.geteuid() != 0:
        print("Script requires root privileges, aborting")
        exit(1)
    install()
    configure()
    observer = monitor(network, ssid, password)
    print("Insert WiFi adapter to configure ...")
    while not finished:
        time.sleep(1)
    observer.stop()
    flush_handlers()


if __name__ == "__main__":
    main()
