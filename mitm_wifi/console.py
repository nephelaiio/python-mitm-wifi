#!/usr/bin/env python3

import os


def is_kitty():
    kitty_window_id = os.getenv("KITTY_WINDOW_ID")
    return kitty_window_id is not None
