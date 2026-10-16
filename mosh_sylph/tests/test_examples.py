# ----------------------------------------------------------------------------
# Copyright (c) 2026, Greg Caporaso.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from unittest import mock

from qiime2.plugin.testing import TestPluginBase


class ExamplesTests(TestPluginBase):
    """Run every usage example registered on the plugin's actions; the
    download examples fetch the fixture instead of the real releases."""
    package = 'mosh_sylph.tests'

    def test_examples(self):
        # TODO: this is AI-generated code; human review pending
        database = 'file://' + self.get_data_path('fixture.syl2db')
        taxonomy = 'file://' + self.get_data_path('taxonomy.tsv.gz')
        with mock.patch('mosh_sylph._sylph._database_url',
                        return_value=database), \
                mock.patch('mosh_sylph._sylph_tax._taxonomy_url',
                           return_value=taxonomy):
            self.execute_examples()
