# CLAUDE.md

Repository-local instructions for the mosh-sylph plugin (registered name `sylph`, module `mosh_sylph`, commands `rachis sylph <action>`); the global `~/.claude/CLAUDE.md` also applies.
The plugin is a nested repository inside the thermo-hec project directory, whose `CLAUDE.md` and memory (`thermo-hec-plugin-plan.md`) hold the project context; git commands use `git -C mosh-sylph` from the project directory.
It was split out of q2-confluence on 2026-10-16: thin wrappers of sylph, one action per command, each returning the native output as its own format; the sylph-tax wrappers were removed on 2026-10-21 (developer's decision: the workflow hands off genome-keyed tables and GTDB's own taxonomy), recoverable at commit 3d133a4.

## Conventions (developer, 2026-10-13, carried over from q2-confluence)

 * Commands in documentation (README, help text examples) are split one parameter per line with `\` continuations, as in the tutorial; the README points readers to the tutorial for the artifact cache instead of explaining it (developer, 2026-10-19).

 * Only registered actions are public functions; every other function, including usage-example functions, fixture factories, nested helpers and test helpers, starts with an underscore.
 * Every function body opens with `# TODO: this is AI-generated code; human review pending`, and every registered action's description ends with `EXPERIMENTAL: this is AI-generated code; human review pending.`; the developer deletes both as functions pass review.
 * An output name never repeats an input or parameter name (the CLI renders such an output as a second input); `tests/test_plugin_setup.py` enforces it.
 * Metadata and TSV column names use hyphens; action, parameter and output identifiers stay Python identifiers. `sample-id` is a reserved metadata ID header and cannot be a column name.
 * One concern per function and per commit; every action has one usage example and tests that compare it with a direct sylph run on the fixture.
 * Commit messages name @gregcaporaso as the requester and say what Claude implemented, with the `Co-Authored-By` trailer; never push.

## Environment and checks

 * The development environment follows the QIIME 2 dev-environment guide (README, "Development installation"): the tiny distribution's `dev/latest/passed` environment file for the platform as base (native arm64 exists for tiny; the qiime2 distribution needs the guide's `CONDA_SUBDIR=osx-64` steps), then `environment-files/mosh-sylph-dev-extras.yml` (sylph 1.0.0, pytest, flake8, q2lint) with `conda env update`; the README names it by creation date (`mosh-sylph-dev-$(date "+%Y-%m-%d")`, the developer's convention), and the developer creates it. Use it without activation: `PATH=$D/bin:$PATH CONDA_PREFIX=$D MPLCONFIGDIR=$TMPDIR/mpl NUMBA_CACHE_DIR=$TMPDIR/numba`; for `rachis ... --help` and `rachis dev refresh-cache`, unset `CONDA_PREFIX` and set `HOME=$TMPDIR/home`.
 * The local environment is still the undated `mosh-sylph-dev`, created 2026-10-16 before the dated convention (osx-arm64; rachis 2026.10.0.dev0+8, sylph 1.0.0, sylph-tax 1.9.2 still installed but unused, plugin editable); flake8, q2lint, the full suite (42 tests + 13 subtests, 11 s) and `rachis info` / `rachis sylph --help` all pass there. Before it existed the code was developed in `qiime2-dev-2026-10-15` with sylph and sylph-tax unpacked from their bioconda packages into `$TMPDIR`; that stand-in is gone.
 * Before every commit: `flake8`, `q2lint`, `python -m pytest -q` (under a minute), and render `rachis sylph <action> --help` for every changed signature.
 * rachis does not accept `Choices` on `Int`; `k` uses `Int % (Range(21, 22) | Range(31, 32))`.
 * Actions take and return the single-file formats (`SylphTwoStageDatabaseFormat`, `SylphProfileFormat`, ...) and address them as `str(fmt)`; the framework converts to and from the `SingleFileDirectoryFormat`s, so no action or test names a member file (`profile.tsv`). Only the multi-file format (sketches) is handled as a directory (developer, 2026-10-19).
 * sylph writes a header-only TSV when nothing is detected; sketches and profile/query outputs are byte-identical to direct runs on the same files, which is what the tests check.

## Status and ownership

 * The session that built and reviewed the plugin closed on 2026-10-16 (build by Opus 5.5, review pass by Fable 5.1; the history is the record, one concern per commit). Any session may edit this repository with the developer's say-so; the thermo-hec project's `CLAUDE.md` names the current arrangement.
 * Remote: `origin` is `gregcaporaso/mosh-sylph` (private). Claude never pushes; the developer pushes after reviewing.
 * The tutorial that uses the plugin lives in `thermo-hec-tutorial/` (pins this plugin by commit in its extras file; repin and re-render when an action's CLI changes). The parent project's `slurm/tutorial.sbatch` runs that page on bacon with both plugins; a plugin change is tested there by re-shipping the `git archive` tarball at the commit under test.
 * The developer's function-by-function review (deleting the `TODO` and `EXPERIMENTAL` markers) has not started. Known limitations left on purpose, for that review to weigh: `fetch-database` has no resume, retry or checksum for the 19 GB download; `read_seq_id` without `estimate_unknown` passes through and sylph ignores it; `profile-to-tables` takes the sketches only for the sample list.
