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


def _reads_factory():
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
    from mosh_sylph._formats import SylphTwoStageDatabaseFormat
    return Artifact.import_data('SylphTwoStageDatabase', _data_path('fixture.syl2db'),
                                SylphTwoStageDatabaseFormat)


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


def _profile_factory():
    from mosh_sylph.plugin_setup import plugin
    sketches, = plugin.methods['sketch'](_reads_factory(), threads=1)
    profile, = plugin.methods['profile'](sketches, _database_factory(),
                                         threads=1, estimate_unknown=True)
    return profile


def _sketches_factory():
    # TODO: this is AI-generated code; human review pending
    from mosh_sylph.plugin_setup import plugin
    sketches, = plugin.methods['sketch'](_reads_factory(), threads=1)
    return sketches


def _profile_to_tables_example(use):
    # TODO: this is AI-generated code; human review pending
    profile = use.init_artifact('sylph-profile', _profile_factory)
    sketches = use.init_artifact('sketches', _sketches_factory)
    use.action(
        use.UsageAction('sylph', 'profile_to_tables'),
        use.UsageInputs(profile=profile, sketches=sketches),
        use.UsageOutputNames(taxonomic_abundance='sylph-taxonomic-abundance',
                             sequence_abundance='sylph-sequence-abundance',
                             stats='sylph-stats'),
    )


def _query_factory():
    # TODO: this is AI-generated code; human review pending
    from mosh_sylph.plugin_setup import plugin
    result, = plugin.methods['query'](_sketches_factory(), _database_factory(),
                                      threads=1)
    return result


_GENOME_TAXONOMY = {
    'RS_GCF_000023865.1': 'd__Bacteria;p__Actinomycetota;c__Actinomycetes;'
                          'o__Mycobacteriales;f__Pseudonocardiaceae;'
                          'g__Saccharomonospora;s__Saccharomonospora viridis',
    'RS_GCF_001592045.1': 'd__Bacteria;p__Actinomycetota;c__Actinomycetes;'
                          'o__Streptosporangiales;f__Streptosporangiaceae;'
                          'g__Thermobifida;s__Thermobifida fusca',
}


def _genome_taxonomy_factory():
    # TODO: this is AI-generated code; human review pending
    """The GTDB r232 taxonomy of two fixture genomes keyed by GTDB genome ID,
    shaped like GTDB's taxonomy file imported as FeatureData[Taxonomy]."""
    import pandas as pd
    taxonomy = pd.Series(_GENOME_TAXONOMY, name='Taxon')
    taxonomy.index.name = 'Feature ID'
    return Artifact.import_data('FeatureData[Taxonomy]', taxonomy)


def _query_to_metadata_example(use):
    # TODO: this is AI-generated code; human review pending
    query = use.init_artifact('sylph-query', _query_factory)
    taxonomy = use.init_artifact('gtdb-taxonomy', _genome_taxonomy_factory)
    use.action(
        use.UsageAction('sylph', 'query_to_metadata'),
        use.UsageInputs(query=query, taxonomy=taxonomy,
                        targets=['g__Thermobifida;']),
        use.UsageOutputNames(query_metadata='thermobifida-query'),
    )
