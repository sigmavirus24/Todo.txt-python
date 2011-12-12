# TODO.TXT-CLI-python test script
# Copyright (C) 2011  Sigmavirus24
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
import test

def addm_todo(n, print_count=True):
	todo.addm_todo("\n".join(test.test_lines(n)))

	count = test.count_matches("Test\s\d+")

	if print_count:
		test._print("vanilla addm_todo()", count, n)


def addm_todo_predate(n):
	_pre = todo.CONFIG["PRE_DATE"]
	todo.CONFIG["PRE_DATE"] = True
	addm_todo(n, False)

	count = test.count_matches("\d{4}-\d{2}-\d{2}.*Test \d+")

	test._print("predate addm_todo()", count, n)


def main():
	test.redirect_stdout()
	n = 11
	test.create_truncate()
	addm_todo(n)
	test.create_truncate()
	addm_todo_predate(n)

if __name__ == "__main__":
	main()
	test.cleanup()
