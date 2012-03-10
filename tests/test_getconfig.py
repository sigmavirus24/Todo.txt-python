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
import re
import os
from functools import partial

class TestConfig(base.BaseTest):

    def setUp(self):
        file_re = re.compile('(\w+\/\w+\.)config')
        # Just some nice magic:
        self.sub = partial(file_re.sub, '\g<1>plain')
        super(TestConfig, self).setUp()

    def tearDown(self):
        todo.CONFIG = self.backup

    def config_assert(self, key, val):
        self.assertEquals(todo.CONFIG[key], val)

    def _validate_(self, filename):
        filename = self.sub(filename)
        with open(filename, 'r') as fd:
            for line in fd:
                if line.startswith('#') or line == '\n':
                    continue
                key, val = line.split()
                if val == "False":
                    val = False
                elif val == "True":
                    val = True
                self.config_assert(key, val)

    def test_configs(self):
        self.backup = todo.CONFIG.copy()
        self.environ = os.environ.copy()
        for f in os.listdir('tests/config/'):
            if f.endswith('config'):
                f = ''.join(['tests/config/', f])
                todo.get_config(config_name=f)
                self._validate_(f)
                todo.CONFIG = self.backup.copy()
                os.environ = self.environ.copy()

