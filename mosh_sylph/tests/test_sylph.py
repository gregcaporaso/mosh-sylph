# ----------------------------------------------------------------------------
# Copyright (c) 2026, Greg Caporaso.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import filecmp
import inspect
import io
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
                                 SylphProfileDirFmt, SylphProfileFormat,
                                 SylphQueryDirFmt, SylphQueryFormat,
                                 SylphSketchesDirFmt, SylphSketchFormat)
from mosh_sylph._sylph import GTDB_RELEASES, _database_url, fetch_database


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

    def test_default_release_is_the_last_listed(self):
        # TODO: this is AI-generated code; human review pending
        self.assertEqual(GTDB_RELEASES, sorted(GTDB_RELEASES, key=int))
        default = inspect.signature(fetch_database).parameters['release']
        self.assertEqual(default.default, GTDB_RELEASES[-1])
        self.assertEqual(
            self.plugin.methods['fetch_database'].signature
                .parameters['release'].default, GTDB_RELEASES[-1])

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


class _SearchTestBase(TestPluginBase):
    """Sketches of the fixture reads and the fixture database, with a helper
    that runs sylph directly on the same files."""
    package = 'mosh_sylph.tests'

    @classmethod
    def setUpClass(cls):
        # TODO: this is AI-generated code; human review pending
        super().setUpClass()
        from mosh_sylph.plugin_setup import plugin
        cls.sketches, = plugin.methods['sketch'](ex._reads_factory(), threads=1)
        cls.database = ex._database_factory()
        cls.sketch_paths = list(
            cls.sketches.view(SylphSketchesDirFmt).sample_paths().values())
        cls.database_path = os.path.join(
            str(cls.database.view(SylphDatabaseDirFmt)), 'database.syl2db')

    def _direct(self, command, *options, sketch_paths=None):
        # TODO: this is AI-generated code; human review pending
        """Output of `sylph <command>` run directly, as text."""
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, 'out.tsv')
            _sylph(command, '-t', '1', *options, '-d', self.database_path,
                   '-o', out, *(sketch_paths or self.sketch_paths))
            with open(out) as fh:
                return fh.read()


class ProfileTests(_SearchTestBase):

    def _profile(self, **kwargs):
        # TODO: this is AI-generated code; human review pending
        result, = self.plugin.methods['profile'](
            self.sketches, self.database, threads=1, **kwargs)
        self.assertEqual(str(result.type), 'SylphProfile')
        with open(os.path.join(str(result.view(SylphProfileDirFmt)),
                               'profile.tsv')) as fh:
            return fh.read()

    def test_same_as_sylph_profile(self):
        # TODO: this is AI-generated code; human review pending
        observed = self._profile()
        self.assertEqual(observed, self._direct('profile'))
        df = pd.read_csv(io.StringIO(observed), sep='\t')
        self.assertEqual(list(zip(df['Sample_file'], df['Genome_file'])), [
            ('1135D', 'genomes/GCF_040096305.1_genomic.fna.gz'),
            ('DB47D', 'genomes/GCF_000023865.1_genomic.fna.gz'),
            ('DB47D', 'genomes/GCF_001592045.1_genomic.fna.gz')])
        self.assertIn('Eff_cov', df.columns)

    def test_estimate_unknown(self):
        # TODO: this is AI-generated code; human review pending
        observed = self._profile(estimate_unknown=True)
        self.assertEqual(observed, self._direct('profile', '-u'))
        df = pd.read_csv(io.StringIO(observed), sep='\t')
        self.assertIn('True_cov', df.columns)
        # about half of each sample's reads come from genomes not in the
        # database, so the detected genomes' sequence abundance is far below
        # 100% once the unknown share is estimated
        self.assertLess(df.groupby('Sample_file')['Sequence_abundance'].sum().max(),
                        75)

    def test_options_reach_sylph(self):
        # TODO: this is AI-generated code; human review pending
        observed = self._profile(minimum_ani=99.5, min_number_kmers=20,
                                 estimate_unknown=True, read_seq_id=99.0)
        self.assertEqual(observed, self._direct(
            'profile', '--minimum-ani', '99.5', '--min-number-kmers', '20',
            '-u', '--read-seq-id', '99.0'))
        # T. fusca in DB47D sits at an adjusted ANI of about 99.4
        self.assertNotIn('GCF_001592045.1', observed)

    def test_nothing_detected_is_a_header(self):
        # TODO: this is AI-generated code; human review pending
        soil = [p for p in self.sketch_paths if '73F84' in p]
        observed = self._direct('profile', sketch_paths=soil)
        self.assertEqual(observed.count('\n'), 1)
        with tempfile.NamedTemporaryFile('w', suffix='.tsv') as fh:
            fh.write(observed)
            fh.flush()
            SylphProfileFormat(fh.name, mode='r').validate()

    def test_format_rejects_query_output(self):
        # TODO: this is AI-generated code; human review pending
        with tempfile.NamedTemporaryFile('w', suffix='.tsv') as fh:
            fh.write(self._direct('query'))
            fh.flush()
            with self.assertRaisesRegex(ValidationError, 'header'):
                SylphProfileFormat(fh.name, mode='r').validate()


class QueryTests(_SearchTestBase):

    def _query(self, **kwargs):
        # TODO: this is AI-generated code; human review pending
        result, = self.plugin.methods['query'](
            self.sketches, self.database, threads=1, **kwargs)
        self.assertEqual(str(result.type), 'SylphQuery')
        with open(os.path.join(str(result.view(SylphQueryDirFmt)),
                               'query.tsv')) as fh:
            return fh.read()

    def test_same_as_sylph_query(self):
        # TODO: this is AI-generated code; human review pending
        observed = self._query()
        self.assertEqual(observed, self._direct('query'))
        df = pd.read_csv(io.StringIO(observed), sep='\t')
        self.assertEqual(sorted(zip(df['Sample_file'], df['Genome_file'])), [
            ('1135D', 'genomes/GCF_040096305.1_genomic.fna.gz'),
            ('DB47D', 'genomes/GCF_000023865.1_genomic.fna.gz'),
            ('DB47D', 'genomes/GCF_001592045.1_genomic.fna.gz')])

    def test_options_reach_sylph(self):
        # TODO: this is AI-generated code; human review pending
        observed = self._query(min_number_kmers=12000, screen_ani=80.0)
        self.assertEqual(observed, self._direct(
            'query', '--min-number-kmers', '12000', '--screen-ani', '80.0'))
        # R. intestinale, the genome detected in 1135D, has 9,886 sampled
        # k-mers, under the floor
        self.assertNotIn('1135D', observed)

    def test_format_rejects_profile_output(self):
        # TODO: this is AI-generated code; human review pending
        with tempfile.NamedTemporaryFile('w', suffix='.tsv') as fh:
            fh.write(self._direct('profile'))
            fh.flush()
            with self.assertRaisesRegex(ValidationError, 'header'):
                SylphQueryFormat(fh.name, mode='r').validate()
