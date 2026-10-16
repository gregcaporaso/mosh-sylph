# ----------------------------------------------------------------------------
# Copyright (c) 2026, Greg Caporaso.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import (Bool, Choices, Citations, Float, Int, Plugin, Range,
                           Str)
from q2_types.per_sample_sequences import PairedEndSequencesWithQuality
from q2_types.sample_data import SampleData

from mosh_sylph import __version__
from mosh_sylph._examples import (_fetch_database_example, _profile_example,
                                  _sketch_example, _tax_download_example)
from mosh_sylph._formats import (SylphDatabaseDirFmt, SylphDatabaseFormat,
                                 SylphProfileDirFmt, SylphProfileFormat,
                                 SylphSketchesDirFmt, SylphSketchFormat,
                                 SylphTaxonomyDirFmt, SylphTaxonomyFormat)
from mosh_sylph._sylph import fetch_database, profile, sketch
from mosh_sylph._sylph_tax import TAXONOMIES, tax_download
from mosh_sylph._types import (SylphDatabase, SylphProfile, SylphSketches,
                               SylphTaxonomy)

citations = Citations.load("citations.bib", package="mosh_sylph")

plugin = Plugin(
    name="sylph",
    version=__version__,
    website="https://github.com/gregcaporaso/mosh-sylph",
    package="mosh_sylph",
    description=("Thin wrappers of the sylph metagenome profiler and sylph-tax: "
                 "one action per command, each returning the tool's own output "
                 "as an artifact, and conversions of those outputs to feature "
                 "tables, taxonomies and metadata."),
    short_description="sylph metagenome profiling and sylph-tax taxonomy.",
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
                        SylphProfileFormat, SylphProfileDirFmt)
plugin.register_semantic_types(SylphDatabase, SylphTaxonomy, SylphSketches,
                               SylphProfile)
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

plugin.methods.register_function(
    function=fetch_database,
    inputs={},
    parameters={'release': Str % Choices(['226', '232']),
                'base_url': Str},
    outputs=[('database', SylphDatabase)],
    parameter_descriptions={
        'release': 'GTDB release. The authors build two-stage databases for '
                   'r226 and r232 only.',
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
        'species representatives for one release (14 GB for r226, 19 GB for '
        'r232). Reads must be sketched with the same c (200) and k (31).'
        + _EXPERIMENTAL),
    citations=[citations['Shaw-Yu-2025']],
    examples={'fetch_database_r232': _fetch_database_example},
)

plugin.methods.register_function(
    function=tax_download,
    inputs={},
    parameters={'taxonomy': Str % Choices(TAXONOMIES)},
    outputs=[('sylph_taxonomy', SylphTaxonomy)],
    parameter_descriptions={
        'taxonomy': 'sylph-tax\'s identifier of the taxonomy; GTDB_r226 and '
                    'GTDB_r232 match the databases fetch-database downloads.'},
    output_descriptions={
        'sylph_taxonomy': 'The taxonomy metadata file, as sylph-tax download '
                          'stores it.'},
    name='Download sylph-tax taxonomy metadata',
    description=(
        'Downloads the taxonomy metadata file that sylph-tax download fetches '
        'for one taxonomy identifier, from the URL sylph-tax lists for it '
        '(sylph-tax download itself fetches every taxonomy at once).'
        + _EXPERIMENTAL),
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
