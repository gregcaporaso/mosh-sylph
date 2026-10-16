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
