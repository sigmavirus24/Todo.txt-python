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

import unittest
import base
import todo

class AppendTest(base.BaseTest):

    def test_append(self):
        todo.addm_todo("\n".join(self._test_lines_no_pri(self.num)))

        for i in range(1, self.num + 1):
            todo.append_todo([str(i), "testing", "append"])

        self.assertNumLines(self.num, "Test\s\d+\stesting\sappend")


if __name__ == "__main__":
    unittest.main()
