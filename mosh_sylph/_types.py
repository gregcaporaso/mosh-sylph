# ----------------------------------------------------------------------------
# Copyright (c) 2026, Greg Caporaso.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

"""Semantic types: one per kind of file sylph reads or writes."""

from qiime2.plugin import SemanticType

SylphTwoStageDatabase = SemanticType('SylphTwoStageDatabase')
SylphSketches = SemanticType('SylphSketches')
SylphProfile = SemanticType('SylphProfile')
SylphQuery = SemanticType('SylphQuery')
