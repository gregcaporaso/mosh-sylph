# ----------------------------------------------------------------------------
# Copyright (c) 2026, Greg Caporaso.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

"""File formats: each holds a sylph or sylph-tax file exactly as the tool
reads or writes it."""

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
