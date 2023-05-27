#!/usr/bin/env python3

from mitm_wifi.handlers import add, get, clear, flush

hi = lambda: "hi"
there = lambda: "there"


def test_add():
    add(hi)
    add(there)
    assert len(get()) == 2
    assert flush() == ["hi", "there"]


def test_clear():
    add(hi)
    add(there)
    assert len(get()) == 2
    clear()
    assert len(get()) == 0


def test_flush():
    add(there)
    add(hi)
    assert flush() == ["there", "hi"]
    assert len(get()) == 0


def test_get():
    add(hi)
    assert len(get()) == 1
    add(get)
    assert len(get()) == 2
    clear()
    assert len(get()) == 0
