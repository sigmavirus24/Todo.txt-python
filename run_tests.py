#!/usr/bin/env python
# TODO.TXT-CLI-python test script
# Copyright (C) 2011-2012  Jeff Stein
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
import sys
import os
import re
import tests

if __name__ == "__main__":
    if sys.version_info >= (2, 7):
        suite = unittest.defaultTestLoader.discover("tests")
    else:
        names = os.listdir("tests")
        tmp = []
        regex = re.compile("(?!_+)\w+\.py$")
        for f in names:
            if regex.match(f):
                tmp.append(f)
        tmp = [ a[:-3] for a in tmp ]
        names = [ "".join(["tests.", a]) for a in tmp ]
        suite = unittest.defaultTestLoader.loadTestsFromNames(names)

    print("=== Starting unittest suite ===")
    unittest.TextTestRunner(verbosity=2).run(suite)
