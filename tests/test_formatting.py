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
		#lines = todo.format_lines()
		#self.assert_formatted(lines)


	def test_color_only(self):
		self.addm_todo_with_pri(self.num)
		lines = todo.format_lines(True)
		self.assert_color_only(lines)


	def test_formatted_remove_pri(self):
		self.addm_todo_with_pri(self.num)
		#self.assertNumLines(self.num, "Test \d+")


	def addm_todo_no_pri(self, n):
		todo.addm_todo("\n".join(self._test_lines_no_pri(n)))


	def addm_todo_with_pri(self, n):
		todo.addm_todo("\n".join(self._test_lines_pri(n)))


	def assert_formatted(self, lines):
		# This needs to check that the string starts with the proper code (i.e.
		# todo.TERM_COLORS["red"] and terminates with
		# todo.TERM_COLORS["default"]\n for the proper colors based on priority
		# also checks that the return value is a dictionary.
		pass


	def assert_color_only(self, lines):
		# This needs to check that the return value is only a list of strings
		# colored by priority.
		self.assertTrue(isinstance(lines, list))
		# Not finished, just testing the above statement.


	def assert_plain(self):
		# This needs to check that only the todo.TERM_COLORS["default"] color
		# has been applied to the beginning and end of the string. Also needs to
		# check that the return value is a dictionary
		pass


	def assert_nopri(self):
		# This should check to make sure the function removes the priorities
		# from the beginning of the lines (formatted or otherwise).
		pass


	def assert_dated(self):
		# Should check that the formatting is in date form and properly sorted.
		pass


	def assert_context(self):
		# Should check that the return value is sorted by context.
		pass

if __name__ == "__main__":
	unittest.main()
