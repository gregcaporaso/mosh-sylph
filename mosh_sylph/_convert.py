# ----------------------------------------------------------------------------
# Copyright (c) 2026, Greg Caporaso.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

"""Conversions of sylph and sylph-tax outputs to stock QIIME 2 types.

profile-to-tables turns sylph profile output into two genome-keyed relative
tables: taxonomic abundance (genome-size corrected, roughly a share of cells)
and sequence abundance (share of reads, renormalized over the detected
genomes, so the unknown share that sylph profile -u estimates is reported per
sample instead of as a missing remainder); the genome IDs can take GTDB's
prefixed form, so the tables key like GTDB's taxonomy and trees.
taxprof-to-tables does the same from sylph-tax's per-sample .sylphmpa
profiles and adds the genome-keyed taxonomy. query-to-metadata turns sylph
query output into one metadata row per sample and genome with the taxonomy
joined.
"""

import csv
import os
import re

import biom
import numpy as np
import pandas as pd
import qiime2

from mosh_sylph._formats import (SylphProfileFormat, SylphQueryFormat,
                                 SylphSketchesDirFmt,
                                 SylphTaxonomyFormat, SylphTaxProfilesDirFmt)

RANKS = ('d__', 'p__', 'c__', 'o__', 'f__', 'g__', 's__')


def _accession(label):
    # TODO: this is AI-generated code; human review pending
    """t__ label (a genome file name) -> accession, e.g. GCF_000227485.1."""
    name = label.split('/')[-1]
    m = re.match(r'^(GC[AF]_\d+\.\d+)', name)
    return m.group(1) if m else re.sub(r'\.(fa|fna|fasta)(\.gz)?$', '', name)


def _read_sylphmpa(path):
    # TODO: this is AI-generated code; human review pending
    """-> (sample id, DataFrame indexed by accession: Taxon, rel, seq, ani)."""
    with open(path) as fh:
        header = fh.readline()
    if not header.startswith('#SampleID'):
        raise ValueError(f'{path}: not a .sylphmpa file')
    sample = header.split('\t')[1].strip()
    df = pd.read_csv(path, sep='\t', comment='#', header=0,
                     quoting=csv.QUOTE_NONE)
    df.columns = [c.split(' ')[0] for c in df.columns]   # 'ANI (if ...)' -> 'ANI'
    rows = {}
    for clade, rel, seq, ani in zip(df['clade_name'], df['relative_abundance'],
                                    df['sequence_abundance'], df['ANI']):
        *ranks, strain = clade.split('|')
        if not strain.startswith('t__'):
            continue
        if ranks == ['NO_TAXONOMY']:
            raise ValueError(f'{path}: genome {strain[3:]} has no entry in the '
                             'sylph-tax taxonomy (database and taxonomy differ)')
        if len(ranks) != 7 or any(not r.startswith(p) for r, p in zip(ranks, RANKS)):
            raise ValueError(f'{path}: expected the seven GTDB ranks d__ to s__ '
                             f'above the genome, found {clade!r}; '
                             'taxprof-to-tables handles GTDB taxonomies only')
        acc = _accession(strain[3:])
        if acc in rows:
            raise ValueError(f'{path}: accession {acc} appears twice')
        rows[acc] = {'Taxon': ';'.join(ranks), 'rel': float(rel),
                     'seq': float(seq), 'ani': float(ani)}
    return sample, pd.DataFrame.from_dict(rows, orient='index')


def _build_tables(per_sample, samples):
    # TODO: this is AI-generated code; human review pending
    """{sample: DataFrame indexed by genome with rel, seq, ani (percentages)}
    -> (taxonomic table, sequence table, per-sample stats DataFrame).

    `samples` is the full sample list: a sample with no detection (so no
    rows in sylph's output) gets an all-zero column and an unknown share of
    1. The stats are genomes, median-ani and unknown-share, indexed by
    sample-id in the order of `samples`.
    """
    extra = sorted(set(per_sample) - set(samples))
    if extra:
        raise ValueError(f'sample {extra[0]} has a profile but no sketch')
    stats = []
    for sample in samples:
        df = per_sample.get(sample)
        if df is None:
            df = per_sample[sample] = pd.DataFrame(columns=['rel', 'seq', 'ani'])
        stats.append({'sample-id': sample, 'genomes': len(df),
                      'median-ani': df['ani'].median() if len(df) else np.nan,
                      # sylph's four-decimal percentages can sum to 100.0001
                      # without -u: no negative share
                      'unknown-share': min(1.0, max(
                          0.0, round(1 - df['seq'].sum() / 100, 6)))})
    features = sorted({f for df in per_sample.values() for f in df.index})

    def _table(col, renormalize):
        # TODO: this is AI-generated code; human review pending
        data = np.zeros((len(features), len(samples)))
        for j, s in enumerate(samples):
            v = per_sample[s][col].reindex(features).fillna(0.0).to_numpy() / 100
            if renormalize and v.sum() > 0:
                v = v / v.sum()
            data[:, j] = v
        return biom.Table(data, features, samples)

    md = pd.DataFrame(stats).set_index('sample-id')
    return _table('rel', False), _table('seq', True), md


def _tables(paths, samples):
    # TODO: this is AI-generated code; human review pending
    """-> (taxonomic table, sequence table, taxonomy Series, per-sample stats).

    `samples` is the full sample list: a sample with no profile (sylph
    detected nothing, so sylph-tax wrote no file) gets an all-zero column and
    an unknown share of 1. The stats add `genera` to those of _build_tables.
    """
    per_sample, taxonomy, genera = {}, {}, {}
    for path in sorted(paths):
        sample, df = _read_sylphmpa(path)
        if sample in per_sample:
            raise ValueError(f'sample {sample} appears twice')
        per_sample[sample] = df
        for acc, taxon in df['Taxon'].items():
            if taxonomy.setdefault(acc, taxon) != taxon:
                raise ValueError(f'{acc}: two taxonomy strings across samples')
        genera[sample] = df['Taxon'].str.split(';').str[5].nunique()
    rel, seq, md = _build_tables(per_sample, sorted(samples))
    md.insert(1, 'genera', [genera.get(s, 0) for s in md.index])
    tax = pd.Series(taxonomy, name='Taxon').reindex(rel.ids(axis='observation'))
    tax.index.name = 'Feature ID'
    return rel, seq, tax, md


def _gtdb_id(accession):
    # TODO: this is AI-generated code; human review pending
    """NCBI assembly accession -> GTDB's prefixed form (RS_ RefSeq, GB_
    GenBank), the genome IDs of GTDB's taxonomy, metadata and trees."""
    if accession.startswith('GCF_'):
        return 'RS_' + accession
    if accession.startswith('GCA_'):
        return 'GB_' + accession
    raise ValueError(f'{accession!r} is not an NCBI assembly accession (GCF_ '
                     'or GCA_), so it has no GTDB form; is the database a GTDB '
                     'one? Turn gtdb_ids off to keep the names as they are')


def _read_profile(path):
    # TODO: this is AI-generated code; human review pending
    """sylph profile output -> {sample: DataFrame indexed by accession with
    rel, seq, ani}. Read as sylph-tax reads it: no quoting, only the
    header's columns (a tab in a contig name adds fields to its row)."""
    with open(path) as fh:
        columns = fh.readline().rstrip('\n').split('\t')
    df = pd.read_csv(path, sep='\t', dtype=str, quoting=csv.QUOTE_NONE,
                     usecols=range(len(columns)))
    rows = pd.DataFrame({'sample': df['Sample_file'],
                         'accession': df['Genome_file'].map(_accession),
                         'rel': pd.to_numeric(df['Taxonomic_abundance']),
                         'seq': pd.to_numeric(df['Sequence_abundance']),
                         'ani': pd.to_numeric(df['Adjusted_ANI'])})
    per_sample = {}
    for sample, group in rows.groupby('sample', sort=True):
        dup = group['accession'][group['accession'].duplicated()]
        if len(dup):
            raise ValueError(f'{path}: {dup.iloc[0]} appears twice in sample '
                             f'{sample}')
        per_sample[sample] = group.set_index('accession')[['rel', 'seq', 'ani']]
    return per_sample


def profile_to_tables(profile: SylphProfileFormat,
                      sketches: SylphSketchesDirFmt, gtdb_ids: bool = True
                      ) -> (biom.Table, biom.Table, qiime2.Metadata):
    # TODO: this is AI-generated code; human review pending
    """sylph profile output -> genome-keyed tables and per-sample statistics,
    without a taxonomy; the sketches give the full sample list."""
    per_sample = _read_profile(str(profile))
    if gtdb_ids:
        per_sample = {s: df.rename(index=_gtdb_id) for s, df in per_sample.items()}
    rel, seq, stats = _build_tables(per_sample, sorted(sketches.sample_paths()))
    return rel, seq, qiime2.Metadata(stats)


def taxprof_to_tables(taxonomic_profiles: SylphTaxProfilesDirFmt,
                      sketches: SylphSketchesDirFmt
                      ) -> (biom.Table, biom.Table, pd.Series, qiime2.Metadata):
    # TODO: this is AI-generated code; human review pending
    """sylph-tax .sylphmpa profiles -> genome-keyed tables, taxonomy and
    per-sample statistics; the sketches give the full sample list."""
    paths = [os.path.join(str(taxonomic_profiles), f)
             for f in os.listdir(str(taxonomic_profiles))
             if f.endswith('.sylphmpa')]
    rel, seq, tax, stats = _tables(paths, sorted(sketches.sample_paths()))
    return rel, seq, tax, qiime2.Metadata(stats)


def _read_taxonomy(sylph_taxonomy):
    # TODO: this is AI-generated code; human review pending
    """{accession: taxonomy string} from sylph-tax taxonomy metadata."""
    df = pd.read_csv(str(sylph_taxonomy), sep='\t', header=None,
                     usecols=[0, 1], dtype=str,
                     quoting=csv.QUOTE_NONE)
    return df.set_index(0)[1].to_dict()


def _query_to_metadata(path, taxonomy, targets=None):
    # TODO: this is AI-generated code; human review pending
    """sylph query output -> one row per sample and genome, ID
    '<sample>-<accession>' (sample-id is reserved for the ID header), the
    taxonomy joined by accession, and the 5-95 percentile interval split into
    two numeric columns (NA -> missing). `targets`: keep only rows whose
    taxonomy or accession contains one. Read as sylph-tax reads sylph output:
    no quoting, and only the header's columns, because a tab inside a genome's
    first contig name adds fields to its Contig_name rows."""
    with open(path) as fh:
        columns = fh.readline().rstrip('\n').split('\t')
    df = pd.read_csv(path, sep='\t', dtype=str, quoting=csv.QUOTE_NONE,
                     usecols=range(len(columns)))
    if df.empty:
        raise ValueError('sylph query reported no genome with enough sampled '
                         'k-mers in any sample')
    out = pd.DataFrame({'sample': df['Sample_file'],
                        'accession': df['Genome_file'].map(_accession)})
    out['taxonomy'] = out['accession'].map(taxonomy)
    out['adjusted-ani'] = pd.to_numeric(df['Adjusted_ANI'])
    out['effective-coverage'] = pd.to_numeric(df['Eff_cov'])
    interval = df['ANI_5-95_percentile'].str.split('-', n=1, expand=True)
    out['ani-5-percentile'] = pd.to_numeric(interval[0], errors='coerce')
    out['ani-95-percentile'] = pd.to_numeric(interval[1], errors='coerce')
    out['containment-index'] = df['Containment_ind']
    out['naive-ani'] = pd.to_numeric(df['Naive_ANI'])
    if targets:
        lineage = out['taxonomy'].fillna('') + ' ' + out['accession']
        out = out[lineage.apply(lambda s: any(t in s for t in targets))]
        if out.empty:
            raise ValueError(f'no reported genome matches the targets {targets}')
    out = out.sort_values(['sample', 'accession'])
    out.index = pd.Index(out['sample'] + '-' + out['accession'], name='id')
    return qiime2.Metadata(out)


def query_to_metadata(query: SylphQueryFormat,
                      sylph_taxonomy: SylphTaxonomyFormat,
                      targets: list = None) -> qiime2.Metadata:
    # TODO: this is AI-generated code; human review pending
    """sylph query output with the taxonomy joined, as metadata."""
    return _query_to_metadata(str(query), _read_taxonomy(sylph_taxonomy),
                              targets)
