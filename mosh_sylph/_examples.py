# ----------------------------------------------------------------------------
# Copyright (c) 2026, Greg Caporaso.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

"""Usage examples, registered on the actions and executed by the tests.

The download examples name the real releases; the tests point the downloads
at the fixture in tests/data. Every other example runs on that fixture: three
GTDB r232 genomes in a two-stage database and a few thousand read pairs from
three tutorial samples (tests/data/README.md says how they were made).
"""

import os

_DATA = os.path.join(os.path.dirname(__file__), 'tests', 'data')


def _data_path(name):
    # TODO: this is AI-generated code; human review pending
    return os.path.join(_DATA, name)


def _fetch_database_example(use):
    # TODO: this is AI-generated code; human review pending
    use.action(
        use.UsageAction('sylph', 'fetch_database'),
        use.UsageInputs(release='232'),
        use.UsageOutputNames(database='sylph-gtdb-r232'),
    )


def _tax_download_example(use):
    # TODO: this is AI-generated code; human review pending
    use.action(
        use.UsageAction('sylph', 'tax_download'),
        use.UsageInputs(taxonomy='GTDB_r232'),
        use.UsageOutputNames(sylph_taxonomy='sylph-taxonomy-gtdb-r232'),
    )
