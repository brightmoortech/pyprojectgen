# pyprojectgen

Version: 0.2.1

A generic command-line utility for initial Python project setup. It creates a
source template and isolated development environment, optionally publishes the
initial source to GitHub, and reconstructs a separate staging environment.
It finishes when initial setup is complete. After handover, the project owner
maintains the generated files and dependency specifications.

## Prerequisites

- macOS is the primary supported platform; commands use POSIX paths and Bash.
- Python 3.12 or newer to run the generator.
- The exact Python version selected for the generated project must already be
  installed. The generator does not download Python or substitute another version.
- Git on PATH and an effective Git name/email matching the configuration.
- Network/package-index access for bootstrap and staging installations.
- For optional GitHub integration: an existing GitHub repository, SSH access,
  and configured SSH key files. SSH uses the configured host/alias and agent;
  key paths are checked but are not passed as explicit SSH identity arguments.

The generator's interpreter can differ from the generated project's interpreter.
No project-specific deployment system, database, Docker configuration, or
credentials are embedded in the template.

## Configuration

```bash
python3 pyprojectgen.py config-init
```

Edit `~/.pyprojectgenrc`, using `pyprojectgenrc.example` as a reference. The file
contains absolute development/staging roots, expected Git identity, and optional
GitHub owner, SSH host, and key paths. Do not store passwords, tokens, or key
contents. For separate environments, choose distinct roots that do not contain
one another. Validation rejects roots that resolve to the same directory and
project paths or `.venv` paths that alias one another, including existing symlinks.
Different nested roots are not otherwise prohibited.

```bash
python3 pyprojectgen.py config-validate
```

This checks configuration structure and local paths; it does not install Python
or prove GitHub authentication. Existing configuration is never overwritten.

## Implemented commands

```bash
python3 pyprojectgen.py --help
python3 pyprojectgen.py config-init
python3 pyprojectgen.py config-validate
python3 pyprojectgen.py create demo --python 3.12.10 --dry-run
python3 pyprojectgen.py create demo --python 3.12.10
```

Installed console entry point: `pyprojectgen` accepts the same arguments.
There are no separate `bootstrap`, `github`, `stage`, or project `validate`
commands. Development bootstrapping is a generated project script.

`--python X.Y.Z` selects an exact interpreter version. New projects default to
`3.12.10`; reruns without the option use the project's `.python-version`.
An explicit conflicting version fails. Interpreter discovery checks the running
interpreter, `pythonX.Y`, `python3`, and the macOS Python framework location.
Unavailable versions fail before project resources are created.

## Guided workflow

| Phase | Behavior |
| --- | --- |
| Preflight | Validate configuration, selected interpreter, project name, and Git. |
| Project structure | Create project, `src/<name>`, `tests`, `scripts`, and VS Code directories. |
| Python environment | Record the selected version; create or validate an isolated `.venv`. |
| Project files | Create the fixed template and dependency/bootstrap specifications. |
| Git repository and identity | Initialize `main` if missing and verify effective Git identity. |
| Initial commit | Ask before staging all unignored files with `git add .` and committing. |
| GitHub checks | Validate configured keys and test SSH authentication. |
| Remote | Ask whether the manually created repository exists before adding a missing `origin`. |
| Initial push | Ask before pushing the current branch and setting its upstream. |
| Staging | Verify the live remote branch tip equals development HEAD, reconstruct that exact commit, install, and test. |

The three confirmation gates default to No. Declining stops the dependent work.
GitHub configuration requires owner, SSH host, private-key path, and public-key
path. With integration unconfigured, the workflow finishes its local portion
and skips GitHub/staging. Configured but invalid settings stop with an error.
The generator does not create GitHub repositories or change global Git/SSH settings.

For staging, the selected version is the current development branch HEAD after
publication, not whichever branch the remote names as default. A live remote
mismatch stops setup for user review. A fresh clone checks out the verified
commit in detached HEAD mode. An existing clone must have the expected origin,
exact commit, and clean tracked/untracked state. Stale or conflicting checkouts
are not automatically pulled, reset, or deleted. Review them manually and rerun.
Staging checks freshness at verification time; it does not monitor later remote changes.

## Development bootstrap and reproduction

`create` prepares the development `.venv` but does not install development
packages or run development tests. Complete that work from the generated project:

```bash
./scripts/bootstrap.sh
```

| Generated specification | Purpose |
| --- | --- |
| `.python-version` | Exact selected interpreter version. |
| `pyproject.toml` | Same exact Python requirement, package metadata, exact setuptools build requirement, and pytest extra. |
| `requirements-bootstrap.txt` | Exact pip and setuptools versions. |
| `requirements.txt` | Exact pytest and transitive test-dependency versions. |
| `scripts/bootstrap.sh` | Find exact Python, create/validate `.venv`, install pins, install editable project, check dependencies, run tests. |

Bootstrap installs tooling first, then dependencies, then the project with
`--no-build-isolation --no-deps`. This prevents project installation from
selecting additional build-tool or dependency versions. Staging uses the same
pins and a non-editable project installation, then dependency checks and pytest.
The starter package has no runtime dependencies. Listed test dependencies and
bootstrap tools are fixed template defaults, not a snapshot of the host environment.

Commit the specifications and source; exclude `.venv` and secrets. Recreate each
environment from the same revision with the specified Python version on a
compatible OS/architecture. Do not copy `.venv` or `pyvenv.cfg` between locations.
Package version pins do not constitute an offline artifact archive or guarantee
byte-identical builds. Artifact hashes, retained wheels, system libraries, and
cross-platform dependency locks are outside the current scope. Development and
staging intentionally differ in editable versus non-editable package installation.

## Failure, interruption, and restart

Every phase reports `OK`, `CREATE`, `SKIP`, `WARNING`, or `ERROR`. Errors stop
execution. Completed changes remain; no rollback is attempted. Rerun `create`
to inspect resources from the beginning, skipping compatible existing work.
There is no saved phase-position ledger.

The generator is for the initial template before user edits. Existing generated
files must match the expected template; mismatches stop setup and preserve the
files. If matching bootstrap content lacks executable permission, execution
restores that permission; dry-run only reports the required repair. It does not
merge edits, adopt older generated templates automatically,
or maintain a project after development starts. Review conflicts manually.
The generated bootstrap can be rerun but does not remove unexpected extra packages;
use a fresh environment when checking reproduction.

| Exit code | Meaning |
| --- | --- |
| 0 | Requested operation succeeded, including intentionally unconfigured optional integration or dry-run. |
| 1 | Configuration, prerequisite, validation, or execution failure. |
| 2 | Invalid command-line usage (argparse). |
| 3 | User declined a guided confirmation; dependent setup was not completed. |
| 130 | Interrupted execution or unavailable confirmation input. |

Dry-run plans creation without writing project resources or prompting for changes.
If GitHub is configured, it still tests SSH authentication over the network.
Remote staging-revision verification and package installation are deferred;
a successful preview does not establish that those operations will succeed.

### Interrupted staging checkout recovery

An interruption after clone but before checkout can leave a Git directory without
its source files. The tool stops without resetting the directory; it does not
attempt automatic recovery or assume that missing files are safe to overwrite.

1. Inspect the staging project's Git status and files. Missing tracked files can
   mean an unfinished checkout or real user changes; do not infer which from the
   status alone.
2. If uncertain, preserve the entire staging project directory in a separate,
   previously unused backup location outside the development checkout. Move the
   whole directory rather than deleting files or using a forced Git reset.
3. Once the intended staging project path is absent, rerun the same `create`
   command. It revalidates development and GitHub state and creates a fresh staging
   clone at the verified commit. Retain the backup until setup succeeds.

The same preserve-and-retry approach is available for a failed partial staging
clone. Do not apply it to development or delete a shared environment.

## Validation

### Test design

The generator's automated tests are in `tests/test_setup.py` and use Python's
built-in `unittest` framework. They do not require pytest in the interpreter
running the suite. The generated projects use pytest: the opt-in installation
test installs and runs pytest inside their own virtual environments.

The regression checks exercise configuration, interpreter selection, generated
files, Git operations, confirmation gates, failure handling, and setup resumption.
Some checks execute real commands in temporary projects. Others use mocks
(controlled substitutes for operations and responses), including the controller
check for confirmation gates and GitHub actions. The suite runs without manual
answers and does not authenticate to a personal GitHub account or operate on a
live deployment.

The opt-in installation test performs actual development bootstrap, dependency
installation, and pytest execution. It publishes to a temporary local Git remote,
clones a separate staging project, installs it non-editably, runs its tests,
compares installed package versions between development and staging, and retries
staging setup. This verifies local environment reconstruction; it does not prove
live GitHub SSH access or compatibility with every OS/Python version.

### Temporary projects and cleanup

Each test creates a separate workspace using `tempfile.TemporaryDirectory()`.
Projects, local Git repositories, staging copies, and `.venv` directories needed
by that test live beneath this workspace. Test configuration points to these
locations, separate from the user's configured development and staging projects.

Python chooses an OS temporary location, which can be influenced by settings
such as `TMPDIR`. On macOS it is commonly under `/var/folders/.../T/`; on Linux
it is often under `/tmp/`. The exact path is generated at runtime, not hardcoded.
To see the temporary root Python currently selects, run:

```bash
python3 -c "import tempfile; print(tempfile.gettempdir())"
```

The suite registers cleanup for each workspace. It removes the workspace after
normal completion, including ordinary test failures. Forced process termination
or a system crash can leave temporary files behind. Package downloads may also
populate pip's normal cache outside these workspaces; workspace cleanup does not
clear that cache.

### Running the tests

Run these commands from the repository root, which contains `pyprojectgen.py`
and the `tests` directory. Use Python 3.12 or newer, with Git and Bash available.
The temporary projects use the Python version running the suite; run with the
intended interpreter to validate that version.

Fast regression checks, without package installation:

```bash
python3 -m unittest discover -s tests -v
```

`-m unittest` starts Python's test runner. `discover -s tests` finds test files
named `test*.py` under `tests`; `-v` prints each test's name and result. With no
installation-test opt-in, the installation/reproduction test is reported as
skipped. The current suite discovers 23 tests: 22 run and one is skipped.

Run all checks, including package installation and environment reproduction:

```bash
PG_RUN_INSTALL_TESTS=1 python3 -m unittest discover -s tests -v
```

`PG_RUN_INSTALL_TESTS` is a custom switch read by this suite, not a built-in Python
setting. The shell assignment at the start of this command supplies the text value
`1` to this Python process and its child processes. No `.env` file or persistent
configuration is needed. With no prior exported setting, omitting the assignment
leaves the installation test disabled. The inline assignment does not change the
parent shell's existing value. Only the exact value `1` enables the test.

To run only the installation/reproduction test:

```bash
PG_RUN_INSTALL_TESTS=1 python3 -m unittest discover -s tests \
  -p test_setup.py -k test_real_development_bootstrap -v
```

Installation checks require access to the pinned packages through the configured
package index, cache, or a local wheel source supplied through pip configuration.
No temporary directory from a previous run is needed: each run creates its own.
An `ok` result means a check passed; `skipped` means it did not run. `FAIL` or
`ERROR` requires investigation, and the runner returns a nonzero exit status.

See `VALIDATION.md` for measured results and platform limitations, and `CHANGES.md`
for release changes and the source-preservation map.

## Setup ownership and future enhancement

Until initial setup completes, the workflow controls `.venv`; do not manually
change its packages except when a repair is required. Repairs must preserve the
declared dependency specifications. Normal interrupted installations may be retried.

**Future enhancement (not implemented):** detect installed packages outside the
specified initial environment and report them for review. Such packages can arise
from a reused foreign environment or manual intervention; their presence has not
been demonstrated as a result of the normal workflow. This is not a current release
blocker under the setup-ownership rule. Do not remove packages automatically.

## License

MIT. See `LICENSE`.
