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
import subprocess
import tempfile

import pandas as pd

from qiime2.plugin import ValidationError
from qiime2.plugin.testing import TestPluginBase
from q2_types.per_sample_sequences import SingleLanePerSamplePairedEndFastqDirFmt

from mosh_sylph import _examples as ex
from mosh_sylph._formats import (SylphDatabaseDirFmt, SylphDatabaseFormat,
                                 SylphSketchesDirFmt, SylphSketchFormat)
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


def _sylph(*args):
    # TODO: this is AI-generated code; human review pending
    subprocess.run(['sylph', *args], check=True, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)


def _read_paths(reads):
    # TODO: this is AI-generated code; human review pending
    """{sample id: (forward, reverse)} of a paired-end reads artifact."""
    manifest = reads.view(SingleLanePerSamplePairedEndFastqDirFmt).manifest.view(
        pd.DataFrame)
    return {s: (r['forward'], r['reverse']) for s, r in manifest.iterrows()}


class SketchTests(TestPluginBase):
    package = 'mosh_sylph.tests'

    def test_same_as_sylph_sketch(self):
        # TODO: this is AI-generated code; human review pending
        reads = ex._reads_factory()
        sketches, = self.plugin.methods['sketch'](reads, threads=1)
        self.assertEqual(str(sketches.type), 'SylphSketches')
        paths = sketches.view(SylphSketchesDirFmt).sample_paths()
        self.assertEqual(list(paths), ex._SAMPLES)
        with tempfile.TemporaryDirectory() as d:
            for sample, (r1, r2) in _read_paths(reads).items():
                _sylph('sketch', '-t', '1', '-1', r1, '-2', r2, '-S', sample,
                       '-d', d)
                self.assertTrue(filecmp.cmp(
                    os.path.join(d, f'{sample}.paired.sylsp'), paths[sample],
                    shallow=False), sample)

    def test_c_and_k_reach_sylph(self):
        # TODO: this is AI-generated code; human review pending
        reads = ex._reads_factory()
        sketches, = self.plugin.methods['sketch'](reads, threads=1, c=100, k=21)
        path = sketches.view(SylphSketchesDirFmt).sample_paths()['1135D']
        with tempfile.TemporaryDirectory() as d:
            r1, r2 = _read_paths(reads)['1135D']
            _sylph('sketch', '-t', '1', '-c', '100', '-k', '21', '-1', r1, '-2',
                   r2, '-S', '1135D', '-d', d)
            self.assertTrue(filecmp.cmp(os.path.join(d, '1135D.paired.sylsp'),
                                        path, shallow=False))


class SylphSketchesFormatTests(TestPluginBase):
    package = 'mosh_sylph.tests'

    def test_empty_sketch(self):
        # TODO: this is AI-generated code; human review pending
        with tempfile.TemporaryDirectory() as d:
            open(os.path.join(d, 's1.paired.sylsp'), 'wb').close()
            with self.assertRaisesRegex(ValidationError, 'empty sylph sketch'):
                SylphSketchFormat(os.path.join(d, 's1.paired.sylsp'),
                                  mode='r').validate()

    def test_sample_paths(self):
        # TODO: this is AI-generated code; human review pending
        with tempfile.TemporaryDirectory() as d:
            for s in ['b', 'a']:
                with open(os.path.join(d, f'{s}.paired.sylsp'), 'wb') as fh:
                    fh.write(b'x')
            fmt = SylphSketchesDirFmt(d, mode='r')
            fmt.validate()
            self.assertEqual(list(fmt.sample_paths()), ['a', 'b'])
