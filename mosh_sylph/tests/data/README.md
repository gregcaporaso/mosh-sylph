# Test fixture

Small real data for comparing every action with a direct sylph run; the usage examples run on it too.
Built on 2026-10-16 with sylph 1.0.0.

## `fixture.syl2db`

A two-stage sylph database of three GTDB r232 species representatives that the [q2-confluence-tutorial](https://github.com/gregcaporaso/q2-confluence-tutorial) samples contain, downloaded from NCBI and named as in the authors' GTDB databases (`<accession>_genomic.fna.gz`):

| Accession | GTDB r232 species | Size |
|---|---|---|
| GCF_000023865.1 | *Saccharomonospora viridis* | 4.3 Mb |
| GCF_001592045.1 | *Thermobifida fusca* | 3.6 Mb |
| GCF_040096305.1 | *Ruminococcoides intestinale* | 2.3 Mb |

```shell
for a in GCF_000023865.1 GCF_001592045.1 GCF_040096305.1; do
  curl -sSL -o $a.zip "https://api.ncbi.nlm.nih.gov/datasets/v2/genome/accession/$a/download?include_annotation_type=GENOME_FASTA"
  unzip -q $a.zip -d $a && gzip -c $a/ncbi_dataset/data/$a/*.fna > genomes/${a}_genomic.fna.gz
done
sylph sketch -t 3 -g genomes/*.fna.gz -o fixture            # c=200, k=31: the authors' settings
sylph convert-db-two-screen -t 3 -o fixture fixture.syldb
```

## `reads/`

Read pairs of three tutorial samples (the tutorial's `metagenome-reads-10p.qza`, named `wgs-subset-reads.qza` until 2026-10-30; its data-preparation page describes the trimming, host-read removal and 10% subsample), chosen so that the database detects one genome in 1135D (*R. intestinale*), two in DB47D (*S. viridis* and *T. fusca*) and none in the soil sample 73F84, each beside an unknown share of about half the reads:

 * From the first 400,000 pairs of each sample, in file order: the first 2,000 pairs whose forward read shares a 31-mer with the three genomes (genome k-mers taken every 16th position, both strands), then the first 2,000 pairs whose forward read shares none.
   73F84 has only 484 such pairs among its first 400,000, all of which are kept.
 * Gzipped with mtime 0, as `<sample>_R1.fastq.gz` and `<sample>_R2.fastq.gz`.

Coverage is 0.05x to 0.24x, low enough that sylph's ANI intervals overshoot 100 (sylph query's 95th percentile reaches 101.4 for *T. fusca* in DB47D).
