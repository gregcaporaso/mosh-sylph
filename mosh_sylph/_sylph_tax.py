# ----------------------------------------------------------------------------
# Copyright (c) 2026, Greg Caporaso.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

"""sylph-tax commands: taxonomy download, taxprof and merge."""

import os

from mosh_sylph._formats import (SylphMergedProfileFormat, SylphProfileFormat,
                                 SylphTaxonomyFormat, SylphTaxProfilesDirFmt)
from mosh_sylph._util import _download, _run

# The taxonomies sylph-tax knows, as its identifier -> the URL of its metadata
# file. This is a copy of sylph-tax's own table (sylph_tax/metadata_files.py:
# __name_to_metadata_file__ maps identifier -> file name, and
# __metadata_file_urls__ lists the URLs ending in those file names), kept
# here because sylph-tax exposes it only through those dunder names and
# `sylph-tax download` fetches every file at once. Copied from sylph-tax 1.9.2.
# When the pinned sylph-tax changes (environment-files/*-extras.yml), update
# this table to match: tests/test_sylph_tax.py compares it with the installed
# sylph-tax's table and fails on any difference.
TAXONOMIES = {
    'FungiRefSeq-latest':
        'https://zenodo.org/records/17330476/files/'
        'fungi_refseq_2025-10-11_metadata.tsv.gz',
    'FungiRefSeq-2024-07-25':
        'https://zenodo.org/records/14320496/files/'
        'fungi_refseq_2024-07-25_metadata.tsv.gz',
    'GTDB_r214':
        'https://zenodo.org/records/14320496/files/gtdb_r214_metadata.tsv.gz',
    'GTDB_r220':
        'https://zenodo.org/records/14320496/files/gtdb_r220_metadata.tsv.gz',
    'GTDB_r226':
        'https://zenodo.org/records/15314244/files/gtdb_r226_metadata.tsv.gz',
    'GTDB_r232':
        'https://zenodo.org/records/19646381/files/gtdb_r232_metadata.tsv.gz',
    'IMGVR_4.1':
        'https://zenodo.org/records/14320496/files/IMGVR_4.1_metadata.tsv.gz',
    'UHGV_default':
        'https://zenodo.org/records/15670321/files/uhgv_default_metadata.tsv.gz',
    'UHGV_ictv':
        'https://zenodo.org/records/15670321/files/uhgv_ictv_metadata.tsv.gz',
    'OceanDNA':
        'https://zenodo.org/records/14320496/files/ocean_dna_metadata.tsv.gz',
    'SoilSMAG':
        'https://zenodo.org/records/14320496/files/soil_smag_metadata.tsv.gz',
    'TaraEukaryoticSMAG':
        'https://zenodo.org/records/14320496/files/tara_SMAGs_metadata.tsv.gz',
    'GlobDB_r226':
        'https://zenodo.org/records/16322879/files/globdb_r226_sylph_tax.tsv.gz',
    'GlobDB_r232':
        'https://fileshare.lisc.univie.ac.at/globdb/globdb_r232/'
        'globdb_r232_taxonomy.tsv.gz',
}
MERGE_COLUMNS = ['relative_abundance', 'sequence_abundance', 'ANI', 'Coverage']


def _taxonomy_url(taxonomy):
    """sylph-tax's download URL for one of its taxonomy identifiers."""
    return TAXONOMIES[taxonomy]


def tax_download(taxonomy: str) -> SylphTaxonomyFormat:
    """The taxonomy metadata file that sylph-tax download fetches for one of
    its taxonomy identifiers (sylph-tax download fetches all of them)."""
    fmt = SylphTaxonomyFormat()
    _download(_taxonomy_url(taxonomy), str(fmt))
    return fmt


def taxprof(profile: SylphProfileFormat, sylph_taxonomy: SylphTaxonomyFormat
            ) -> SylphTaxProfilesDirFmt:
    """sylph-tax taxprof of a sylph profile with the given taxonomy."""
    path = str(profile)
    with open(path) as fh:
        fh.readline()
        if not fh.readline():
            raise ValueError('sylph profile detected no genome in any sample, '
                             'so sylph-tax taxprof has nothing to annotate')
    result = SylphTaxProfilesDirFmt()
    _run(['sylph-tax', '--no-config', 'taxprof', path,
          '-t', str(sylph_taxonomy),
          '-o', str(result) + os.sep])
    return result


def tax_merge(taxonomic_profiles: SylphTaxProfilesDirFmt,
              column: str = 'relative_abundance') -> SylphMergedProfileFormat:
    # TODO: this is AI-generated code; human review pending
    """sylph-tax merge of the per-sample profiles for one column."""
    paths = sorted(os.path.join(str(taxonomic_profiles), f)
                   for f in os.listdir(str(taxonomic_profiles))
                   if f.endswith('.sylphmpa'))
    result = SylphMergedProfileFormat()
    _run(['sylph-tax', '--no-config', 'merge', *paths, '--column', column,
          '-o', str(result)])
    return result
