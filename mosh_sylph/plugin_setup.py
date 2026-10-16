# ----------------------------------------------------------------------------
# Copyright (c) 2026, Greg Caporaso.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import Citations, Plugin

from mosh_sylph import __version__

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
