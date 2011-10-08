#!/usr/bin/env python
"""
TODO.TXT-CLI-python profiler.py script (translates profiled information to
plain-text)
Copyright (C) 2011  Sigmavirus24

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

TLDR: This is licensed under the GPLv3. See LICENSE for more details.
"""

import pstats
from os import system

system('python -m cProfile -o todo_py_profile todo.py')

p = pstats.Stats('todo_py_profile')
p.strip_dirs().sort_stats('cumulative').print_stats(25)
