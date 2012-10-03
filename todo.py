#!/usr/bin/env python

# TODO.TXT-CLI-python
# Copyright (C) 2011-2012  Sigmavirus24
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

import os
# import re
import sys
# from optparse import OptionParser
# from datetime import datetime, date
from todotxt import TodoDotTxt

version = "development"
revision = "$Id$"

try:
    import readline
except ImportError:
    # This isn't crucial to the execution of the script.
    # But it is a nice feature to have. Sucks to be an OSX user.
    pass

try:
    # Python 3 moved the built-in intern() to sys.intern()
    intern = sys.intern
except AttributeError:
    pass

try:
    input = raw_input
except NameError:
    # Python 3 renamed raw_input to input
    pass

try:
    from string import uppercase
except ImportError:
    # Python 3 again
    from string import ascii_uppercase as uppercase

if os.name == "nt":
    try:
        from colorama import init
        init()
    except Exception:
        pass
    # colorama provides ANSI -> win32 color support
    # If they don't have it, no worries.
priorities = uppercase[:24]

# concat() is necessary long before the grouping of function declarations
concat = lambda str_list, sep='': sep.join([str(i) for i in str_list])
_path = lambda p: os.path.abspath(os.path.expanduser(p))
_pathc = lambda plist: _path(concat(plist))

term_colors = {
        "black": "\033[0;30m", "red": "\033[0;31m",
        "green": "\033[0;32m", "brown": "\033[0;33m",
        "blue": "\033[0;34m", "purple": "\033[0;35m",
        "cyan": "\033[0;36m", "light grey": "\033[0;37m",
        "dark grey": "\033[1;30m", "light red": "\033[1;31m",
        "light green": "\033[1;32m", "yellow": "\033[1;33m",
        "light blue": "\033[1;34m", "light purple": "\033[1;35m",
        "light cyan": "\033[1;36m", "white": "\033[1;37m",
        "default": "\033[0m", "reverse": "\033[7m",
        "bold": "\033[1m",
        }

todo_dir = _path("~/.todo")
config = {
        "TODO_DIR": todo_dir,
        "TODOTXT_DEFAULT_ACTION": "list",
        "TODOTXT_CFG_FILE": _pathc([todo_dir, "/config"]),
        "TODO_FILE": _pathc([todo_dir, "/todo.txt"]),
        "DONE_FILE": _pathc([todo_dir, "/done.txt"]),
        "TMP_FILE": "",
        "REPORT_FILE": "",
        "USE_GIT": False,
        "PLAIN": False,
        "NO_PRI": False,
        "PRE_DATE": False,
        "INVERT": False,
        "HIDE_PROJ": False,
        "HIDE_CONT": False,
        "HIDE_DATE": False,
        "LEGACY": False,
        "ACTIONS": None,
        "TERM_COLORS": term_colors,
        "PRIORITIES": priorities,
        "VERSION": version,
        "REVISION": revision
        }

DoToDo = TodoDotTxt(config)

for p in priorities:
    config["PRI_{0}".format(p)] = "default"
del(p, todo_dir)


### Helper Functions


if __name__ == "__main__":
    config["TODO_PY"] = sys.argv[0]
    opts = DoToDo.opt_setup()

    valid, args = opts.parse_args()

    DoToDo.get_config(valid.config, valid.todo_dir)

    if config["USE_GIT"]:
        DoToDo.update_commands(
                [("push", 	(False, DoToDo._git_push)),
                ("pull", 	(False, DoToDo._git_pull)),
                ("status", 	(False, DoToDo._git_status)),
                ("log", 	(False, DoToDo._git_log))]
                )

    if config["ACTIONS"]:
        DoToDo.load_actions()

    if not len(args) > 0:
        args.append(config["TODOTXT_DEFAULT_ACTION"])

    sys.exit(DoToDo.execute_commands(args))
