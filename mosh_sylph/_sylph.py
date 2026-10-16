# ----------------------------------------------------------------------------
# Copyright (c) 2026, Greg Caporaso.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

"""sylph commands: database download, sketch, profile and query."""

import os
import tempfile

import pandas as pd
from q2_types.per_sample_sequences import SingleLanePerSamplePairedEndFastqDirFmt

from mosh_sylph._formats import SylphDatabaseDirFmt, SylphSketchesDirFmt
from mosh_sylph._util import _download, _run

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


def sketch(reads: SingleLanePerSamplePairedEndFastqDirFmt, threads: int = 3,
           c: int = 200, k: int = 31, fpr: float = 0.0001
           ) -> SylphSketchesDirFmt:
    # TODO: this is AI-generated code; human review pending
    """sylph sketch of every sample's read pairs, named by sample ID."""
    manifest = reads.manifest.view(pd.DataFrame)
    samples = list(manifest.index)
    sketches = SylphSketchesDirFmt()
    with tempfile.TemporaryDirectory() as work:
        lists = {}
        for name, column in [('l1', manifest['forward']),
                             ('l2', manifest['reverse']),
                             ('names', pd.Series(samples, index=samples))]:
            lists[name] = os.path.join(work, name + '.txt')
            with open(lists[name], 'w') as fh:
                fh.write('\n'.join(column.loc[samples]) + '\n')
        _run(['sylph', 'sketch', '-t', str(threads), '-c', str(c), '-k', str(k),
              '--fpr', str(fpr), '--l1', lists['l1'], '--l2', lists['l2'],
              '--lS', lists['names'], '-d', str(sketches)])
    return sketches
