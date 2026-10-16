# mosh-sylph

A [QIIME 2](https://qiime2.org) plugin (registered name `sylph`; `rachis sylph <action>`) that wraps the [sylph](https://sylph-docs.github.io/) metagenome profiler (Shaw & Yu, *Nature Biotechnology* 2025) and its taxonomy companion sylph-tax.
Each action runs one sylph or sylph-tax command and returns the tool's own output as an artifact; separate conversion actions turn those outputs into feature tables, taxonomies and metadata.
The plugin was [created from the template](https://develop.qiime2.org/en/stable/plugins/tutorials/create-from-template.html) and is experimental: its code is AI-generated and under review.

## Install (development version)

The development environment is the 2026.10 *tiny* distribution from the `passed` channel plus sylph 1.0.0 and sylph-tax 1.9.2 from bioconda:

```shell
conda env create -n mosh-sylph-dev --file environment-files/mosh-sylph-rachis-tiny-dev.yml
conda activate mosh-sylph-dev
make dev
rachis dev refresh-cache
rachis sylph --help
```

The plugin depends only on `rachis`, `q2-types`, sylph and sylph-tax, so it also installs into the moshpit and qiime2 distributions once sylph and sylph-tax are added (`conda install -c bioconda sylph=1.0.0 sylph-tax=1.9.2`, then `pip install .`).

## Checks

```shell
make lint
make test
```
