#!/usr/bin/env python3
import subprocess

from .logger import logger


def run(cmd) -> str:
    logger.info(f"running command: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True)
    if result.returncode != 0:
        raise (Exception(result.stderr.decode("utf-8")))
    else:
        return result.stdout.decode("utf-8")
