# mosh-sylph: a [rachis](https://rachis.org) plugin for use with QIIME 2 and/or MOSHPIT

> ⚠️ This plugin is in early testing (alpha release) phase. Interfaces will almost certainly change. Be skeptical of results - testing is still in progress.

`mosh-sylph` (registered name `sylph`; `rachis sylph --help`) wraps the [sylph](https://sylph-docs.github.io/) metagenome profiler (Shaw & Yu, *Nature Biotechnology* 2025): each action runs one sylph command and returns the tool's own output as an artifact, and two conversion actions turn those outputs into stock types keyed by GTDB genome ID, so that GTDB's own taxonomy file and tree serve as taxonomy and phylogeny.

The documentation is the tutorial, [thermo-hec-tutorial](https://gregcaporaso.github.io/thermo-hec-tutorial/) ([source](https://github.com/gregcaporaso/thermo-hec-tutorial)), which uses this plugin with [q2-confluence](https://github.com/gregcaporaso/q2-confluence) and says how to create an environment with both; `rachis sylph <action> --help` is the action reference.

Development: create the tutorial's environment, then `make dev`, `make test` and `make lint` from this directory.

The code, tests and usage examples were written by Claude and reviewed function by function by @gregcaporaso; the commit history says what was requested and what the assistant implemented.
Questions and bug reports go to the [QIIME 2 Forum](https://forum.qiime2.org).
