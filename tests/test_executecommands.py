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

import todo
import base
from functools import partial


class TestExecute(base.BaseTest):

    def setUp(self):
        super(TestExecute, self).setUp()
        self.back_up = todo.commands.copy()
        args_msg = '{0} is expecting args to be passed to it, but none are.'
        noargs_msg = '{0} is having args passed during execution when none should be.'
        for (k, v) in todo.commands.items():
            if todo.commands[k][0]:
                todo.commands[k] = (todo.commands[k][0], partial(self.assert_args,
                    args_msg.format(k)))
            else:
                todo.commands[k] = (todo.commands[k][0], partial(self.assert_no_args,
                    noargs_msg.format(k)))

    def tearDown(self):
        super(TestExecute, self).tearDown()
        todo.commands = self.back_up.copy()
    
    def assert_args(self, msg, *args):
        self.assertIsNotNone(args, msg)

    def assert_no_args(self, msg, *args):
        if args:
            self.fail(msg)

    def test_execution(self):
        _args = ('foo', 'bar', 'bogus')

        for command in todo.commands:
            args = [command]
            args.extend(_args)
            todo.execute_commands(args)
