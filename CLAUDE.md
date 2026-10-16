# CLAUDE.md

Repository-local instructions for the mosh-sylph plugin (registered name `sylph`, module `mosh_sylph`, commands `rachis sylph <action>`); the global `~/.claude/CLAUDE.md` also applies.
The plugin is a nested repository inside the thermo-hec project directory, whose `CLAUDE.md` and memory (`thermo-hec-plugin-plan.md`) hold the project context; git commands use `git -C mosh-sylph` from the project directory.
It was split out of q2-confluence on 2026-10-16: thin wrappers of sylph and sylph-tax, one action per command, each returning the native output as its own format.

## Conventions (developer, 2026-10-13, carried over from q2-confluence)

 * Only registered actions are public functions; every other function, including usage-example functions, fixture factories, nested helpers and test helpers, starts with an underscore.
 * Every function body opens with `# TODO: this is AI-generated code; human review pending`, and every registered action's description ends with `EXPERIMENTAL: this is AI-generated code; human review pending.`; the developer deletes both as functions pass review.
 * An output name never repeats an input or parameter name (the CLI renders such an output as a second input); `tests/test_plugin_setup.py` enforces it.
 * Metadata and TSV column names use hyphens; action, parameter and output identifiers stay Python identifiers. `sample-id` is a reserved metadata ID header and cannot be a column name.
 * One concern per function and per commit; every action has one usage example and tests that compare it with a direct sylph or sylph-tax run on the fixture.
 * Commit messages name @gregcaporaso as the requester and say what Claude implemented, with the `Co-Authored-By` trailer; never push.

## Environment and checks

 * The development environment follows the QIIME 2 dev-environment guide (README, "Development installation"): the tiny distribution's `dev/latest/passed` environment file for the platform as base (native arm64 exists for tiny; the qiime2 distribution needs the guide's `CONDA_SUBDIR=osx-64` steps), then `environment-files/mosh-sylph-dev-extras.yml` (sylph 1.0.0, sylph-tax 1.9.2, pytest, flake8, q2lint) with `conda env update`; the developer creates it as the named env `mosh-sylph-dev`. Use it without activation: `PATH=$D/bin:$PATH CONDA_PREFIX=$D MPLCONFIGDIR=$TMPDIR/mpl NUMBA_CACHE_DIR=$TMPDIR/numba`; for `rachis ... --help` and `rachis dev refresh-cache`, unset `CONDA_PREFIX` and set `HOME=$TMPDIR/home`.
 * Until that env existed (2026-10-16) the code was developed in `qiime2-dev-2026-10-15` with sylph and sylph-tax unpacked from their bioconda packages into `$TMPDIR` and a `sitecustomize.py` limiting plugin discovery to q2-types, q2-metadata and mosh-sylph (that env's editable q2-taxa and q2-feature-table live in `~/4-git-repos`, which the sandbox cannot read). Prefer the real env.
 * Before every commit: `flake8`, `q2lint`, `python -m pytest -q` (under a minute), and render `rachis sylph <action> --help` for every changed signature.
 * rachis does not accept `Choices` on `Int`; `k` uses `Int % (Range(21, 22) | Range(31, 32))`.
 * sylph writes a header-only TSV when nothing is detected; sylph-tax taxprof writes no file for such a sample; sketches and profile/query/taxprof/merge outputs are byte-identical to direct runs on the same files, which is what the tests check.
