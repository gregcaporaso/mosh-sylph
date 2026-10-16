# ----------------------------------------------------------------------------
# Copyright (c) 2026, Greg Caporaso.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import filecmp
import gzip
import os
import subprocess
import tempfile
from unittest import mock

from qiime2 import Artifact
from qiime2.plugin import ValidationError
from qiime2.plugin.testing import TestPluginBase

from mosh_sylph import _examples as ex
from mosh_sylph._formats import (SylphMpaFormat, SylphProfileDirFmt,
                                 SylphTaxonomyDirFmt, SylphTaxonomyFormat,
                                 SylphTaxProfilesDirFmt)
from mosh_sylph._sylph_tax import TAXONOMIES, _taxonomy_url


class TaxDownloadTests(TestPluginBase):
    package = 'mosh_sylph.tests'

    def test_download_is_the_file(self):
        # TODO: this is AI-generated code; human review pending
        source = self.get_data_path('taxonomy.tsv.gz')
        with mock.patch('mosh_sylph._sylph_tax._taxonomy_url',
                        return_value='file://' + source) as url:
            taxonomy, = self.plugin.methods['tax_download'](taxonomy='GTDB_r232')
        url.assert_called_once_with('GTDB_r232')
        self.assertEqual(str(taxonomy.type), 'SylphTaxonomy')
        path = os.path.join(str(taxonomy.view(SylphTaxonomyDirFmt)),
                            'taxonomy.tsv.gz')
        self.assertTrue(filecmp.cmp(path, source, shallow=False))

    def test_urls_are_sylph_tax_urls(self):
        # TODO: this is AI-generated code; human review pending
        self.assertIn('GTDB_r232', TAXONOMIES)
        self.assertEqual(_taxonomy_url('GTDB_r232'),
                         'https://zenodo.org/records/19646381/files/'
                         'gtdb_r232_metadata.tsv.gz')
        for taxonomy in TAXONOMIES:
            self.assertTrue(_taxonomy_url(taxonomy).startswith('https://'))


class SylphTaxonomyFormatTests(TestPluginBase):
    package = 'mosh_sylph.tests'

    def test_valid(self):
        # TODO: this is AI-generated code; human review pending
        SylphTaxonomyFormat(self.get_data_path('taxonomy.tsv.gz'),
                            mode='r').validate()

    def test_one_column(self):
        # TODO: this is AI-generated code; human review pending
        with tempfile.NamedTemporaryFile(suffix='.gz') as fh:
            with gzip.open(fh.name, 'wt') as gz:
                gz.write('GCF_1.1\n')
            with self.assertRaisesRegex(ValidationError, 'line 1'):
                SylphTaxonomyFormat(fh.name, mode='r').validate()

    def test_not_gzipped(self):
        # TODO: this is AI-generated code; human review pending
        with tempfile.NamedTemporaryFile(suffix='.gz') as fh:
            fh.write(b'GCF_1.1\td__Bacteria\n')
            fh.flush()
            with self.assertRaisesRegex(ValidationError, 'not gzipped'):
                SylphTaxonomyFormat(fh.name, mode='r').validate()


def _sylph_tax(*args):
    # TODO: this is AI-generated code; human review pending
    subprocess.run(['sylph-tax', '--no-config', *args], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _read_dir(path):
    # TODO: this is AI-generated code; human review pending
    """{file name: text} of a directory."""
    out = {}
    for f in sorted(os.listdir(path)):
        with open(os.path.join(path, f)) as fh:
            out[f] = fh.read()
    return out


class TaxprofTests(TestPluginBase):
    package = 'mosh_sylph.tests'

    @classmethod
    def setUpClass(cls):
        # TODO: this is AI-generated code; human review pending
        super().setUpClass()
        cls.profile = ex._profile_factory()
        cls.taxonomy = ex._taxonomy_factory()
        cls.profile_path = os.path.join(
            str(cls.profile.view(SylphProfileDirFmt)), 'profile.tsv')
        cls.taxonomy_path = os.path.join(
            str(cls.taxonomy.view(SylphTaxonomyDirFmt)), 'taxonomy.tsv.gz')

    def test_same_as_sylph_tax_taxprof(self):
        # TODO: this is AI-generated code; human review pending
        result, = self.plugin.methods['taxprof'](self.profile, self.taxonomy)
        self.assertEqual(str(result.type), 'SylphTaxProfiles')
        observed = _read_dir(str(result.view(SylphTaxProfilesDirFmt)))
        with tempfile.TemporaryDirectory() as d:
            _sylph_tax('taxprof', self.profile_path, '-t', self.taxonomy_path,
                       '-o', d + os.sep)
            expected = _read_dir(d)
        self.assertEqual(observed, expected)
        # 73F84 has no detected genome, so no file
        self.assertEqual(list(observed), ['1135D.sylphmpa', 'DB47D.sylphmpa'])
        self.assertIn('g__Thermobifida|s__Thermobifida fusca|'
                      't__GCF_001592045.1', observed['DB47D.sylphmpa'])

    def test_nothing_detected(self):
        # TODO: this is AI-generated code; human review pending
        with open(self.profile_path) as fh:
            header = fh.readline()
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, 'profile.tsv'), 'w') as fh:
                fh.write(header)
            profile = Artifact.import_data('SylphProfile', d)
        with self.assertRaisesRegex(ValueError, 'detected no genome'):
            self.plugin.methods['taxprof'](profile, self.taxonomy)


class SylphMpaFormatTests(TestPluginBase):
    package = 'mosh_sylph.tests'

    def test_not_sylphmpa(self):
        # TODO: this is AI-generated code; human review pending
        with tempfile.NamedTemporaryFile('w', suffix='.sylphmpa') as fh:
            fh.write('clade_name\trelative_abundance\n')
            fh.flush()
            with self.assertRaisesRegex(ValidationError, '#SampleID'):
                SylphMpaFormat(fh.name, mode='r').validate()
