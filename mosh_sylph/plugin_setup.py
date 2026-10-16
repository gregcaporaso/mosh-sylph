# ----------------------------------------------------------------------------
# Copyright (c) 2026, Greg Caporaso.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import Choices, Citations, Plugin, Str

from mosh_sylph import __version__
from mosh_sylph._examples import _fetch_database_example
from mosh_sylph._formats import SylphDatabaseDirFmt, SylphDatabaseFormat
from mosh_sylph._sylph import fetch_database
from mosh_sylph._types import SylphDatabase

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

plugin.register_formats(SylphDatabaseFormat, SylphDatabaseDirFmt)
plugin.register_semantic_types(SylphDatabase)
plugin.register_artifact_class(
    SylphDatabase, SylphDatabaseDirFmt,
    description='A two-stage sylph genome database (.syl2db, sylph >= 1.0.0), '
                'which sylph profile and sylph query search.')

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
