# ----------------------------------------------------------------------------
# Copyright (c) 2026, Greg Caporaso.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

"""File formats: each holds a sylph file exactly as sylph reads or writes
it; the two TSV outputs also view as a pandas DataFrame of strings."""

import csv
import os
import subprocess
import tempfile

import pandas as pd
from qiime2.plugin import model


_INSPECT_SUFFIX = {'database': '.syl2db', 'sketch': '.sylsp'}


def _inspect(path, what):
    """Raise ValidationError unless the installed sylph can read the file as
    a `what` (database or sketch): `sylph inspect`, which picks its parser by
    file extension and skips any other extension with a warning and exit
    status 0, so the file is inspected through a symlink with the right
    extension, and an empty report counts as a failure. The YAML report is
    discarded; on the 20 GB GTDB r232 two-stage database this takes 9 s and
    4.2 GB of memory (it reads the stage-one screen sketches, not the whole
    file; measured on bacon, 2026-10-22). The error carries the last line
    sylph printed."""
    with tempfile.TemporaryDirectory() as work:
        link = os.path.join(work, what + _INSPECT_SUFFIX[what])
        os.symlink(os.path.abspath(path), link)
        report = os.path.join(work, 'report.yaml')
        run = subprocess.run(['sylph', 'inspect', link, '-o', report],
                             stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                             text=True)
        failed = run.returncode != 0 or os.path.getsize(report) == 0
    if failed:
        said = [line for line in run.stderr.splitlines()
                if line and not line.startswith('note:')]
        raise model.ValidationError(
            f'sylph inspect cannot read this {what}: '
            + (said[-1] if said else f'exit status {run.returncode}'))


class SylphTwoStageDatabaseFormat(model.BinaryFileFormat):
    """A two-stage sylph genome database (.syl2db, sylph >= 1.0.0): the SY2D
    magic, then `sylph inspect` at every level, so that a download
    (fetch-database's output is validated at min) is checked as soon as it
    lands."""

    def _validate_(self, level):
        with open(str(self), 'rb') as fh:
            if fh.read(4) != b'SY2D':
                raise model.ValidationError(
                    'not a two-stage sylph database (.syl2db)')
        _inspect(str(self), 'database')


SylphTwoStageDatabaseDirFmt = model.SingleFileDirectoryFormat(
    'SylphTwoStageDatabaseDirFmt', 'database.syl2db', SylphTwoStageDatabaseFormat)


class SylphSketchFormat(model.BinaryFileFormat):
    """One sample's read sketch (.sylsp), as sylph sketch writes it. The file
    has no header to recognize it by, so at level max `sylph inspect` decides
    whether the installed sylph can read it; at level min (action outputs,
    which sylph itself wrote) only an empty file is rejected."""

    def _validate_(self, level):
        if os.path.getsize(str(self)) == 0:
            raise model.ValidationError('empty sylph sketch')
        if level == 'max':
            _inspect(str(self), 'sketch')


class SylphSketchesDirFmt(model.DirectoryFormat):
    """Per-sample read sketches named <sample-id>.paired.sylsp, as sylph
    sketch names paired-end sketches given sample names with --lS."""
    sketches = model.FileCollection(r'.+\.paired\.sylsp$',
                                    format=SylphSketchFormat)

    @sketches.set_path_maker
    def _sketch_path(self, sample_id):
        return f'{sample_id}.paired.sylsp'

    def sample_paths(self):
        """{sample id: sketch path}, sorted by sample id."""
        suffix = '.paired.sylsp'
        return {f[:-len(suffix)]: os.path.join(str(self), f)
                for f in sorted(os.listdir(str(self))) if f.endswith(suffix)}


class _SylphTSVFormat(model.TextFileFormat):
    """A sylph TSV: its header starts with HEADER."""
    HEADER = ()

    def _validate_(self, level):
        with open(str(self)) as fh:
            columns = fh.readline().rstrip('\n').split('\t')
        if tuple(columns[:len(self.HEADER)]) != self.HEADER:
            raise model.ValidationError(
                f'expected a header starting with {self.HEADER}, found '
                f'{tuple(columns)}')


class SylphProfileFormat(_SylphTSVFormat):
    """sylph profile output: one row per sample and detected genome."""
    HEADER = ('Sample_file', 'Genome_file', 'Taxonomic_abundance',
              'Sequence_abundance', 'Adjusted_ANI')


SylphProfileDirFmt = model.SingleFileDirectoryFormat(
    'SylphProfileDirFmt', 'profile.tsv', SylphProfileFormat)


class SylphQueryFormat(_SylphTSVFormat):
    """sylph query output: one row per sample and genome with enough k-mers."""
    HEADER = ('Sample_file', 'Genome_file', 'Adjusted_ANI', 'Eff_cov')


SylphQueryDirFmt = model.SingleFileDirectoryFormat(
    'SylphQueryDirFmt', 'query.tsv', SylphQueryFormat)


def _read_sylph_tsv(path):
    # TODO: this is AI-generated code; human review pending
    """A sylph TSV as a DataFrame of strings, read as sylph-tax reads sylph
    output: no quoting, and only the header's columns, because a tab inside
    a genome's first contig name adds fields to its Contig_name rows."""
    with open(path) as fh:
        columns = fh.readline().rstrip('\n').split('\t')
    return pd.read_csv(path, sep='\t', dtype=str, quoting=csv.QUOTE_NONE,
                       usecols=range(len(columns)))


def _profile_to_dataframe(ff: SylphProfileFormat) -> pd.DataFrame:
    # TODO: this is AI-generated code; human review pending
    return _read_sylph_tsv(str(ff))


def _query_to_dataframe(ff: SylphQueryFormat) -> pd.DataFrame:
    # TODO: this is AI-generated code; human review pending
    return _read_sylph_tsv(str(ff))
