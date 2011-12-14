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

import todo
import base

class TestFormat(base.BaseTest):

	def setUp(self):
		i = 0
		for k in todo.TERM_COLORS.keys():
			if k not in ("default", "reverse", "bold"):
				todo.CONFIG["PRI_{0}".format(todo.PRIORITIES[i])] = k
				i += 1
		for k in todo.PRIORITIES[i:]:
			todo.CONFIG["PRI_{0}".format(k)] = "default"
		super(TestFormat,self).setUp()

	def test_formatted(self):
		self.addm_todo_no_pri(self.num)
		#self.assertNumLines(self.num, "Test\s\d+")

	def test_formatted_remove_pri(self):
		self.addm_todo_with_pri(self.num)
		#self.assertNumLines(self.num, "Test \d+")

	def addm_todo_no_pri(self, n):
		todo.addm_todo("\n".join(self._test_lines_no_pri(n)))

	def addm_todo_with_pri(self, n):
		todo.addm_todo("\n".join(self._test_lines_pri(n)))

	def assert_formatted(self):
		# This needs to check that the string starts with the proper code (i.e.
		# todo.TERM_COLORS["red"] and terminates with
		# todo.TERM_COLORS["default"]\n for the proper colors based on priority
		pass

	def assert_plain(self):
		# This needs to check that only the todo.TERM_COLORS["default"] color
		# has been applied to the beginning and end of the string
		pass

	def assert_nopri(self):
		# This should check to make sure the function removes the priorities
		# from the beginning of the lines (formatted or otherwise).
		pass

if __name__ == "__main__":
	unittest.main()
