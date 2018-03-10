#!/usr/bin/env python3
import logging
import coloredlogs
from support import Support


if __name__ == '__main__':
    coloredlogs.install(fmt='%(asctime)s %(message)s', datefmt='%H:%M:%S')
    try:
        e = Support('../config/support_mini.json')
        e.run()
    finally:
        e.stop()
