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
from mosh_sylph._convert import (_accession, _build_tables, _gtdb_id,
                                 _query_to_metadata, _read_profile)
from mosh_sylph._formats import _read_sylph_tsv
from mosh_sylph._formats import SylphProfileFormat, SylphQueryFormat


class AccessionTests(unittest.TestCase):

    def test_forms(self):
        self.assertEqual(_accession('GCF_000227485.1_ASM22748v1_genomic.fna.gz'),
                         'GCF_000227485.1')
        self.assertEqual(_accession('/db/GCA_01.2_genomic.fna'), 'GCA_01.2')
        self.assertEqual(_accession('mygenome.fasta'), 'mygenome')


PROFILE_HEADER = ('Sample_file\tGenome_file\tTaxonomic_abundance\t'
                  'Sequence_abundance\tAdjusted_ANI\tTrue_cov\tContig_name\n')


def _profile(rows):
    # TODO: this is AI-generated code; human review pending
    """rows: [(sample, genome file, rel, seq, ani, contig name)] -> text."""
    return PROFILE_HEADER + ''.join(
        f'{s}\t{g}\t{rel}\t{seq}\t{ani}\t0.1\t{contig}\n'
        for s, g, rel, seq, ani, contig in rows)


class GtdbIdTests(unittest.TestCase):

    def test_forms(self):
        # TODO: this is AI-generated code; human review pending
        self.assertEqual(_gtdb_id('GCF_000227485.1'), 'RS_GCF_000227485.1')
        self.assertEqual(_gtdb_id('GCA_000154345.1'), 'GB_GCA_000154345.1')
        with self.assertRaisesRegex(ValueError, 'no GTDB form'):
            _gtdb_id('mygenome')


class ProfileParserTests(unittest.TestCase):

    def setUp(self):
        # TODO: this is AI-generated code; human review pending
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, 'profile.tsv')
        with open(self.path, 'w') as fh:
            fh.write(_profile([
                ('s1', 'genomes/GCF_1.1_genomic.fna.gz', 60.0, 70.0, 99.1,
                 'NC_1 a contig\twith a tab in its name'),
                ('s1', 'genomes/GCA_2.1_genomic.fna.gz', 40.0, 10.0, 97.3, 'c2'),
                ('s2', 'genomes/GCA_2.1_genomic.fna.gz', 100.0, 50.0, 98.0, 'c2')]))

    def tearDown(self):
        # TODO: this is AI-generated code; human review pending
        self.tmp.cleanup()

    def test_read(self):
        # TODO: this is AI-generated code; human review pending
        per_sample = _read_profile(_read_sylph_tsv(self.path))
        self.assertEqual(sorted(per_sample), ['s1', 's2'])
        self.assertEqual(list(per_sample['s1'].index), ['GCF_1.1', 'GCA_2.1'])
        self.assertEqual(per_sample['s1'].loc['GCF_1.1', 'ani'], 99.1)
        self.assertEqual(per_sample['s2'].loc['GCA_2.1', 'seq'], 50.0)

    def test_tables(self):
        # TODO: this is AI-generated code; human review pending
        rel, seq, stats = _build_tables(_read_profile(_read_sylph_tsv(self.path)),
                                        ['s1', 's2', 's3'])
        self.assertEqual(list(rel.ids()), ['s1', 's2', 's3'])
        self.assertEqual(list(rel.ids(axis='observation')), ['GCA_2.1', 'GCF_1.1'])
        self.assertAlmostEqual(rel.get_value_by_ids('GCF_1.1', 's1'), 0.6)
        # sylph's numbers divided by 100, not renormalized: s1 sums to 0.8
        self.assertAlmostEqual(seq.get_value_by_ids('GCF_1.1', 's1'), 0.7)
        self.assertAlmostEqual(seq.get_value_by_ids('GCA_2.1', 's2'), 0.5)
        self.assertAlmostEqual(seq.sum(axis='sample')[0], 0.8)
        self.assertEqual(list(stats.columns),
                         ['genomes', 'median-ani', 'unknown-share'])
        self.assertEqual(stats.loc['s1', 'genomes'], 2)
        self.assertAlmostEqual(stats.loc['s1', 'median-ani'], 98.2)
        self.assertAlmostEqual(stats.loc['s1', 'unknown-share'], 0.2)
        # s3: no detection, all-zero column, unknown share 1
        self.assertEqual(rel.data('s3').sum(), 0.0)
        self.assertEqual(stats.loc['s3', 'genomes'], 0)
        self.assertEqual(stats.loc['s3', 'unknown-share'], 1.0)

    def test_genome_twice(self):
        # TODO: this is AI-generated code; human review pending
        with open(self.path, 'a') as fh:
            fh.write(_profile([('s2', 'GCA_2.1_genomic.fna.gz', 1, 1, 99, 'c')])
                     .split('\n', 1)[1])
        with self.assertRaisesRegex(ValueError, 'genome GCA_2.1 twice for sample s2'):
            _read_profile(_read_sylph_tsv(self.path))

    def test_profile_without_sketch(self):
        # TODO: this is AI-generated code; human review pending
        with self.assertRaisesRegex(ValueError, 's2 has a profile but no sketch'):
            _build_tables(_read_profile(_read_sylph_tsv(self.path)), ['s1'])


class ProfileToTablesTests(TestPluginBase):
    package = 'mosh_sylph.tests'

    def test_fixture_against_sylph_profile(self):
        # TODO: this is AI-generated code; human review pending
        sketches = ex._sketches_factory()
        profile, = self.plugin.methods['profile'](
            sketches, ex._database_factory(), threads=1, estimate_unknown=True)
        rel, seq, stats = self.plugin.methods['profile_to_tables'](profile,
                                                                   sketches)
        self.assertEqual(str(rel.type), 'FeatureTable[RelativeFrequency]')
        self.assertEqual(str(stats.type), 'ImmutableMetadata')
        rel, seq = rel.view(biom.Table), seq.view(biom.Table)
        stats = stats.view(qiime2.Metadata).to_dataframe()
        with open(str(profile.view(SylphProfileFormat))) as fh:
            direct = pd.read_csv(io.StringIO(fh.read()), sep='\t')
        direct['gtdb-id'] = direct['Genome_file'].map(_accession).map(_gtdb_id)
        self.assertEqual(list(rel.ids()), ex._SAMPLES)
        self.assertEqual(sorted(rel.ids(axis='observation')),
                         sorted(direct['gtdb-id'].unique()))
        self.assertTrue(all(i.startswith('RS_GCF_')
                            for i in rel.ids(axis='observation')))
        for sample, rows in direct.groupby('Sample_file'):
            unknown = 1 - rows['Sequence_abundance'].sum() / 100
            self.assertAlmostEqual(stats.loc[sample, 'unknown-share'], unknown,
                                   places=5)
            for _, r in rows.iterrows():
                self.assertAlmostEqual(
                    rel.get_value_by_ids(r['gtdb-id'], sample),
                    r['Taxonomic_abundance'] / 100, places=5)
                self.assertAlmostEqual(
                    seq.get_value_by_ids(r['gtdb-id'], sample),
                    r['Sequence_abundance'] / 100, places=5)
        self.assertEqual(stats.loc['73F84', 'genomes'], 0)
        self.assertEqual(stats.loc['73F84', 'unknown-share'], 1.0)
        self.assertEqual(stats.loc['DB47D', 'genomes'], 2)

    def test_ncbi_ids(self):
        # TODO: this is AI-generated code; human review pending
        sketches = ex._sketches_factory()
        profile, = self.plugin.methods['profile'](
            sketches, ex._database_factory(), threads=1)
        rel, _, _ = self.plugin.methods['profile_to_tables'](profile, sketches,
                                                             gtdb_ids=False)
        self.assertTrue(all(i.startswith('GCF_')
                            for i in rel.view(biom.Table).ids(axis='observation')))


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
            fh.write('s1\t/db/GCA_000003.1_genomic.fna.gz\t99.00\t0.500\t'
                     '98.0-99.9\t0.5\t0.4-0.6\t1\t1.200\t90/300\t96.00\t'
                     'contig "3"\textra field\n')
        self.taxonomy = pd.Series({'RS_GCF_000001.1': 'd__Bacteria;g__A;s__A one',
                                   'RS_GCF_000002.1': 'd__Bacteria;g__B;s__B two'})
        self.query = _read_sylph_tsv(self.path)

    def tearDown(self):
        # TODO: this is AI-generated code; human review pending
        shutil.rmtree(self.dir)

    def test_rows(self):
        # TODO: this is AI-generated code; human review pending
        df = _query_to_metadata(self.query, self.taxonomy).to_dataframe()
        self.assertEqual(list(df.index), ['s1-GB_GCA_000003.1', 's1-RS_GCF_000001.1',
                                          's2-RS_GCF_000002.1'])
        self.assertEqual(df.loc['s1-GB_GCA_000003.1', 'naive-ani'], 96.0)
        self.assertTrue(pd.isna(df.loc['s1-GB_GCA_000003.1', 'taxonomy']))
        self.assertEqual(list(df.columns), [
            'sample', 'genome', 'taxonomy', 'adjusted-ani',
            'effective-coverage', 'ani-5-percentile', 'ani-95-percentile',
            'containment-index', 'naive-ani'])
        self.assertEqual(df.loc['s2-RS_GCF_000002.1', 'taxonomy'],
                         'd__Bacteria;g__B;s__B two')
        self.assertEqual(df.loc['s2-RS_GCF_000002.1', 'adjusted-ani'], 97.5)
        self.assertEqual(df.loc['s2-RS_GCF_000002.1', 'effective-coverage'], 0.08)
        self.assertEqual(df.loc['s2-RS_GCF_000002.1', 'ani-5-percentile'], 96.1)
        self.assertEqual(df.loc['s2-RS_GCF_000002.1', 'ani-95-percentile'], 101.2)
        self.assertTrue(np.isnan(df.loc['s1-RS_GCF_000001.1', 'ani-5-percentile']))
        self.assertEqual(df.loc['s1-RS_GCF_000001.1', 'containment-index'], '270/270')
        self.assertEqual(df.loc['s1-RS_GCF_000001.1', 'naive-ani'], 100.0)

    def test_without_taxonomy_and_ncbi_ids(self):
        # TODO: this is AI-generated code; human review pending
        df = _query_to_metadata(self.query, gtdb_ids=False).to_dataframe()
        self.assertEqual(list(df.index), ['s1-GCA_000003.1', 's1-GCF_000001.1',
                                          's2-GCF_000002.1'])
        self.assertTrue(df['taxonomy'].isna().all())

    def test_targets(self):
        # TODO: this is AI-generated code; human review pending
        by_taxon = _query_to_metadata(self.query, self.taxonomy, targets=['g__B;'])
        self.assertEqual(list(by_taxon.to_dataframe().index), ['s2-RS_GCF_000002.1'])
        by_genome = _query_to_metadata(self.query, self.taxonomy, targets=['GCF_00000'])
        self.assertEqual(list(by_genome.to_dataframe().index),
                         ['s1-RS_GCF_000001.1', 's2-RS_GCF_000002.1'])
        with self.assertRaisesRegex(ValueError, 'no reported genome matches'):
            _query_to_metadata(self.query, self.taxonomy, targets=['g__C;'])

    def test_empty(self):
        # TODO: this is AI-generated code; human review pending
        with open(self.path, 'w') as fh:
            fh.write(_QUERY_HEADER)
        with self.assertRaisesRegex(ValueError, 'no genome with enough'):
            _query_to_metadata(_read_sylph_tsv(self.path), self.taxonomy)


class QueryToMetadataTests(TestPluginBase):
    package = 'mosh_sylph.tests'

    def test_fixture_against_sylph_query(self):
        # TODO: this is AI-generated code; human review pending
        query = ex._query_factory()
        md, = self.plugin.methods['query_to_metadata'](
            query, ex._genome_taxonomy_factory())
        self.assertEqual(str(md.type), 'ImmutableMetadata')
        df = md.view(qiime2.Metadata).to_dataframe()
        with open(str(query.view(SylphQueryFormat))) as fh:
            direct = pd.read_csv(io.StringIO(fh.read()), sep='\t', dtype=str)
        self.assertEqual(len(df), len(direct))
        for _, r in direct.iterrows():
            genome = _gtdb_id(_accession(r['Genome_file']))
            row = df.loc[f"{r['Sample_file']}-{genome}"]
            self.assertEqual(row['adjusted-ani'], float(r['Adjusted_ANI']))
            self.assertEqual(row['effective-coverage'], float(r['Eff_cov']))
            self.assertEqual(row['containment-index'], r['Containment_ind'])
            self.assertEqual(row['naive-ani'], float(r['Naive_ANI']))
            low, high = r['ANI_5-95_percentile'].split('-')
            self.assertEqual(row['ani-5-percentile'], float(low))
            self.assertEqual(row['ani-95-percentile'], float(high))
        # T. fusca in DB47D at 0.05x: the interval overshoots 100
        self.assertGreater(df.loc['DB47D-RS_GCF_001592045.1', 'ani-95-percentile'],
                           100)
        self.assertTrue(df.loc['DB47D-RS_GCF_001592045.1', 'taxonomy'].endswith(
            'g__Thermobifida;s__Thermobifida fusca'))
        # R. intestinale is not in the example taxonomy: an empty cell
        self.assertTrue(pd.isna(df.loc['1135D-RS_GCF_040096305.1', 'taxonomy']))

    def test_targets(self):
        # TODO: this is AI-generated code; human review pending
        md, = self.plugin.methods['query_to_metadata'](
            ex._query_factory(), ex._genome_taxonomy_factory(),
            targets=['g__Thermobifida;'])
        self.assertEqual(list(md.view(qiime2.Metadata).to_dataframe().index),
                         ['DB47D-RS_GCF_001592045.1'])
