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
import tempfile
from unittest import mock

from qiime2.plugin import ValidationError
from qiime2.plugin.testing import TestPluginBase

from mosh_sylph._formats import SylphTaxonomyDirFmt, SylphTaxonomyFormat
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
