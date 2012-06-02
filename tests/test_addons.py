# TODO.TXT-CLI-python test script
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
import todo
import base
import unittest

class TestAddons(base.BaseTest):
    def setUp(self):
        super(TestAddons, self).setUp()
        todo.CONFIG['TODO_DIR'] = todo._path('./todo/')
        todo.CONFIG['TODO_ACTIONS_DIR'] = todo._path('./todo/actions')
        if not os.path.exists(todo.CONFIG['TODO_DIR']):
            os.mkdir(todo.CONFIG['TODO_DIR'])
        if not os.path.exists(todo.CONFIG['TODO_ACTIONS_DIR']):
            os.mkdir(todo.CONFIG['TODO_ACTIONS_DIR'])

    def tearDown(self):
        super(TestAddons, self).tearDown()
        if os.path.exists(todo.CONFIG['TODO_ACTIONS_DIR']):
            os.rmdir(todo.CONFIG['TODO_ACTIONS_DIR'])
        if os.path.exists(todo.CONFIG['TODO_DIR']):
            os.rmdir(todo.CONFIG['TODO_DIR'])

    def test_noaddons(self):
        bad_args = ['addp', 'foo']
        good_args = ['add', 'foo']
        self.assertEqual(todo.execute_commands(bad_args), 1)
        self.assertEqual(todo.execute_commands(good_args), 0)

    def test_py_addons(self):
        lines = ['def addp():\n', '\tpass', '\n\n',
            'commands = {"addp": (False, addp)}\n']
        filename = todo.CONFIG['TODO_ACTIONS_DIR'] + '/addp.py'
        if not os.path.exists(filename):
            with open(filename, 'w+') as fd:
                fd.writelines(lines)

        todo.CONFIG['ACTIONS'] = 'addp'
        commands = todo.commands.copy()
        todo.load_actions()

        args = ['addp', '']
        self.assertEqual(todo.execute_commands(args), 0)
        os.unlink(filename)
        os.unlink(filename + 'c')
        todo.CONFIG['ACTIONS'] = ''
        todo.commands = commands.copy()
        self.assertEqual(todo.execute_commands(args), 1)

    def test_sh_addons(self):
        lines = ['#!/bin/bash\n\n', 'A=$((1+1))']
        filename = todo.CONFIG['TODO_ACTIONS_DIR'] + '/addnums'
        if not os.path.exists(filename):
            with open(filename, 'w+') as fd:
                fd.writelines(lines)
        os.chmod(filename, 0700)

        args = ['addnums']
        self.assertEqual(todo.execute_commands(args), 0)
        os.unlink(filename)
        self.assertEqual(todo.execute_commands(args), 1)
