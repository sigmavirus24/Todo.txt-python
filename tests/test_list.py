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

class TestList(base.BaseTest):
	max = 31

	def test_not_dated(self):
		#todo.CONFIG["PRE_DATE"] = True
		if self.num > self.max:
			self.num = self.max
		todo.addm_todo("\n".join(self._test_lines_date(self.num)))
		colored, sorted = todo._list_("date", "#\{(\d{4})-(\d{1,2})-(\d{1,2})\}")
		self.assert_not_equal(colored, sorted)
		self.assert_dated(colored, sorted)


	def assert_dated(self, colored, lines):
		# Should check that the formatting is in date form and properly sorted.
		self.assertIsInstance(lines, list)
		datere = re.compile("\d{4}-\d{1,2}-\d{1,2}")
		count = 0
		for line in lines:
			if datere.match(line):
				count += 1
		self.assertEqual(count, len(colored))


	def assert_not_equal(self, colored, sorted):
		self.assertNotEqual(len(colored), len(sorted))


	def assert_context(self):
		# Should check that the return value is sorted by context.
		pass


if __name__ == "__main__":
	unittest.main()


# vim:set noet:
