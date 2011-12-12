# TODO.TXT-CLI-python test script
# Copyright (C) 2011  Sigmavirus24, Jeff Stein
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
# TLDR: This is licensed under the GPLv3. See LICENSE for more details.

# Common functions for test_*_todo.py
import re
import sys
import unittest
from os import unlink

import todo

todotxt = todo.CONFIG["TODO_FILE"] = "test_todo.txt"
donetxt = todo.CONFIG["DONE_FILE"] = "test_done.txt"

class BaseTest(unittest.TestCase):
    def setUp(self):
        todo.CONFIG["PRE_DATE"] = False
        sys.stdout = open("/dev/null", "w")
        open(todotxt, "w+").close()
        open(donetxt, "w+").close()

    def tearDown(self):
        sys.stdout = sys.__stdout__
        unlink(todotxt)
        unlink(donetxt)

    def count_matches(self, regexp=None):
        count = 0
        for line in todo.iter_todos():
            if regexp == None or re.match(regexp, line):
                count += 1
        return count

    def _test_lines(self, num):
        return ["Test {0}".format(i) for i in range(0, num)]

    def assertNumLines(self, exp, regexp=None):
        c = self.count_matches(regexp)
        self.assertEqual(exp, c)
