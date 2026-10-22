# mosh-sylph

A [QIIME 2](https://qiime2.org) plugin (registered name `sylph`; `rachis sylph <action>`) that wraps the [sylph](https://sylph-docs.github.io/) metagenome profiler (Shaw & Yu, *Nature Biotechnology* 2025).
Each wrapper runs one sylph command and returns the tool's own output as an artifact; two conversion actions turn those outputs into stock QIIME 2 types, keyed by GTDB genome ID so that GTDB's own taxonomy file and tree serve as taxonomy and phylogeny.
The plugin was [created from the template](https://develop.qiime2.org/en/stable/plugins/tutorials/create-from-template.html) and is experimental: its code is AI-generated and under review.

The tutorial that uses it, integrating a sylph metagenome profile with a 16S profile through [q2-confluence](https://github.com/gregcaporaso/q2-confluence), is the [thermo-hec-tutorial](https://github.com/gregcaporaso/thermo-hec-tutorial) repository; this repository carries no documentation of its own.

## Actions

| Action | Wraps | Inputs | Parameters | Outputs |
|---|---|---|---|---|
| `fetch-database` | download of the authors' pre-built GTDB database | | `release` (the newest listed by default), `base_url` (default `http://faust.compbio.cs.cmu.edu/sylph-stuff`) | `database`: `SylphTwoStageDatabase` |
| `sketch` | `sylph sketch` (paired-end reads) | `reads`: `SampleData[PairedEndSequencesWithQuality]` | `threads`, `c` (200), `k` (31; 21 or 31), `fpr` | `sketches`: `SylphSketches` |
| `profile` | `sylph profile` | `sketches`: `SylphSketches`, `database`: `SylphTwoStageDatabase` | `threads`, `minimum_ani` (95), `min_number_kmers`, `min_contain`, `min_count_correct`, `estimate_unknown` (off, as in sylph), `read_seq_id`, `screen_ani` | `profile`: `SylphProfile` |
| `query` | `sylph query` | `sketches`, `database` | as `profile`, `minimum_ani` 90, without `estimate_unknown` and `read_seq_id` | `query`: `SylphQuery` |
| `profile-to-tables` | conversion | `profile`: `SylphProfile`, `sketches`: `SylphSketches` | `gtdb_ids` (on: `RS_GCF_...` / `GB_GCA_...`, GTDB's genome IDs; off: the NCBI accession) | `taxonomic_abundance`, `sequence_abundance`: `FeatureTable[RelativeFrequency]`; `stats`: `ImmutableMetadata` (genomes, median-ani, unknown-share) |
| `query-to-metadata` | conversion | `query`: `SylphQuery`, `taxonomy`: `FeatureData[Taxonomy]` (optional, keyed by genome ID) | `gtdb_ids` (as `profile-to-tables`), `targets` (`List[Str]`, optional) | `query_metadata`: `ImmutableMetadata` |

The sylph options keep sylph's names and defaults; `rachis sylph <action> --help` gives each one's flag.

`profile-to-tables` keys its tables by GTDB genome ID (`RS_GCF_...`, `GB_GCA_...`, from the genome file names of the authors' GTDB databases; `--p-no-gtdb-ids` keeps the NCBI accession or, for other databases, the file name).
Both tables are sylph's numbers divided by 100: taxonomic abundance is the genome-size-corrected abundance (summing to 1 over the detected genomes), sequence abundance the share of reads, which with `--p-estimate-unknown` sums to the classified share rather than to 1 (the remainder is `unknown-share` in `stats`; see [the sylph cookbook](https://sylph-docs.github.io/sylph-cookbook/) on estimating the unknown percentage).
`stats` holds, per sample, `genomes`, `genera`, `median-ani` and `unknown-share` (the share of reads assigned to no database genome, meaningful for profiles made with `--p-estimate-unknown`).
A sample in which sylph detected nothing gets an all-zero column and an unknown share of 1; the sample list comes from the sketches.

`query-to-metadata` gives one row per sample and genome (ID `<sample-id>-<accession>`) with the columns `sample`, `accession`, `taxonomy`, `adjusted-ani`, `effective-coverage`, `ani-5-percentile`, `ani-95-percentile`, `containment-index` and `naive-ani`.
Below about 0.1x effective coverage the adjusted ANI and its interval overshoot (the 95th percentile can exceed 100).

## Types and formats

| Semantic type | Directory format | File in the artifact | Content |
|---|---|---|---|
| `SylphTwoStageDatabase` | `SylphTwoStageDatabaseDirFmt` | `database.syl2db` (`SylphTwoStageDatabaseFormat`) | two-stage sylph database (sylph >= 1.0.0) |
| `SylphSketches` | `SylphSketchesDirFmt` | `<sample-id>.paired.sylsp` (`SylphSketchFormat`) | one read sketch per sample |
| `SylphProfile` | `SylphProfileDirFmt` | `profile.tsv` (`SylphProfileFormat`) | sylph profile output |
| `SylphQuery` | `SylphQueryDirFmt` | `query.tsv` (`SylphQueryFormat`) | sylph query output |

A `SylphProfile` or `SylphQuery` artifact also views as a `pandas.DataFrame` of strings (`artifact.view(pd.DataFrame)`), read as sylph-tax reads sylph output: no quoting, and only the header's columns, because a tab inside a genome's first contig name adds fields to its row; `profile-to-tables` and `query-to-metadata` work on that view.

A database or taxonomy file already on disk is imported as a single file:

```shell
rachis tools import \
  --type SylphTwoStageDatabase \
  --input-format SylphTwoStageDatabaseFormat \
  --input-path gtdb-r232-c200-dbv2.syl2db \
  --output-path sylph-gtdb-r232.qza
```

Only two-stage databases (`.syl2db`) are accepted; a single-stage `.syldb` converts with `sylph convert-db-two-screen`.
`fetch-database` downloads the sylph authors' two-stage GTDB databases; [GlobDB](https://globdb.org) publishes its own sylph databases for r226 and r232, but only single-stage ones so far, so `fetch-database` will offer them once a two-stage build exists.
Until then, download the GlobDB database (`globdb_r<release>_sylph_c200.syldb` under `https://fileshare.lisc.univie.ac.at/globdb/globdb_r<release>/taxonomic_profiling/`, with md5 sums alongside; 35 to 40 GB), convert it, and import the result; its genomes are not NCBI assemblies, so `profile-to-tables` and `query-to-metadata` run with `--p-no-gtdb-ids`, and GlobDB's taxonomy file serves as their taxonomy:

```shell
sylph convert-db-two-screen \
  -t 8 \
  -o globdb-r232 \
  globdb_r232_sylph_c200.syldb

rachis tools import \
  --type SylphTwoStageDatabase \
  --input-format SylphTwoStageDatabaseFormat \
  --input-path globdb-r232.syl2db \
  --output-path sylph-globdb-r232.qza
```
A database is checked with `sylph inspect` whenever it is validated, including the output of `fetch-database`, so a broken download fails at once (9 s and 4.2 GB of memory on the 20 GB GTDB r232 database, which it reads only partially); a sketch is checked with `sylph inspect` when imported and only for emptiness as an action's output.

## Typical use

```shell
rachis sylph fetch-database \
  --p-release 232 \
  --o-database sylph-gtdb-r232.qza

rachis sylph sketch \
  --i-reads reads.qza \
  --p-threads 8 \
  --o-sketches sketches.qza

rachis sylph profile \
  --i-sketches sketches.qza \
  --i-database sylph-gtdb-r232.qza \
  --p-estimate-unknown \
  --p-threads 8 \
  --o-profile sylph-profile.qza

rachis sylph profile-to-tables \
  --i-profile sylph-profile.qza \
  --i-sketches sketches.qza \
  --o-taxonomic-abundance sylph-taxonomic-abundance.qza \
  --o-sequence-abundance sylph-sequence-abundance.qza \
  --o-stats sylph-stats.qza
```

The tables are keyed by GTDB's genome IDs, so GTDB's own taxonomy file (`bac120_taxonomy_r232.tsv.gz`, imported as `FeatureData[Taxonomy]` with `--input-format HeaderlessTSVTaxonomyFormat`) is their taxonomy and GTDB's tree their phylogeny; the [tutorial](https://github.com/gregcaporaso/thermo-hec-tutorial) does both.
The database is 19 GB; the tutorial shows how to keep it and the sketches in an artifact cache.

## Development installation

The plugin targets the unreleased 2026.10 epoch, so the base environment is a distribution's development environment, created as in the [QIIME 2 development environment guide](https://develop.qiime2.org/en/stable/plugins/how-to-guides/set-up-development-environment.html) from the distribution's `dev/latest/passed` environment file for your platform; the plugin's extras (sylph, the test and lint tools) are layered on with `conda env update`.
The *tiny* distribution (rachis, rachis-cli, q2-types, q2-metadata) is all the plugin needs.
As the guide suggests, the environment is named by its creation date (`mosh-sylph-dev-$(date "+%Y-%m-%d")`), so that a later rebuild can exist beside it; run the commands below on one day, or spell out the name.

Linux (x86_64):

```shell
conda env create \
  -n mosh-sylph-dev-$(date "+%Y-%m-%d") \
  --file https://raw.githubusercontent.com/qiime2/distributions/dev/latest/passed/rachis-tiny-linux-64-conda.yml
```

macOS on Apple Silicon (the tiny distribution has a native arm64 build, so no Rosetta):

```shell
conda env create \
  -n mosh-sylph-dev-$(date "+%Y-%m-%d") \
  --file https://raw.githubusercontent.com/qiime2/distributions/dev/latest/passed/rachis-tiny-osx-arm64-conda.yml
```

macOS on Intel uses `rachis-tiny-osx-64-conda.yml`.
Then, in the activated environment, from this directory:

```shell
conda activate mosh-sylph-dev-$(date "+%Y-%m-%d")

conda env update \
  -n mosh-sylph-dev-$(date "+%Y-%m-%d") \
  --file environment-files/mosh-sylph-dev-extras.yml

make dev
rachis dev refresh-cache
rachis sylph --help
```

The dev environment files are rebuilt as the distribution's packages change; recreate the environment every few weeks, as the guide suggests.

Run the tests and the linters with:

```shell
make test
make lint
```

To use the plugin inside the moshpit or qiime2 distribution instead, create that distribution's development environment the same way (`rachis-moshpit-linux-64-conda.yml`; `rachis-qiime2-<platform>-conda.yml`, which on Apple Silicon needs the guide's `CONDA_SUBDIR=osx-64` steps because that distribution has no arm64 build), then apply the same extras file and `make dev`.

The tests compare every action with a direct sylph run on a small real fixture (`mosh_sylph/tests/data/`, described in its README) and execute every usage example; the suite takes under a minute.
