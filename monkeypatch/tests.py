#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


import unittest
from .utils import *


#class TestExample(unittest.TestCase):
#    def test(self):
#        pass


# also test the functions in utils.py
# since django doesn't find those
__test__ = {
    "monkey_patch":    monkey_patch,
    "sanity_check":    sanity_check,
    "apply_patch":     apply_patch,
    "fields":          fields,
    "conflicts":       conflicts,
    "non_magic_attrs": non_magic_attrs,
    "is_magic":        is_magic
}
