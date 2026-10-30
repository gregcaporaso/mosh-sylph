# mosh-sylph: a [rachis](https://rachis.org) plugin for use with QIIME 2 and/or MOSHPIT

⚠️ This plugin is in early testing (alpha release) phase. Interfaces will almost certainly change. Be skeptical of results - testing is still in progress.

`mosh-sylph` wraps the [sylph](https://sylph-docs.github.io/) metagenome profiler (Shaw & Yu, *Nature Biotechnology* 2025).
It is designed to be an extremely thin wrapper around sylph, supporting integration with QIIME 2 and MOSHPIT, and adding [data provenance tracking](https://news.rachis.org/en/latest/glossary#term-data-provenance).
Each [Action](https://news.rachis.org/en/latest/glossary#term-action) runs one sylph command and returns the tool's own output as a [`rachis` Artifact](https://news.rachis.org/en/latest/glossary#term-artifact).
Two additional conversion actions turn those outputs into `FeatureTable[RelativeFrequency]` and `ImmutableMetadata` artifacts for easy use with QIIME 2 and MOSHPIT.

See the [q2-confluence-tutorial](https://gregcaporaso.github.io/q2-confluence-tutorial/) ([source](https://github.com/gregcaporaso/q2-confluence-tutorial)) for documentation, including installation and usage instructions.
Run `rachis sylph --help` after installation to learn what actions are available.

Questions and bug reports should be directed to the [QIIME 2 Forum](https://forum.qiime2.org).

## sylph database notes

The plugin accepts only sylph's two-stage database format (`.syl2db`), which the sylph authors publish for GTDB r226 and r232; those are the releases `fetch-database` offers.
[GlobDB](https://globdb.org) publishes sylph databases for its r226 and r232 releases as well, but in the single-stage format so far; `fetch-database` will offer them when two-stage builds become available.
Until then, a GlobDB database can be used by downloading it, converting it with `sylph convert-db-two-screen`, and importing the result (`qiime tools import --type SylphTwoStageDatabase --input-format SylphTwoStageDatabaseFormat`); its genomes are not NCBI assemblies, so `profile-to-tables` would run with `--p-no-gtdb-ids`, and taxonomies and trees used for downstream analysis would need to be GlobDB's.

## AI disclosure

The code, tests and usage examples were written by Claude and reviewed function by function by @gregcaporaso; the commit history says what was requested and what the assistant implemented.
As of this writing (28 October 2026) all code has been reviewed, while usage example and unit test review is still pending.
Functions that are unreviewed are tagged in the [source code](https://github.com/gregcaporaso/mosh-sylph) with the comment line:

```
# TODO: this is AI-generated code; human review pending
```

[This search](https://github.com/search?q=repo%3Agregcaporaso%2Fmosh-sylph+%23+TODO%3A+this+is+AI-generated+code%3B+human+review+pending&type=code) will direct you to all of those lines.
