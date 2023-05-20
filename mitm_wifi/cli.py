#!/usr/bin/env python

import os
import sys
import pyudev
import typer

from typing_extensions import Annotated

from .packages import install, configure, start_hostapd, start_dnsmasq
from .handlers import flush as flush_handlers
from .util import run
from .logger import logger


def configure_device(action, device, network, ssid, password):
    if device.device_type == "wlan":
        if action == "move":
            iface = device["INTERFACE"]
            logger.info(f"{action} {iface}")
            start_hostapd(iface, ssid, password)
            start_dnsmasq(iface, network)
        elif action == "remove":
            iface = device["INTERFACE"]
            logger.info(f"{action} {iface}")
            flush_handlers()
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


def main(
    ssid: Annotated[str, typer.Option("--ssid", help="WiFi network SSID")] = "mitm",
    network: Annotated[
        str, typer.Option("--network", help="WiFi network subnet")
    ] = "192.168.127.0/24",
    password: Annotated[
        str, typer.Option("--password", help="WiFi network password")
    ] = "12345678",
    verbose: Annotated[
        int, typer.Option("--verbose", "-v", help="Increase verbosity", count=True)
    ] = False,
):
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
    print("Press Enter to quit ...")
    input()
    observer.stop()
    flush_handlers()


def exec():
    typer.run(main)


if __name__ == "__main__":
    typer()
