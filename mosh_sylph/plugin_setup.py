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
                                  _query_example, _query_to_metadata_example,
                                  _sketch_example,
                                  _tax_download_example, _tax_merge_example,
                                  _taxprof_example, _taxprof_to_tables_example)
from mosh_sylph._convert import query_to_metadata, taxprof_to_tables
from mosh_sylph._formats import (SylphDatabaseDirFmt, SylphDatabaseFormat,
                                 SylphMergedProfileDirFmt,
                                 SylphMergedProfileFormat,
                                 SylphProfileDirFmt, SylphProfileFormat,
                                 SylphQueryDirFmt, SylphQueryFormat,
                                 SylphSketchesDirFmt, SylphSketchFormat,
                                 SylphMpaFormat, SylphTaxonomyDirFmt,
                                 SylphTaxonomyFormat, SylphTaxProfilesDirFmt)
from mosh_sylph._sylph import (GTDB_RELEASES, fetch_database, profile, query,
                               sketch)
from mosh_sylph._sylph_tax import (MERGE_COLUMNS, TAXONOMIES, tax_download,
                                   tax_merge, taxprof)
from mosh_sylph._types import (SylphDatabase, SylphMergedProfile, SylphProfile,
                               SylphQuery,
                               SylphSketches, SylphTaxonomy, SylphTaxProfiles)

citations = Citations.load("citations.bib", package="mosh_sylph")

plugin = Plugin(
    name="sylph",
    version=__version__,
    website="https://github.com/gregcaporaso/mosh-sylph",
    package="mosh_sylph",
    description=("Thin wrappers of the sylph metagenome profiler and sylph-tax "
                 "and conversions of those outputs to feature tables, "
                 "taxonomies and metadata."),
    short_description="sylph and sylph-tax metagenome profiling.",
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
                        SylphTaxonomyFormat, SylphTaxonomyDirFmt,
                        SylphSketchFormat, SylphSketchesDirFmt,
                        SylphProfileFormat, SylphProfileDirFmt,
                        SylphQueryFormat, SylphQueryDirFmt,
                        SylphMpaFormat, SylphTaxProfilesDirFmt,
                        SylphMergedProfileFormat, SylphMergedProfileDirFmt)
plugin.register_semantic_types(SylphDatabase, SylphTaxonomy, SylphSketches,
                               SylphProfile, SylphQuery, SylphTaxProfiles,
                               SylphMergedProfile)
plugin.register_artifact_class(
    SylphDatabase, SylphDatabaseDirFmt,
    description='A two-stage sylph genome database (.syl2db, sylph >= 1.0.0), '
                'which sylph profile and sylph query search.')
plugin.register_artifact_class(
    SylphTaxonomy, SylphTaxonomyDirFmt,
    description='sylph-tax taxonomy metadata: a gzipped two-column table of '
                'genome accession and taxonomy string, which sylph-tax taxprof '
                'joins to sylph profiles.')
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
plugin.register_artifact_class(
    SylphTaxProfiles, SylphTaxProfilesDirFmt,
    description='sylph-tax taxprof output: one .sylphmpa taxonomic profile '
                'per sample in which sylph detected a genome, as sylph-tax '
                'writes them.')
plugin.register_artifact_class(
    SylphMergedProfile, SylphMergedProfileDirFmt,
    description='sylph-tax merge output: a TSV of one profile column (for '
                'example relative_abundance) with a row per clade at every '
                'rank and a column per sample, as sylph-tax writes it.')

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
    function=tax_download,
    inputs={},
    parameters={'taxonomy': Str % Choices(list(TAXONOMIES))},
    outputs=[('sylph_taxonomy', SylphTaxonomy)],
    parameter_descriptions={
        'taxonomy': 'sylph-tax\'s identifier of the taxonomy: GTDB_r<release> '
                    'for the database fetch-database downloads for that '
                    'release, GlobDB_r<release> for an imported GlobDB '
                    'database.'},
    output_descriptions={
        'sylph_taxonomy': 'The taxonomy metadata file, as sylph-tax download '
                          'stores it.'},
    name='Download sylph-tax taxonomy metadata',
    description=(
        'Downloads the taxonomy metadata file that sylph-tax download fetches '
        'for one taxonomy identifier, from the URL sylph-tax lists for it '
        '(sylph-tax download itself fetches every taxonomy at once).'),
    citations=[citations['Shaw-Yu-2025']],
    examples={'tax_download_gtdb_r232': _tax_download_example},
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
                 'database genomes in every sample. sylph-tax taxprof adds '
                 'the taxonomy.' + _EXPERIMENTAL),
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
    function=taxprof,
    inputs={'profile': SylphProfile, 'sylph_taxonomy': SylphTaxonomy},
    parameters={},
    outputs=[('taxonomic_profiles', SylphTaxProfiles)],
    input_descriptions={
        'profile': 'A sylph profile.',
        'sylph_taxonomy': 'sylph-tax taxonomy metadata for the profile\'s '
                          'database (GTDB_r<release> for a GTDB database).'},
    output_descriptions={
        'taxonomic_profiles': 'One .sylphmpa file per sample in which sylph '
                              'detected a genome: abundances summed at every '
                              'rank from domain to genome (t__).'},
    name='Add taxonomy to a sylph profile',
    description=(
        'sylph-tax taxprof: joins the taxonomy to each detected genome and '
        'writes a MetaPhlAn-style profile per sample. Samples with no '
        'detected genome get no file; taxprof-to-tables gives them an all-zero '
        'column. A genome missing from the taxonomy is reported under '
        'NO_TAXONOMY.'),
    citations=[citations['Shaw-Yu-2025']],
    examples={'taxprof_gtdb': _taxprof_example},
)

plugin.methods.register_function(
    function=tax_merge,
    inputs={'taxonomic_profiles': SylphTaxProfiles},
    parameters={'column': Str % Choices(MERGE_COLUMNS)},
    outputs=[('merged_profile', SylphMergedProfile)],
    input_descriptions={'taxonomic_profiles': 'sylph-tax taxprof profiles.'},
    parameter_descriptions={
        'column': 'The profile column to merge (sylph-tax merge --column): '
                  'relative_abundance (taxonomic abundance), '
                  'sequence_abundance, ANI or Coverage (genome rows only).'},
    output_descriptions={
        'merged_profile': 'One row per clade (every rank, | separated) and one '
                          'column per sample; clades absent from a sample are '
                          '0.'},
    name='Merge sylph-tax profiles into one table',
    description=('sylph-tax merge: one column of every sample\'s profile side '
                 'by side.' + _EXPERIMENTAL),
    citations=[citations['Shaw-Yu-2025']],
    examples={'tax_merge_relative_abundance': _tax_merge_example},
)

plugin.methods.register_function(
    function=taxprof_to_tables,
    inputs={'taxonomic_profiles': SylphTaxProfiles,
            'sketches': SylphSketches},
    parameters={},
    outputs=[('taxonomic_abundance', FeatureTable[RelativeFrequency]),
             ('sequence_abundance', FeatureTable[RelativeFrequency]),
             ('taxonomy', FeatureData[Taxonomy]),
             ('stats', ImmutableMetadata)],
    input_descriptions={
        'taxonomic_profiles': 'sylph-tax taxprof profiles of a GTDB database '
                              '(seven ranks, d__ to s__, above each genome).',
        'sketches': 'The sketches that were profiled: their sample IDs are '
                    'the table\'s samples, so a sample in which sylph '
                    'detected nothing gets an all-zero column.'},
    output_descriptions={
        'taxonomic_abundance': 'Genome-size-corrected abundance of each '
                               'genome (sylph\'s Taxonomic_abundance), as '
                               'proportions summing to 1 per sample with a '
                               'detection.',
        'sequence_abundance': 'Share of reads assigned to each genome '
                              '(sylph\'s Sequence_abundance), renormalized '
                              'to sum to 1 over the detected genomes.',
        'taxonomy': 'The GTDB taxonomy of every genome in the tables, keyed '
                    'by accession.',
        'stats': 'Per sample: genomes and genera detected, median ANI of the '
                 'detected genomes, and unknown-share, the share of reads '
                 'not assigned to any database genome (meaningful only for a '
                 'profile made with estimate-unknown; 0 otherwise, 1 when '
                 'nothing was detected).'},
    name='Feature tables and taxonomy from sylph-tax profiles',
    description=(
        'Converts sylph-tax taxprof profiles into genome-keyed feature tables '
        '(features are accessions parsed from the t__ genome labels, e.g. '
        'GCF_000023865.1), the matching taxonomy, and per-sample statistics. '
        'Collapse the tables to a rank with taxa collapse and the taxonomy.'
        + _EXPERIMENTAL),
    citations=[citations['Shaw-Yu-2025']],
    examples={'taxprof_to_tables': _taxprof_to_tables_example},
)

plugin.methods.register_function(
    function=query_to_metadata,
    inputs={'query': SylphQuery, 'sylph_taxonomy': SylphTaxonomy},
    parameters={'targets': List[Str]},
    outputs=[('query_metadata', ImmutableMetadata)],
    input_descriptions={
        'query': 'A sylph query result.',
        'sylph_taxonomy': 'sylph-tax taxonomy metadata for the query\'s '
                          'database.'},
    parameter_descriptions={
        'targets': 'Keep only genomes whose taxonomy string or accession '
                   'contains one of these texts (e.g. g__Thermobifida; or '
                   'GCF_001592045.1); all genomes when omitted.'},
    output_descriptions={
        'query_metadata': 'One row per sample and genome, ID '
                          '<sample-id>-<accession>, with columns sample, '
                          'accession, taxonomy, adjusted-ani, '
                          'effective-coverage, ani-5-percentile and '
                          'ani-95-percentile (sylph\'s 5-95 percentile '
                          'interval, missing when sylph reports NA), '
                          'containment-index and naive-ani.'},
    name='Metadata from a sylph query',
    description=(
        'Tabulates sylph query output with the taxonomy joined by accession, '
        'for metadata tabulate or filtering. At effective coverage below '
        'about 0.1x the adjusted ANI and its interval overshoot (the 95th '
        'percentile can exceed 100); read such rows with the containment '
        'index and naive ANI.' + _EXPERIMENTAL),
    citations=[citations['Shaw-Yu-2025']],
    examples={'query_to_metadata_thermobifida': _query_to_metadata_example},
)
