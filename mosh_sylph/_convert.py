# ----------------------------------------------------------------------------
# Copyright (c) 2026, Greg Caporaso.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

"""Conversions of sylph and sylph-tax outputs to stock QIIME 2 types.

taxprof-to-tables turns sylph-tax's per-sample .sylphmpa profiles into a
genome-keyed taxonomy and two relative tables: taxonomic abundance (genome-size
corrected, roughly a share of cells) and sequence abundance (share of reads,
renormalized over the detected genomes, so the unknown share that sylph
profile -u estimates is reported per sample instead of as a missing remainder).
"""

import os
import re

import biom
import numpy as np
import pandas as pd
import qiime2

from mosh_sylph._formats import SylphSketchesDirFmt, SylphTaxProfilesDirFmt

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
    df = pd.read_csv(path, sep='\t', comment='#', header=0)
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
            raise ValueError(f'{path}: unexpected clade string {clade!r}')
        acc = _accession(strain[3:])
        if acc in rows:
            raise ValueError(f'{path}: accession {acc} appears twice')
        rows[acc] = {'Taxon': ';'.join(ranks), 'rel': float(rel),
                     'seq': float(seq), 'ani': float(ani)}
    return sample, pd.DataFrame.from_dict(rows, orient='index')


def _tables(paths, samples):
    # TODO: this is AI-generated code; human review pending
    """-> (taxonomic table, sequence table, taxonomy Series, per-sample stats).

    `samples` is the full sample list: a sample with no profile (sylph
    detected nothing, so sylph-tax wrote no file) gets an all-zero column and
    an unknown share of 1.
    """
    per_sample, taxonomy, stats = {}, {}, []
    for path in sorted(paths):
        sample, df = _read_sylphmpa(path)
        if sample in per_sample:
            raise ValueError(f'sample {sample} appears twice')
        if sample not in samples:
            raise ValueError(f'sample {sample} has a profile but no sketch')
        per_sample[sample] = df
        for acc, taxon in df['Taxon'].items():
            if taxonomy.setdefault(acc, taxon) != taxon:
                raise ValueError(f'{acc}: two taxonomy strings across samples')
        stats.append({'sample-id': sample, 'genomes': len(df),
                      'genera': df['Taxon'].str.split(';').str[5].nunique(),
                      'median-ani': df['ani'].median() if len(df) else np.nan,
                      'unknown-share': round(1 - df['seq'].sum() / 100, 6)})
    for sample in samples:
        if sample not in per_sample:
            per_sample[sample] = pd.DataFrame(
                columns=['Taxon', 'rel', 'seq', 'ani'])
            stats.append({'sample-id': sample, 'genomes': 0, 'genera': 0,
                          'median-ani': np.nan, 'unknown-share': 1.0})
    samples, features = sorted(per_sample), sorted(taxonomy)

    def _table(col, renormalize):
        # TODO: this is AI-generated code; human review pending
        data = np.zeros((len(features), len(samples)))
        for j, s in enumerate(samples):
            v = per_sample[s][col].reindex(features).fillna(0.0).to_numpy() / 100
            if renormalize and v.sum() > 0:
                v = v / v.sum()
            data[:, j] = v
        return biom.Table(data, features, samples)

    tax = pd.Series(taxonomy, name='Taxon').reindex(features)
    tax.index.name = 'Feature ID'
    md = pd.DataFrame(stats).set_index('sample-id').loc[samples]
    return _table('rel', False), _table('seq', True), tax, md


def taxprof_to_tables(taxonomic_profiles: SylphTaxProfilesDirFmt,
                      sketches: SylphSketchesDirFmt
                      ) -> (biom.Table, biom.Table, pd.Series, qiime2.Metadata):
    # TODO: this is AI-generated code; human review pending
    """sylph-tax .sylphmpa profiles -> genome-keyed tables, taxonomy and
    per-sample statistics; the sketches give the full sample list."""
    paths = [os.path.join(str(taxonomic_profiles), f)
             for f in os.listdir(str(taxonomic_profiles))
             if f.endswith('.sylphmpa')]
    rel, seq, tax, stats = _tables(paths, list(sketches.sample_paths()))
    return rel, seq, tax, qiime2.Metadata(stats)
