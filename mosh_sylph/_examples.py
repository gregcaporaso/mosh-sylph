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
import tempfile

from qiime2 import Artifact

_DATA = os.path.join(os.path.dirname(__file__), 'tests', 'data')
_SAMPLES = ['1135D', '73F84', 'DB47D']


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


def _reads_factory():
    # TODO: this is AI-generated code; human review pending
    with tempfile.TemporaryDirectory() as work:
        manifest = os.path.join(work, 'manifest.tsv')
        with open(manifest, 'w') as fh:
            fh.write('sample-id\tforward-absolute-filepath\t'
                     'reverse-absolute-filepath\n')
            for s in _SAMPLES:
                fh.write(f'{s}\t{_data_path(f"reads/{s}_R1.fastq.gz")}\t'
                         f'{_data_path(f"reads/{s}_R2.fastq.gz")}\n')
        return Artifact.import_data('SampleData[PairedEndSequencesWithQuality]',
                                    manifest, 'PairedEndFastqManifestPhred33V2')


def _sketch_example(use):
    # TODO: this is AI-generated code; human review pending
    reads = use.init_artifact('reads', _reads_factory)
    use.action(
        use.UsageAction('sylph', 'sketch'),
        use.UsageInputs(reads=reads, threads=1),
        use.UsageOutputNames(sketches='sketches'),
    )


def _database_factory():
    # TODO: this is AI-generated code; human review pending
    from mosh_sylph._formats import SylphDatabaseFormat
    return Artifact.import_data('SylphDatabase', _data_path('fixture.syl2db'),
                                SylphDatabaseFormat)


def _profile_example(use):
    # TODO: this is AI-generated code; human review pending
    reads = use.init_artifact('reads', _reads_factory)
    database = use.init_artifact('sylph-database', _database_factory)
    sketches, = use.action(
        use.UsageAction('sylph', 'sketch'),
        use.UsageInputs(reads=reads, threads=1),
        use.UsageOutputNames(sketches='sketches'),
    )
    use.action(
        use.UsageAction('sylph', 'profile'),
        use.UsageInputs(sketches=sketches, database=database, threads=1,
                        estimate_unknown=True),
        use.UsageOutputNames(profile='sylph-profile'),
    )


def _query_example(use):
    # TODO: this is AI-generated code; human review pending
    reads = use.init_artifact('reads', _reads_factory)
    database = use.init_artifact('sylph-database', _database_factory)
    sketches, = use.action(
        use.UsageAction('sylph', 'sketch'),
        use.UsageInputs(reads=reads, threads=1),
        use.UsageOutputNames(sketches='sketches'),
    )
    use.action(
        use.UsageAction('sylph', 'query'),
        use.UsageInputs(sketches=sketches, database=database, threads=1),
        use.UsageOutputNames(query='sylph-query'),
    )
