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
import re

import todo
import base

class TestFormat(base.BaseTest):

    def _generate_re_dictionary(self, with_lookbehind=False):
        rd = {}
        esc = re.escape
        colors = todo.TERM_COLORS
        default = esc(colors["default"])
        concat = todo.concat

        if not with_lookbehind:
            for p in todo.PRIORITIES[:-1]:
                color = todo.CONFIG["PRI_{0}".format(p)]
                rd[p] = re.compile(concat([esc(colors[color]), 
                    "\d+ (\({0}\)) .*".format(p), default]))
        else:
            for p in todo.PRIORITIES[:-1]:
                color = todo.CONFIG["PRI_{0}".format(p)]
                rd[p] = re.compile(concat([esc(colors[color]), 
                    "\d+ (?!\({0}\)).*".format(p), default]))
                # If there is a priority listed ([A-X]), the match will fail on
                # lines without priority

        rd["X"] = re.compile(concat([default, "\d+ .*", default]))
        return rd


    def setUp(self):
        i = 0
        for k in todo.TERM_COLORS.keys():
            if k not in ("default", "reverse", "bold"):
                todo.CONFIG["PRI_{0}".format(todo.PRIORITIES[i])] = k
                i += 1
        for k in todo.PRIORITIES[i:]:
            todo.CONFIG["PRI_{0}".format(k)] = "default"
        super(TestFormat, self).setUp()


    def test_formatted(self):
        self.addm_todo_with_pri(self.num)
        lines = todo.format_lines()
        self.assert_formatted(lines)


    def test_color_only(self):
        self.addm_todo_with_pri(self.num)
        lines = todo.format_lines(True)
        self.assert_color_only(lines)


    def test_formatted_remove_pri(self):
        todo.CONFIG["NO_PRI"] = True
        self.addm_todo_with_pri(self.num)
        lines = todo.format_lines()
        self.assert_nopri(lines)


    def test_plain(self):
        todo.CONFIG["PLAIN"] = True
        self.addm_todo_with_pri(self.num)
        lines = todo.format_lines()
        self.assert_plain(lines, dict)
        lines = todo.format_lines(True)
        self.assert_plain(lines, list)


    def addm_todo_no_pri(self, n):
        todo.addm_todo("\n".join(self._test_lines_no_pri(n)))


    def addm_todo_with_pri(self, n):
        todo.addm_todo("\n".join(self._test_lines_pri(n)))


    def assert_formatted(self, lines):
        # This needs to check that the string starts with the proper code (i.e.
        # todo.TERM_COLORS["red"] and terminates with
        # todo.TERM_COLORS["default"]\n for the proper colors based on priority
        # also checks that the return value is a dictionary.
        self.assertIsInstance(lines, dict)

        keys = list(lines.keys())
        keys.sort()
        self.assertEqual(todo.concat(keys), todo.PRIORITIES)

        color_dict = self._generate_re_dictionary()

        for k, v in lines.items():
            for line in v:
                self.assertIsNotNone(color_dict[k].match(line),
                        todo.concat([k, line], " "))


    def assert_color_only(self, lines):
        # This needs to check that the return value is only a list of strings
        # colored by priority.
        self.assertIsInstance(lines, list)

        re_dict = self._generate_re_dictionary()
        priority = re.compile(".*\(([A-X])\).*")

        for line in lines:
            line = line.strip()
            p = priority.sub("\g<1>", line)
            self.assertIsNotNone(re_dict[p].match(line), todo.concat([p, line], 
                " "))


    def assert_plain(self, lines, cls):
        # This needs to check that only the todo.TERM_COLORS["default"] color
        # has been applied to the beginning and end of the string. Also needs to
        # check that the return value is a dictionary
        #pass
        self.assertIsInstance(lines, cls)
        reg = re.compile("\d+\s(\([A-X]\))?.*")

        if cls == list:
            for line in lines:
                self.assertIsNotNone(reg.match(line))
        elif cls == dict:
            for val in lines.values():
                for line in val:
                    self.assertIsNotNone(reg.match(line))


    def assert_nopri(self, lines):
        # This should check to make sure the function removes the priorities
        # from the beginning of the lines (formatted or otherwise).
        self.assertIsInstance(lines, dict)

        keys = list(lines.keys())
        keys.sort()
        self.assertEqual(todo.concat(keys), todo.PRIORITIES)

        color_dict = self._generate_re_dictionary(True)

        for k, v in lines.items():
            for line in v:
                self.assertIsNotNone(color_dict[k].match(line), todo.concat([k,
                    line], " "))


if __name__ == "__main__":
    unittest.main()
