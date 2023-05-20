#!/usr/bin/env python3
from typing import Callable, List

handlers: List[Callable[[], None]] = []


def add(handler):
    handlers.append(handler)


def clear():
    handlers.clear()


def flush():
    return [handler() for handler in handlers]


def get():
    return handlers
