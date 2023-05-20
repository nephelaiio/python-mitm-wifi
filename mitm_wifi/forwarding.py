#!/usr/bin/env python3

import os
from .handlers import add as add_handler

enabled = "1"


def configure(procfile: str, value: str):
    with open(procfile, "w") as file:
        file.write(value)


def enable(procfile="/proc/sys/net/ipv4/ip_forward"):
    assert os.path.exists(procfile), "Your system does not support IP forwarding"
    with open(procfile) as forward:
        current_value = forward.read()
        if current_value != enabled:
            configure(procfile, enabled)
            add_handler(lambda: configure(procfile, current_value))
