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

import todo
import base
import unittest

class TestAdd(base.BaseTest):
    num = 11
    def test_add(self):
        self.add_todo(self.num)
        self.assertNumLines(self.num, "Test\s\d+")

    def test_add_predate(self):
        self.add_todo_predate(self.num)
        self.assertNumLines(self.num, "\d{4}-\d{2}-\d{2}.*Test \d+")

    def add_todo(self, n):
        lines = self._test_lines(n)
        for line in lines:
            todo.add_todo(line)

    def add_todo_predate(self, n):
        _pre = todo.CONFIG["PRE_DATE"]
        todo.CONFIG["PRE_DATE"] = True
        self.add_todo(n)

if __name__ == "__main__":
	unittest.main()
