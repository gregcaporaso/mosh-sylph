# ----------------------------------------------------------------------------
# Copyright (c) 2026, Greg Caporaso.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

"""sylph commands: database download, sketch, profile and query."""

import os

from mosh_sylph._formats import SylphDatabaseDirFmt
from mosh_sylph._util import _download

DEFAULT_BASE_URL = 'http://faust.compbio.cs.cmu.edu/sylph-stuff'


def _database_url(base_url, release):
    # TODO: this is AI-generated code; human review pending
    """The authors' file name for the two-stage GTDB database of a release."""
    return f'{base_url.rstrip("/")}/gtdb-r{release}-c200-dbv2.syl2db'


def fetch_database(release: str,
                   base_url: str = DEFAULT_BASE_URL) -> SylphDatabaseDirFmt:
    # TODO: this is AI-generated code; human review pending
    """Download the sylph authors' pre-built GTDB database of a release."""
    fmt = SylphDatabaseDirFmt()
    _download(_database_url(base_url, release),
              os.path.join(str(fmt), 'database.syl2db'))
    return fmt
