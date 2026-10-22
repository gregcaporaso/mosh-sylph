# ----------------------------------------------------------------------------
# Copyright (c) 2026, Greg Caporaso.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

"""Conversions of sylph outputs to stock QIIME 2 types.

profile-to-tables turns sylph profile output into two genome-keyed relative
tables, sylph's own numbers divided by 100: taxonomic abundance (genome-size
corrected, roughly a share of cells; sums to 1 over the detected genomes)
and sequence abundance (share of reads; with sylph profile -u it sums to the
classified share, and the unknown share is reported per sample in the
stats); the genome IDs can take GTDB's prefixed form, so the tables key like
GTDB's taxonomy and trees.
query-to-metadata turns sylph query output into one metadata row per sample
and genome, with a taxonomy joined when given.
"""

import re

import biom
import numpy as np
import pandas as pd
import qiime2

from mosh_sylph._formats import SylphSketchesDirFmt


def _accession(label):
    """t__ label (a genome file name) -> accession, e.g. GCF_000227485.1."""
    name = label.split('/')[-1]
    m = re.match(r'^(GC[AF]_\d+\.\d+)', name)
    return m.group(1) if m else re.sub(r'\.(fa|fna|fasta)(\.gz)?$', '', name)


def _build_tables(per_sample, samples):
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

    def _table(col):
        data = np.zeros((len(features), len(samples)))
        for j, s in enumerate(samples):
            # we divide by 100 here to get from percentages ([0.0-100.0]),
            # which sylph provides, to fractions ([0.0-1.0]), which
            # FeatureTable[RelativeFrequency] uses.
            data[:, j] = (per_sample[s][col].reindex(features).fillna(0.0)
                          .to_numpy() / 100)
        return biom.Table(data, features, samples)

    md = pd.DataFrame(stats).set_index('sample-id')
    return _table('rel'), _table('seq'), md


def _gtdb_id(accession):
    """NCBI assembly accession -> GTDB's prefixed form (RS_ RefSeq, GB_
    GenBank), the genome IDs of GTDB's taxonomy, metadata and trees."""
    if accession.startswith('GCF_'):
        return 'RS_' + accession
    if accession.startswith('GCA_'):
        return 'GB_' + accession
    raise ValueError(f'{accession!r} is not an NCBI assembly accession (GCF_ '
                     'or GCA_), so it has no GTDB form; is the database a GTDB '
                     'one? Turn gtdb_ids off to keep the names as they are')


def _read_profile(df):
    """sylph profile output (its DataFrame view: strings, one row per sample
    and genome) -> {sample: DataFrame indexed by accession with rel, seq,
    ani}."""
    rows = pd.DataFrame({'sample': df['Sample_file'],
                         'accession': df['Genome_file'].map(_accession),
                         'rel': pd.to_numeric(df['Taxonomic_abundance']),
                         'seq': pd.to_numeric(df['Sequence_abundance']),
                         'ani': pd.to_numeric(df['Adjusted_ANI'])})
    per_sample = {}
    for sample, group in rows.groupby('sample', sort=True):
        dup = group['accession'][group['accession'].duplicated()]
        if len(dup):
            # Two sketch files carrying the same sample name profile as one
            # sample; set_index below would accept the duplicates and the
            # reindex in _build_tables would fail on them later, unclearly.
            raise ValueError(f'the profile lists genome {dup.iloc[0]} twice '
                             f'for sample {sample}')
        per_sample[sample] = group.set_index('accession')[['rel', 'seq', 'ani']]
    return per_sample


def profile_to_tables(profile: pd.DataFrame,
                      sketches: SylphSketchesDirFmt, gtdb_ids: bool = True
                      ) -> (biom.Table, biom.Table, qiime2.Metadata):
    """sylph profile output -> genome-keyed tables and per-sample statistics,
    without a taxonomy; the sketches give the full sample list."""
    per_sample = _read_profile(profile)
    if gtdb_ids:
        per_sample = {s: df.rename(index=_gtdb_id) for s, df in per_sample.items()}
    rel, seq, stats = _build_tables(per_sample, sorted(sketches.sample_paths()))
    return rel, seq, qiime2.Metadata(stats)


def _query_to_metadata(df, taxonomy=None, gtdb_ids=True, targets=None):
    """sylph query output (its DataFrame view) -> one row per sample and
    genome, ID '<sample>-<genome>' (sample-id is reserved for the ID header),
    the taxonomy joined by genome ID when given, and the 5-95 percentile
    interval split into two numeric columns (NA -> missing). `targets`: keep
    only rows whose taxonomy string or genome ID contains one."""
    if df.empty:
        raise ValueError('sylph query reported no genome with enough sampled '
                         'k-mers in any sample')
    genomes = df['Genome_file'].map(_accession)
    if gtdb_ids:
        genomes = genomes.map(_gtdb_id)
    out = pd.DataFrame({'sample': df['Sample_file'], 'genome': genomes})
    out['taxonomy'] = (out['genome'].map(taxonomy) if taxonomy is not None
                       else pd.Series([None] * len(out), index=out.index,
                                      dtype=object))
    out['adjusted-ani'] = pd.to_numeric(df['Adjusted_ANI'])
    out['effective-coverage'] = pd.to_numeric(df['Eff_cov'])
    interval = df['ANI_5-95_percentile'].str.split('-', n=1, expand=True)
    out['ani-5-percentile'] = pd.to_numeric(interval[0], errors='coerce')
    out['ani-95-percentile'] = pd.to_numeric(interval[1], errors='coerce')
    out['containment-index'] = df['Containment_ind']
    out['naive-ani'] = pd.to_numeric(df['Naive_ANI'])
    if targets:
        lineage = out['taxonomy'].fillna('') + ' ' + out['genome']
        out = out[lineage.apply(lambda s: any(t in s for t in targets))]
        if out.empty:
            raise ValueError(f'no reported genome matches the targets {targets}')
    out = out.sort_values(['sample', 'genome'])
    out.index = pd.Index(out['sample'] + '-' + out['genome'], name='id')
    return qiime2.Metadata(out)


def query_to_metadata(query: pd.DataFrame, taxonomy: pd.Series = None,
                      gtdb_ids: bool = True, targets: list = None
                      ) -> qiime2.Metadata:
    """sylph query output as metadata, with a taxonomy joined when given."""
    return _query_to_metadata(query, taxonomy, gtdb_ids, targets)
