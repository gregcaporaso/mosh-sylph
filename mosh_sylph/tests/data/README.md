# Test fixture

Small real data for comparing every action with a direct sylph or sylph-tax run; the usage examples run on it too.
Built on 2026-10-16 with sylph 1.0.0 and sylph-tax 1.9.2.

## `fixture.syl2db`

A two-stage sylph database of three GTDB r232 species representatives that the thermo-hec tutorial samples contain, downloaded from NCBI and named as in the authors' GTDB databases (`<accession>_genomic.fna.gz`):

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
