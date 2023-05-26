---
# Python WiFi Network Monitor

[![Test](https://github.com/nephelaiio/python-mitm-wifi/actions/workflows/test.yml/badge.svg)](https://github.com/nephelaiio/python-mitm-wifi/actions/workflows/test.yml) [![Lint](https://github.com/nephelaiio/python-mitm-wifi/actions/workflows/lint.yml/badge.svg)](https://github.com/nephelaiio/python-mitm-wifi/actions/workflows/lint.yml)

This Python project is a WiFi network management tool which monitors usb devices and performs basic configuration through hostapd and dnsmasq services that allows to set up the host device as a relay ap for traffic monitoring purposes

## Features
* Automatically configure network adapters via hostapd and dnsmasq.
* Automatically start network capture on adapter using [Wireshark](https://www.wireshark.org/)

## Requirements
* python 3.9+
* [pipx](https://www.wireshark.org/)

## Usage
Run the main script with root privileges, providing the desired WiFi network SSID, subnet, and password as optional arguments:

```bash
sudo pipx run --spec git+https://github.com/nephelaiio/python-mitm-wifi.git mitm
```

## Options
* `--ssid` : WiFi network SSID (default: "mitm")
* `--network` : WiFi network subnet (default: "192.168.127.0/24")
* `--password` : WiFi network password (required)
* `-v` or `--verbose` : Increase verbosity. Use twice (`-vv`) for more verbosity.

## Environment variables
* `MITM_SSID` : Configure `--ssid` option
* `MITM_NETWORK` : Configure `--network` option
* `MITM_PASSWORD` : Configure `--password` option

## License
This project is licensed under the terms of the MIT license.
