#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
QWERTZ

Some description
"""

from random import sample
from typing import List


class QWERTZ(object):
    """docstring for QWERTZ"""
    def __init__(self, arg):
        print('QWERTZ init with {}'.format(arg))

    def print_okay(self):
        """Print 'okay'"""
        print("okay")

    def get_list_of_int(self, how_long: int = 5) -> List[int]:
        """
        Get a list of integers.

        :param      how_long:  How many integers, default 5
        :type       how_long:  int

        :returns:   The list of integers.
        :rtype:     List[int]
        """
        random_int_list = sample(range(0, 100), how_long)

        print('Generated random int list of length {}'.
              format(len(random_int_list)))

        return random_int_list
