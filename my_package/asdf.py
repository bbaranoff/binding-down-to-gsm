#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
ASDF

Some other description
"""

from sys import stdout


class ASDF(object):
    """docstring for ASDF"""
    def __init__(self):
        print('ASDF init done')

    def print_hello(self, who: str) -> None:
        """
        Print 'Hello <SOMEONE>' to stdout.

        :param      who:  The who
        :type       who:  str
        """
        stdout.write("Hello {}\n".format(who))
