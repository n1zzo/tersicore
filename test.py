#!/usr/bin/env python

import config
import signal

def _sighup_handler(signum):
    config.reload()

signal.signal(signal.SIGHUP, _sighup_handler)
