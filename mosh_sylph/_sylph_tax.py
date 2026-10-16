# ----------------------------------------------------------------------------
# Copyright (c) 2026, Greg Caporaso.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

"""sylph-tax commands: taxonomy download, taxprof and merge."""

import os

from sylph_tax.metadata_files import (__metadata_file_urls__,
                                      __name_to_metadata_file__)

from mosh_sylph._formats import (SylphProfileDirFmt, SylphTaxonomyDirFmt,
                                 SylphTaxProfilesDirFmt)
from mosh_sylph._util import _download, _run

TAXONOMIES = list(__name_to_metadata_file__)


def _taxonomy_url(taxonomy):
    # TODO: this is AI-generated code; human review pending
    """sylph-tax's download URL for one of its taxonomy identifiers."""
    name = __name_to_metadata_file__[taxonomy]
    return next(u for u in __metadata_file_urls__ if u.endswith('/' + name))


def tax_download(taxonomy: str) -> SylphTaxonomyDirFmt:
    # TODO: this is AI-generated code; human review pending
    """The taxonomy metadata file that sylph-tax download fetches for one of
    its taxonomy identifiers (sylph-tax download fetches all of them)."""
    fmt = SylphTaxonomyDirFmt()
    _download(_taxonomy_url(taxonomy), os.path.join(str(fmt), 'taxonomy.tsv.gz'))
    return fmt


def taxprof(profile: SylphProfileDirFmt, sylph_taxonomy: SylphTaxonomyDirFmt
            ) -> SylphTaxProfilesDirFmt:
    # TODO: this is AI-generated code; human review pending
    """sylph-tax taxprof of a sylph profile with the given taxonomy."""
    path = os.path.join(str(profile), 'profile.tsv')
    with open(path) as fh:
        if sum(1 for _ in fh) < 2:
            raise ValueError('sylph profile detected no genome in any sample, '
                             'so sylph-tax taxprof has nothing to annotate')
    result = SylphTaxProfilesDirFmt()
    _run(['sylph-tax', '--no-config', 'taxprof', path,
          '-t', os.path.join(str(sylph_taxonomy), 'taxonomy.tsv.gz'),
          '-o', str(result) + os.sep])
    return result
