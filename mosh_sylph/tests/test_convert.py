# ----------------------------------------------------------------------------
# Copyright (c) 2026, Greg Caporaso.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import io
import os
import shutil
import tempfile
import unittest

import biom
import numpy as np
import pandas as pd
import qiime2
from qiime2.plugin.testing import TestPluginBase

from mosh_sylph import _examples as ex
from mosh_sylph._convert import (_accession, _query_to_metadata, _read_sylphmpa,
                                 _tables)
from mosh_sylph._formats import SylphProfileDirFmt, SylphQueryDirFmt

LINEAGE = ('d__Bacteria|p__Bacillota_A|c__Clostridia|o__Lachnospirales|'
           'f__Lachnospiraceae|g__Blautia')
HEADER = ('clade_name\trelative_abundance\tsequence_abundance\t'
          'ANI (if strain-level)\tCoverage (if strain-level)\n')


def _sylphmpa(sample, strains):
    # TODO: this is AI-generated code; human review pending
    """strains: [(accession, species, rel, seq, ani)] -> file text."""
    lines = [f'#SampleID\t{sample}\tTaxonomies_used:[\'GTDB_r232\']\n', HEADER,
             f'd__Bacteria\t100.0\t{sum(s[3] for s in strains)}\tNA\tNA\n']
    for acc, species, rel, seq, ani in strains:
        lines.append(f'{LINEAGE}|s__{species}\t{rel}\t{seq}\tNA\tNA\n')
        lines.append(f'{LINEAGE}|s__{species}|t__{acc}_genomic.fna.gz\t{rel}\t{seq}'
                     f'\t{ani}\t12.5\n')
    return ''.join(lines)


class AccessionTests(unittest.TestCase):

    def test_forms(self):
        # TODO: this is AI-generated code; human review pending
        self.assertEqual(_accession('GCF_000227485.1_ASM22748v1_genomic.fna.gz'),
                         'GCF_000227485.1')
        self.assertEqual(_accession('/db/GCA_01.2_genomic.fna'), 'GCA_01.2')
        self.assertEqual(_accession('mygenome.fasta'), 'mygenome')


class SylphmpaParserTests(unittest.TestCase):

    def setUp(self):
        # TODO: this is AI-generated code; human review pending
        self.tmp = tempfile.TemporaryDirectory()
        self.paths = []
        for sample, strains in [
            ('s1', [('GCF_1.1', 'Blautia wexlerae', 60.0, 70.0, 99.1),
                    ('GCF_2.1', 'Blautia_A obeum', 40.0, 10.0, 97.3)]),
            ('s2', [('GCF_2.1', 'Blautia_A obeum', 100.0, 50.0, 98.0)]),
        ]:
            p = os.path.join(self.tmp.name, f'{sample}.sylphmpa')
            with open(p, 'w') as fh:
                fh.write(_sylphmpa(sample, strains))
            self.paths.append(p)

    def tearDown(self):
        # TODO: this is AI-generated code; human review pending
        self.tmp.cleanup()

    def _write(self, name, text):
        # TODO: this is AI-generated code; human review pending
        p = os.path.join(self.tmp.name, name)
        with open(p, 'w') as fh:
            fh.write(text)
        return p

    def test_read_one(self):
        # TODO: this is AI-generated code; human review pending
        sample, df = _read_sylphmpa(self.paths[0])
        self.assertEqual(sample, 's1')
        self.assertEqual(list(df.index), ['GCF_1.1', 'GCF_2.1'])
        self.assertEqual(df.loc['GCF_1.1', 'Taxon'],
                         LINEAGE.replace('|', ';') + ';s__Blautia wexlerae')
        self.assertEqual(df.loc['GCF_2.1', 'ani'], 97.3)

    def test_tables(self):
        # TODO: this is AI-generated code; human review pending
        rel, seq, tax, stats = _tables(self.paths, ['s1', 's2', 's3'])
        self.assertEqual(list(rel.ids()), ['s1', 's2', 's3'])
        self.assertEqual(list(rel.ids(axis='observation')), ['GCF_1.1', 'GCF_2.1'])
        self.assertAlmostEqual(rel.get_value_by_ids('GCF_1.1', 's1'), 0.6)
        self.assertAlmostEqual(rel.get_value_by_ids('GCF_1.1', 's2'), 0.0)
        # sequence abundance renormalized over detected genomes (unknown 20%)
        self.assertAlmostEqual(seq.get_value_by_ids('GCF_1.1', 's1'), 0.875)
        self.assertAlmostEqual(seq.get_value_by_ids('GCF_2.1', 's2'), 1.0)
        self.assertEqual(tax.index.name, 'Feature ID')
        self.assertEqual(tax['GCF_2.1'],
                         LINEAGE.replace('|', ';') + ';s__Blautia_A obeum')
        self.assertEqual(stats.loc['s1', 'genomes'], 2)
        self.assertEqual(stats.loc['s1', 'genera'], 1)
        self.assertAlmostEqual(stats.loc['s1', 'unknown-share'], 0.2)
        self.assertAlmostEqual(stats.loc['s2', 'unknown-share'], 0.5)
        self.assertAlmostEqual(stats.loc['s1', 'median-ani'], 98.2)
        # s3: no profile, all-zero column, unknown share 1
        self.assertEqual(rel.sum(axis='sample')[2], 0.0)
        self.assertEqual(stats.loc['s3', 'genomes'], 0)
        self.assertEqual(stats.loc['s3', 'unknown-share'], 1.0)

    def test_profile_without_sketch(self):
        # TODO: this is AI-generated code; human review pending
        with self.assertRaisesRegex(ValueError, 's2 has a profile but no sketch'):
            _tables(self.paths, ['s1'])

    def test_conflicting_taxonomy(self):
        # TODO: this is AI-generated code; human review pending
        p = self._write('s3.sylphmpa',
                        _sylphmpa('s3', [('GCF_1.1', 'Other name', 100, 50, 99)]))
        with self.assertRaisesRegex(ValueError, 'two taxonomy strings'):
            _tables(self.paths + [p], ['s1', 's2', 's3'])

    def test_no_taxonomy(self):
        # TODO: this is AI-generated code; human review pending
        p = self._write('s4.sylphmpa', (
            '#SampleID\ts4\tTaxonomies_used:[]\n' + HEADER
            + 'NO_TAXONOMY\t100.0\t50.0\tNA\tNA\n'
            'NO_TAXONOMY|t__GCF_9.1_genomic.fna.gz:contig1\t100.0\t50.0\t99.0'
            '\t1.0\n'))
        with self.assertRaisesRegex(ValueError, 'no entry in the sylph-tax'):
            _read_sylphmpa(p)

    def test_not_sylphmpa(self):
        # TODO: this is AI-generated code; human review pending
        p = self._write('x.tsv', 'a\tb\n')
        with self.assertRaisesRegex(ValueError, 'not a .sylphmpa'):
            _read_sylphmpa(p)


class TaxprofToTablesTests(TestPluginBase):
    package = 'mosh_sylph.tests'

    def test_fixture_against_sylph_profile(self):
        # TODO: this is AI-generated code; human review pending
        sketches = ex._sketches_factory()
        profile, = self.plugin.methods['profile'](
            sketches, ex._database_factory(), threads=1, estimate_unknown=True)
        profiles, = self.plugin.methods['taxprof'](profile,
                                                   ex._taxonomy_factory())
        rel, seq, tax, stats = self.plugin.methods['taxprof_to_tables'](
            profiles, sketches)
        self.assertEqual(str(rel.type), 'FeatureTable[RelativeFrequency]')
        self.assertEqual(str(tax.type), 'FeatureData[Taxonomy]')
        self.assertEqual(str(stats.type), 'ImmutableMetadata')
        rel, seq = rel.view(biom.Table), seq.view(biom.Table)
        stats = stats.view(qiime2.Metadata).to_dataframe()
        with open(os.path.join(str(profile.view(SylphProfileDirFmt)),
                               'profile.tsv')) as fh:
            direct = pd.read_csv(io.StringIO(fh.read()), sep='\t')
        direct['accession'] = direct['Genome_file'].map(_accession)
        self.assertEqual(list(rel.ids()), ex._SAMPLES)
        self.assertEqual(sorted(rel.ids(axis='observation')),
                         sorted(direct['accession'].unique()))
        for sample, rows in direct.groupby('Sample_file'):
            unknown = 1 - rows['Sequence_abundance'].sum() / 100
            self.assertAlmostEqual(stats.loc[sample, 'unknown-share'], unknown,
                                   places=5)
            self.assertGreater(unknown, 0.3)
            for _, r in rows.iterrows():
                self.assertAlmostEqual(
                    rel.get_value_by_ids(r['accession'], sample),
                    r['Taxonomic_abundance'] / 100, places=5)
                self.assertAlmostEqual(
                    seq.get_value_by_ids(r['accession'], sample),
                    r['Sequence_abundance'] / rows['Sequence_abundance'].sum(),
                    places=5)
        # 73F84: no detection, all-zero column, unknown share 1
        self.assertEqual(rel.data('73F84').sum(), 0.0)
        self.assertEqual(stats.loc['73F84', 'genomes'], 0)
        self.assertEqual(stats.loc['73F84', 'unknown-share'], 1.0)
        self.assertEqual(stats.loc['DB47D', 'genomes'], 2)
        self.assertEqual(tax.view(pd.Series)['GCF_001592045.1'],
                         'd__Bacteria;p__Actinomycetota;c__Actinomycetes;'
                         'o__Streptosporangiales;f__Streptosporangiaceae;'
                         'g__Thermobifida;s__Thermobifida fusca')


_QUERY_HEADER = ('Sample_file\tGenome_file\tAdjusted_ANI\tEff_cov\t'
                 'ANI_5-95_percentile\tEff_lambda\tLambda_5-95_percentile\t'
                 'Median_cov\tMean_cov_geq1\tContainment_ind\tNaive_ANI\t'
                 'Contig_name\n')


class QueryParserTests(unittest.TestCase):

    def setUp(self):
        # TODO: this is AI-generated code; human review pending
        self.dir = tempfile.mkdtemp()
        self.path = os.path.join(self.dir, 'query.tsv')
        with open(self.path, 'w') as fh:
            fh.write(_QUERY_HEADER)
            fh.write('s2\t/db/GCF_000002.1_genomic.fna.gz\t97.50\t0.080\t'
                     '96.1-101.2\t0.08\t0.05-0.11\t1\t1.000\t60/900\t95.10\t'
                     'GCF_000002.1\n')
            fh.write('s1\t/db/GCF_000001.1_genomic.fna.gz\t100.00\t15.000\t'
                     'NA-NA\tHIGH\tNA-NA\t15\t15.485\t270/270\t100.00\t'
                     'GCF_000001.1\n')
            # a tab and a quote inside the contig name, as sylph passes them on
            fh.write('s1\t/db/GCF_000003.1_genomic.fna.gz\t99.00\t0.500\t'
                     '98.0-99.9\t0.5\t0.4-0.6\t1\t1.200\t90/300\t96.00\t'
                     'contig "3"\textra field\n')
        self.taxonomy = {'GCF_000001.1': 'd__Bacteria;g__A;s__A one',
                         'GCF_000002.1': 'd__Bacteria;g__B;s__B two'}

    def tearDown(self):
        # TODO: this is AI-generated code; human review pending
        shutil.rmtree(self.dir)

    def test_rows(self):
        # TODO: this is AI-generated code; human review pending
        df = _query_to_metadata(self.path, self.taxonomy).to_dataframe()
        self.assertEqual(list(df.index), ['s1-GCF_000001.1', 's1-GCF_000003.1',
                                          's2-GCF_000002.1'])
        self.assertEqual(df.loc['s1-GCF_000003.1', 'naive-ani'], 96.0)
        self.assertTrue(pd.isna(df.loc['s1-GCF_000003.1', 'taxonomy']))
        self.assertEqual(list(df.columns), [
            'sample', 'accession', 'taxonomy', 'adjusted-ani',
            'effective-coverage', 'ani-5-percentile', 'ani-95-percentile',
            'containment-index', 'naive-ani'])
        self.assertEqual(df.loc['s2-GCF_000002.1', 'taxonomy'],
                         'd__Bacteria;g__B;s__B two')
        self.assertEqual(df.loc['s2-GCF_000002.1', 'adjusted-ani'], 97.5)
        self.assertEqual(df.loc['s2-GCF_000002.1', 'effective-coverage'], 0.08)
        self.assertEqual(df.loc['s2-GCF_000002.1', 'ani-5-percentile'], 96.1)
        self.assertEqual(df.loc['s2-GCF_000002.1', 'ani-95-percentile'], 101.2)
        self.assertTrue(np.isnan(df.loc['s1-GCF_000001.1', 'ani-5-percentile']))
        self.assertEqual(df.loc['s1-GCF_000001.1', 'containment-index'], '270/270')
        self.assertEqual(df.loc['s1-GCF_000001.1', 'naive-ani'], 100.0)

    def test_targets(self):
        # TODO: this is AI-generated code; human review pending
        by_taxon = _query_to_metadata(self.path, self.taxonomy, ['g__B;'])
        self.assertEqual(list(by_taxon.to_dataframe().index), ['s2-GCF_000002.1'])
        by_accession = _query_to_metadata(self.path, self.taxonomy, ['GCF_00000'])
        self.assertEqual(list(by_accession.to_dataframe().index),
                         ['s1-GCF_000001.1', 's1-GCF_000003.1', 's2-GCF_000002.1'])
        with self.assertRaisesRegex(ValueError, 'no reported genome matches'):
            _query_to_metadata(self.path, self.taxonomy, ['g__C;'])

    def test_empty(self):
        # TODO: this is AI-generated code; human review pending
        with open(self.path, 'w') as fh:
            fh.write(_QUERY_HEADER)
        with self.assertRaisesRegex(ValueError, 'no genome with enough'):
            _query_to_metadata(self.path, self.taxonomy)


class QueryToMetadataTests(TestPluginBase):
    package = 'mosh_sylph.tests'

    def test_fixture_against_sylph_query(self):
        # TODO: this is AI-generated code; human review pending
        query = ex._query_factory()
        md, = self.plugin.methods['query_to_metadata'](query,
                                                       ex._taxonomy_factory())
        self.assertEqual(str(md.type), 'ImmutableMetadata')
        df = md.view(qiime2.Metadata).to_dataframe()
        with open(os.path.join(str(query.view(SylphQueryDirFmt)),
                               'query.tsv')) as fh:
            direct = pd.read_csv(io.StringIO(fh.read()), sep='\t', dtype=str)
        self.assertEqual(len(df), len(direct))
        for _, r in direct.iterrows():
            row = df.loc[f"{r['Sample_file']}-{_accession(r['Genome_file'])}"]
            self.assertEqual(row['adjusted-ani'], float(r['Adjusted_ANI']))
            self.assertEqual(row['effective-coverage'], float(r['Eff_cov']))
            self.assertEqual(row['containment-index'], r['Containment_ind'])
            self.assertEqual(row['naive-ani'], float(r['Naive_ANI']))
            low, high = r['ANI_5-95_percentile'].split('-')
            self.assertEqual(row['ani-5-percentile'], float(low))
            self.assertEqual(row['ani-95-percentile'], float(high))
        # T. fusca in DB47D at 0.05x: the interval overshoots 100
        self.assertGreater(df.loc['DB47D-GCF_001592045.1', 'ani-95-percentile'],
                           100)
        self.assertTrue(df.loc['DB47D-GCF_001592045.1', 'taxonomy'].endswith(
            'g__Thermobifida;s__Thermobifida fusca'))

    def test_targets(self):
        # TODO: this is AI-generated code; human review pending
        md, = self.plugin.methods['query_to_metadata'](
            ex._query_factory(), ex._taxonomy_factory(),
            targets=['g__Thermobifida;'])
        self.assertEqual(list(md.view(qiime2.Metadata).to_dataframe().index),
                         ['DB47D-GCF_001592045.1'])
