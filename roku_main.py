#!/usr/bin/env python3
"""
Polyglot v2 node server experimental Roku Media Player control.
Copyright (C) 2019 Robert Paauwe
"""
import polyinterface
import sys
from nodes import roku

LOGGER = polyinterface.LOGGER

if __name__ == "__main__":
    try:
        polyglot = polyinterface.Interface('Roku1')
        polyglot.start()
        control = roku.Controller(polyglot)
        control.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        

