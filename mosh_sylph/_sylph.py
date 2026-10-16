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

from mosh_sylph._formats import (SylphDatabaseDirFmt, SylphProfileDirFmt,
                                 SylphQueryDirFmt, SylphSketchesDirFmt)
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


def _search_options(threads, minimum_ani, min_number_kmers, min_contain,
                    min_count_correct, screen_ani):
    # TODO: this is AI-generated code; human review pending
    """The options sylph profile and sylph query share."""
    return ['-t', str(threads), '--minimum-ani', str(minimum_ani),
            '--min-number-kmers', str(min_number_kmers),
            '--min-contain', str(min_contain),
            '--min-count-correct', str(min_count_correct),
            '--screen-ani', str(screen_ani)]


def profile(sketches: SylphSketchesDirFmt, database: SylphDatabaseDirFmt,
            threads: int = 3, minimum_ani: float = 95.0,
            min_number_kmers: int = 10, min_contain: int = 7,
            min_count_correct: float = 3.0, estimate_unknown: bool = False,
            read_seq_id: float = None, screen_ani: float = 85.0
            ) -> SylphProfileDirFmt:
    # TODO: this is AI-generated code; human review pending
    """sylph profile of every sketch against the database."""
    result = SylphProfileDirFmt()
    _run(['sylph', 'profile']
         + _search_options(threads, minimum_ani, min_number_kmers, min_contain,
                           min_count_correct, screen_ani)
         + (['--estimate-unknown'] if estimate_unknown else [])
         + (['--read-seq-id', str(read_seq_id)] if read_seq_id is not None
            else [])
         + ['-d', os.path.join(str(database), 'database.syl2db'),
            '-o', os.path.join(str(result), 'profile.tsv')]
         + list(sketches.sample_paths().values()))
    return result


def query(sketches: SylphSketchesDirFmt, database: SylphDatabaseDirFmt,
          threads: int = 3, minimum_ani: float = 90.0,
          min_number_kmers: int = 10, min_contain: int = 7,
          min_count_correct: float = 3.0, screen_ani: float = 85.0
          ) -> SylphQueryDirFmt:
    # TODO: this is AI-generated code; human review pending
    """sylph query of every sketch against the database."""
    result = SylphQueryDirFmt()
    _run(['sylph', 'query']
         + _search_options(threads, minimum_ani, min_number_kmers, min_contain,
                           min_count_correct, screen_ani)
         + ['-d', os.path.join(str(database), 'database.syl2db'),
            '-o', os.path.join(str(result), 'query.tsv')]
         + list(sketches.sample_paths().values()))
    return result
