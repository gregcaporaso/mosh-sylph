# ----------------------------------------------------------------------------
# Copyright (c) 2026, Greg Caporaso.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import filecmp
import os
import shutil
import tempfile

from qiime2.plugin import ValidationError
from qiime2.plugin.testing import TestPluginBase

from mosh_sylph._formats import SylphDatabaseDirFmt, SylphDatabaseFormat
from mosh_sylph._sylph import _database_url


class FetchDatabaseTests(TestPluginBase):
    package = 'mosh_sylph.tests'

    def test_download_is_the_file(self):
        # TODO: this is AI-generated code; human review pending
        source = self.get_data_path('fixture.syl2db')
        with tempfile.TemporaryDirectory() as host:
            shutil.copy(source, os.path.join(host, 'gtdb-r232-c200-dbv2.syl2db'))
            database, = self.plugin.methods['fetch_database'](
                release='232', base_url='file://' + host)
        self.assertEqual(str(database.type), 'SylphDatabase')
        path = os.path.join(str(database.view(SylphDatabaseDirFmt)),
                            'database.syl2db')
        self.assertTrue(filecmp.cmp(path, source, shallow=False))

    def test_url(self):
        # TODO: this is AI-generated code; human review pending
        self.assertEqual(
            _database_url('http://faust.compbio.cs.cmu.edu/sylph-stuff', '232'),
            'http://faust.compbio.cs.cmu.edu/sylph-stuff/'
            'gtdb-r232-c200-dbv2.syl2db')
        self.assertEqual(_database_url('https://mirror/x/', '226'),
                         'https://mirror/x/gtdb-r226-c200-dbv2.syl2db')


class SylphDatabaseFormatTests(TestPluginBase):
    package = 'mosh_sylph.tests'

    def test_valid(self):
        # TODO: this is AI-generated code; human review pending
        SylphDatabaseFormat(self.get_data_path('fixture.syl2db'),
                            mode='r').validate()

    def test_single_stage_database_rejected(self):
        # TODO: this is AI-generated code; human review pending
        with tempfile.NamedTemporaryFile(suffix='.syldb') as fh:
            fh.write(b'\x03\x00\x00\x00\x00\x00\x00\x00')
            fh.flush()
            with self.assertRaisesRegex(ValidationError, 'two-stage'):
                SylphDatabaseFormat(fh.name, mode='r').validate()
