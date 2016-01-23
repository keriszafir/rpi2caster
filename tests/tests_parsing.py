"""Tests for parsing module"""
from unittest import TestCase
from rpi2caster import parsing

class TestParsing(TestCase):
    def test_file_read(self):
        file = parsing.read_file('tests/r1')
        self.assertNotEqual(file, False)
