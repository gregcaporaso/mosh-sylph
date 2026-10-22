# ----------------------------------------------------------------------------
# Copyright (c) 2026, Greg Caporaso.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import (Bool, Choices, Citations, Float, Int, List, Plugin,
                           Range, Str)
from q2_types.feature_data import FeatureData, Taxonomy
from q2_types.feature_table import FeatureTable, RelativeFrequency
from q2_types.metadata import ImmutableMetadata
from q2_types.per_sample_sequences import PairedEndSequencesWithQuality
from q2_types.sample_data import SampleData

from mosh_sylph import __version__
from mosh_sylph._examples import (_fetch_database_example, _profile_example,
                                  _profile_to_tables_example,
                                  _query_example, _query_to_metadata_example,
                                  _sketch_example)
from mosh_sylph._convert import profile_to_tables, query_to_metadata
from mosh_sylph._formats import (SylphDatabaseDirFmt, SylphDatabaseFormat,
                                 SylphProfileDirFmt, SylphProfileFormat,
                                 SylphQueryDirFmt, SylphQueryFormat,
                                 SylphSketchesDirFmt, SylphSketchFormat)
from mosh_sylph._sylph import (GTDB_RELEASES, fetch_database, profile, query,
                               sketch)
from mosh_sylph._types import (SylphDatabase, SylphProfile, SylphQuery,
                               SylphSketches)

citations = Citations.load("citations.bib", package="mosh_sylph")

plugin = Plugin(
    name="sylph",
    version=__version__,
    website="https://github.com/gregcaporaso/mosh-sylph",
    package="mosh_sylph",
    description=("Thin wrappers of the sylph metagenome profiler and "
                 "conversions of its outputs to genome-keyed feature tables "
                 "and metadata."),
    short_description="sylph metagenome profiling.",
    citations=[citations['Shaw-Yu-2025']]
)

_EXPERIMENTAL = ' EXPERIMENTAL: this is AI-generated code; human review pending.'

# Inputs and options sylph profile and sylph query share.
_SEARCH_INPUTS = {'sketches': SylphSketches, 'database': SylphDatabase}
_SEARCH_INPUT_DESCRIPTIONS = {
    'sketches': 'Read sketches, one per sample (made with the database\'s c '
                'and k).',
    'database': 'A two-stage sylph database.'}
_SEARCH_PARAMETERS = {'threads': Int % Range(1, None),
                      'minimum_ani': Float % Range(0, 100, inclusive_end=True),
                      'min_number_kmers': Int % Range(1, None),
                      'min_contain': Int % Range(1, None),
                      'min_count_correct': Float % Range(0, None),
                      'screen_ani': Float % Range(0, 100, inclusive_end=True)}
_SEARCH_PARAMETER_DESCRIPTIONS = {
    'threads': 'Threads (-t).',
    'minimum_ani': 'Minimum adjusted ANI, 0-100, for a genome to be reported '
                   '(--minimum-ani).',
    'min_number_kmers': 'Discard genomes with fewer sampled k-mers '
                        '(--min-number-kmers).',
    'min_contain': 'Minimum number of contained k-mers for a hit '
                   '(--min-contain).',
    'min_count_correct': 'Minimum k-mer multiplicity for coverage correction '
                         '(--min-count-correct).',
    'screen_ani': 'Minimum adjusted ANI, 0-100, for a genome to pass the '
                  'first-stage screen of a two-stage database (--screen-ani).'}

plugin.register_formats(SylphDatabaseFormat, SylphDatabaseDirFmt,
                        SylphSketchFormat, SylphSketchesDirFmt,
                        SylphProfileFormat, SylphProfileDirFmt,
                        SylphQueryFormat, SylphQueryDirFmt)
plugin.register_semantic_types(SylphDatabase, SylphSketches, SylphProfile,
                               SylphQuery)
plugin.register_artifact_class(
    SylphDatabase, SylphDatabaseDirFmt,
    description='A two-stage sylph genome database (.syl2db, sylph >= 1.0.0), '
                'which sylph profile and sylph query search.')
plugin.register_artifact_class(
    SylphSketches, SylphSketchesDirFmt,
    description='sylph read sketches, one .sylsp file per sample, which sylph '
                'profile and sylph query search against a database.')
plugin.register_artifact_class(
    SylphProfile, SylphProfileDirFmt,
    description='sylph profile output: a TSV with one row per sample and '
                'detected genome (taxonomic and sequence abundance, ANI, '
                'coverage), as sylph writes it.')
plugin.register_artifact_class(
    SylphQuery, SylphQueryDirFmt,
    description='sylph query output: a TSV with one row per sample and '
                'database genome with enough sampled k-mers (containment ANI, '
                'coverage), as sylph writes it.')
plugin.methods.register_function(
    function=fetch_database,
    inputs={},
    parameters={'release': Str % Choices(GTDB_RELEASES),
                'base_url': Str},
    outputs=[('database', SylphDatabase)],
    parameter_descriptions={
        'release': 'GTDB release; the newest one the authors have built a '
                   'database for by default.',
        'base_url': 'Where the file gtdb-r<release>-c200-dbv2.syl2db is '
                    'downloaded from: the authors\' server by default; their '
                    'mirror is https://storage.googleapis.com/sylph-stuff.'},
    output_descriptions={
        'database': 'The sylph database of the release\'s species '
                    'representatives (one genome per species, sketched at '
                    'c=200, k=31).'},
    name='Download a pre-built sylph GTDB database',
    description=(
        'Downloads the sylph authors\' pre-built two-stage database of the GTDB '
        'species representatives for one release. Reads must be sketched with '
        'the same c (200) and k (31).'
        + _EXPERIMENTAL),
    citations=[citations['Shaw-Yu-2025']],
    examples={'fetch_database_r232': _fetch_database_example},
)

plugin.methods.register_function(
    function=sketch,
    inputs={'reads': SampleData[PairedEndSequencesWithQuality]},
    parameters={'threads': Int % Range(1, None),
                'c': Int % Range(1, None),
                'k': Int % (Range(21, 22) | Range(31, 32)),
                'fpr': Float % Range(0, 1, inclusive_end=False)},
    outputs=[('sketches', SylphSketches)],
    input_descriptions={'reads': 'Paired-end reads, one pair of files per '
                                 'sample.'},
    parameter_descriptions={
        'threads': 'Threads (sylph sketch -t).',
        'c': 'Subsampling rate (sylph sketch -c): one k-mer in c is kept. '
             'Must match the database (200 for the pre-built GTDB '
             'databases).',
        'k': 'k-mer size (sylph sketch -k), 21 or 31. Must match the '
             'database (31 for the pre-built GTDB databases).',
        'fpr': 'False positive rate of the read deduplication hashing '
               '(sylph sketch --fpr).'},
    output_descriptions={'sketches': 'One sketch per sample, named by sample '
                                     'ID.'},
    name='Sketch reads',
    description=('sylph sketch of every sample\'s read pairs (--l1, --l2, with '
                 'the sample IDs as sketch names through --lS): the k-mer '
                 'sketch that sylph profile and sylph query search. Sketch '
                 'once, then profile and query as often as needed.'
                 + _EXPERIMENTAL),
    citations=[citations['Shaw-Yu-2025']],
    examples={'sketch_reads': _sketch_example},
)

plugin.methods.register_function(
    function=profile,
    inputs=_SEARCH_INPUTS,
    parameters={**_SEARCH_PARAMETERS,
                'estimate_unknown': Bool,
                'read_seq_id': Float % Range(0, 100, inclusive_end=True)},
    outputs=[('profile', SylphProfile)],
    input_descriptions=_SEARCH_INPUT_DESCRIPTIONS,
    parameter_descriptions={
        **_SEARCH_PARAMETER_DESCRIPTIONS,
        'minimum_ani': 'Minimum adjusted ANI, 0-100, for a genome to be '
                       'reported (--minimum-ani). Below 95 the abundances are '
                       'inaccurate, sylph warns.',
        'estimate_unknown': 'Estimate the share of reads from genomes absent '
                            'from the database and scale the sequence '
                            'abundance by it (-u); the coverage column is then '
                            'True_cov instead of Eff_cov.',
        'read_seq_id': 'Sequence identity (%) of the reads, overriding '
                       'automatic detection; used only with estimate_unknown '
                       '(--read-seq-id).'},
    output_descriptions={
        'profile': 'sylph profile\'s TSV: per sample and detected genome, '
                   'Taxonomic_abundance (genome-size corrected, %), '
                   'Sequence_abundance (% of reads), Adjusted_ANI, coverage and '
                   'the other statistics sylph reports. A sample in which '
                   'nothing is detected has no rows.'},
    name='Profile sketches against a database',
    description=('sylph profile: species-level abundances and ANI of the '
                 'database genomes in every sample; profile-to-tables turns it '
                 'into feature tables.' + _EXPERIMENTAL),
    citations=[citations['Shaw-Yu-2025']],
    examples={'profile_with_unknown_share': _profile_example},
)

plugin.methods.register_function(
    function=query,
    inputs=_SEARCH_INPUTS,
    parameters=_SEARCH_PARAMETERS,
    outputs=[('query', SylphQuery)],
    input_descriptions=_SEARCH_INPUT_DESCRIPTIONS,
    parameter_descriptions={
        **_SEARCH_PARAMETER_DESCRIPTIONS,
        'minimum_ani': 'Minimum adjusted ANI, 0-100, for a genome to be '
                       'reported (--minimum-ani; sylph\'s default for query is '
                       '90, lower than profile\'s 95).'},
    output_descriptions={
        'query': 'sylph query\'s TSV: per sample and genome, '
                 'Adjusted_ANI, Eff_cov, ANI_5-95_percentile, '
                 'Containment_ind, Naive_ANI and the other statistics sylph '
                 'reports. A sample with no genome above the thresholds has '
                 'no rows.'},
    name='Query sketches against a database',
    description=(
        'sylph query: the coverage-adjusted containment ANI of every database '
        'genome in every sample, without abundances and without profile\'s '
        'reassignment of shared k-mers, so closely related genomes are all '
        'reported. At effective coverage below about 0.1x the adjusted ANI and '
        'its 5-95 percentile interval overshoot (the interval can exceed 100), '
        'so read low-coverage rows with the containment index and naive ANI.'
        + _EXPERIMENTAL),
    citations=[citations['Shaw-Yu-2025']],
    examples={'query_sketches': _query_example},
)

plugin.methods.register_function(
    function=profile_to_tables,
    inputs={'profile': SylphProfile, 'sketches': SylphSketches},
    parameters={'gtdb_ids': Bool},
    outputs=[('taxonomic_abundance', FeatureTable[RelativeFrequency]),
             ('sequence_abundance', FeatureTable[RelativeFrequency]),
             ('stats', ImmutableMetadata)],
    input_descriptions={
        'profile': 'A sylph profile result.',
        'sketches': 'The sketches that were profiled: their sample IDs are '
                    'the table\'s samples, so a sample in which sylph '
                    'detected nothing gets an all-zero column.'},
    parameter_descriptions={
        'gtdb_ids': 'Name the genomes as GTDB does (RS_GCF_... for RefSeq, '
                    'GB_GCA_... for GenBank), the IDs of GTDB\'s taxonomy '
                    'files and trees; off, the NCBI accession parsed from the '
                    'genome file name (GCF_000023865.1), or the file name '
                    'without its extension for a non-NCBI genome.'},
    output_descriptions={
        'taxonomic_abundance': 'Genome-size-corrected abundance of each '
                               'genome (sylph\'s Taxonomic_abundance), as '
                               'proportions summing to 1 per sample with a '
                               'detection.',
        'sequence_abundance': 'Share of reads assigned to each genome '
                              '(sylph\'s Sequence_abundance divided by 100). '
                              'With estimate-unknown a sample sums to its '
                              'classified share, not to 1: the remainder is '
                              'the unknown-share in stats (see "Estimating '
                              'percentage of unknown reads" at '
                              'https://sylph-docs.github.io/sylph-cookbook/).',
        'stats': 'Per sample: genomes detected, median ANI of the detected '
                 'genomes, and unknown-share, the share of reads not '
                 'assigned to any database genome (meaningful only for a '
                 'profile made with estimate-unknown; 0 otherwise, 1 when '
                 'nothing was detected).'},
    name='Feature tables from a sylph profile',
    description=(
        'Converts sylph profile output into genome-keyed feature tables and '
        'per-sample statistics, with no taxonomy step: the names in the '
        'tables are the genome IDs, by default in GTDB\'s form, so a GTDB '
        'taxonomy file imported as FeatureData[Taxonomy] and the GTDB tree '
        'serve as the tables\' taxonomy and phylogeny.' + _EXPERIMENTAL),
    citations=[citations['Shaw-Yu-2025']],
    examples={'profile_to_tables': _profile_to_tables_example},
)

plugin.methods.register_function(
    function=query_to_metadata,
    inputs={'query': SylphQuery, 'taxonomy': FeatureData[Taxonomy]},
    parameters={'gtdb_ids': Bool, 'targets': List[Str]},
    outputs=[('query_metadata', ImmutableMetadata)],
    input_descriptions={
        'query': 'A sylph query result.',
        'taxonomy': 'A taxonomy keyed like the genome IDs (GTDB\'s taxonomy '
                    'file imported as FeatureData[Taxonomy]), joined to the '
                    'rows when given (optional).'},
    parameter_descriptions={
        'gtdb_ids': 'Name the genomes as GTDB does (RS_GCF_... for RefSeq, '
                    'GB_GCA_... for GenBank), the IDs of GTDB\'s taxonomy '
                    'files and trees; off, the NCBI accession parsed from the '
                    'genome file name (GCF_000023865.1), or the file name '
                    'without its extension for a non-NCBI genome.',
        'targets': 'Keep only genomes whose taxonomy string or genome ID '
                   'contains one of these texts (e.g. g__Thermobifida; or '
                   'GCF_001592045.1); all genomes when omitted.'},
    output_descriptions={
        'query_metadata': 'One row per sample and genome, ID '
                          '<sample-id>-<genome>, with columns sample, genome, '
                          'taxonomy (empty without a taxonomy), adjusted-ani, '
                          'effective-coverage, ani-5-percentile and '
                          'ani-95-percentile (sylph\'s 5-95 percentile '
                          'interval, missing when sylph reports NA), '
                          'containment-index and naive-ani.'},
    name='Metadata from a sylph query',
    description=(
        'Tabulates sylph query output, with a taxonomy joined by genome ID '
        'when given, for metadata tabulate or filtering. At effective '
        'coverage below about 0.1x the adjusted ANI and its interval '
        'overshoot (the 95th percentile can exceed 100); read such rows with '
        'the containment index and naive ANI.' + _EXPERIMENTAL),
    citations=[citations['Shaw-Yu-2025']],
    examples={'query_to_metadata_thermobifida': _query_to_metadata_example},
)
