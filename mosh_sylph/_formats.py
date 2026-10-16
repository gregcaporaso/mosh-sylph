# ----------------------------------------------------------------------------
# Copyright (c) 2026, Greg Caporaso.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

"""File formats: each holds a sylph or sylph-tax file exactly as the tool
reads or writes it."""

import gzip
import os

from qiime2.plugin import model


class SylphDatabaseFormat(model.BinaryFileFormat):
    """A two-stage sylph genome database (.syl2db, sylph >= 1.0.0)."""

    def _validate_(self, level):
        # TODO: this is AI-generated code; human review pending
        with open(str(self), 'rb') as fh:
            if fh.read(4) != b'SY2D':
                raise model.ValidationError(
                    'not a two-stage sylph database (.syl2db)')


SylphDatabaseDirFmt = model.SingleFileDirectoryFormat(
    'SylphDatabaseDirFmt', 'database.syl2db', SylphDatabaseFormat)


class SylphTaxonomyFormat(model.BinaryFileFormat):
    """sylph-tax taxonomy metadata: gzipped, tab-separated, one genome per
    line (accession or genome file name, ;-separated taxonomy string, and an
    optional third column such as a virus host)."""

    def _validate_(self, level):
        # TODO: this is AI-generated code; human review pending
        lines = {'min': 10, 'max': None}[level]
        try:
            with gzip.open(str(self), 'rt') as fh:
                for i, line in enumerate(fh):
                    if lines is not None and i >= lines:
                        break
                    if len(line.rstrip('\n').split('\t')) < 2:
                        raise model.ValidationError(
                            f'line {i + 1}: expected an accession and a '
                            'taxonomy string separated by a tab')
        except (OSError, EOFError) as e:
            raise model.ValidationError(f'not gzipped: {e}')


SylphTaxonomyDirFmt = model.SingleFileDirectoryFormat(
    'SylphTaxonomyDirFmt', 'taxonomy.tsv.gz', SylphTaxonomyFormat)


class SylphSketchFormat(model.BinaryFileFormat):
    """One sample's read sketch (.sylsp), as sylph sketch writes it."""

    def _validate_(self, level):
        # TODO: this is AI-generated code; human review pending
        if os.path.getsize(str(self)) == 0:
            raise model.ValidationError('empty sylph sketch')


class SylphSketchesDirFmt(model.DirectoryFormat):
    """Per-sample read sketches named <sample-id>.paired.sylsp, as sylph
    sketch names paired-end sketches given sample names with --lS."""
    sketches = model.FileCollection(r'.+\.paired\.sylsp$',
                                    format=SylphSketchFormat)

    @sketches.set_path_maker
    def _sketch_path(self, sample_id):
        # TODO: this is AI-generated code; human review pending
        return f'{sample_id}.paired.sylsp'

    def sample_paths(self):
        # TODO: this is AI-generated code; human review pending
        """{sample id: sketch path}, sorted by sample id."""
        suffix = '.paired.sylsp'
        return {f[:-len(suffix)]: os.path.join(str(self), f)
                for f in sorted(os.listdir(str(self))) if f.endswith(suffix)}
