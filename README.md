# pyprojectgen

Version: 0.2.1

## Overview

### Purpose and scope

`pyprojectgen` creates a consistent starting point for Python projects: source and
test directories, package specifications, a virtual environment, and Git version
control. It is for developers familiar with basic Python and terminal commands
who want to reduce repeated setup work and configuration inconsistencies.

A **project** is the Python codebase being created, together with its tests,
package specifications, configuration, and setup script. **The generator** means
`pyprojectgen`; **the generated project** means the project it creates.

The generator supports initial setup, including an optional local staging check.
Afterward, you maintain the project and its package specifications. Production
deployment is outside the current tool's scope.

### Setup phases: inputs and outputs

| Phase | Input | Action | Output |
| --- | --- | --- | --- |
| **1. Configure the generator** | Your directory preferences, Git name/email, and optional GitHub settings | Create, edit, and validate `~/.pyprojectgenrc`. | Settings used to create projects. |
| **2. Create the project** | Configuration, project name, and selected Python version | Run `create` and respond to its prompts. | Project files, development `.venv`, and local Git repository. If configured, published GitHub code and an independently installed and tested local staging copy. |
| **3. Bootstrap development** | Generated project and its package specifications | Run the generated bootstrap script separately. | Required packages and project installed in development, with tests passed. |

Configure the generator once and reuse the settings for later projects. You can
complete the phases in one session or return to them later. Within Phase 2,
`create` automates its steps and pauses at confirmation prompts. On retry, it
checks existing resources and reuses compatible work; some interruptions or
conflicts require manual recovery. Retry guidance appears within each phase.

Optional local staging runs inside `create`, before the separate development
bootstrap command in Phase 3.

## Key terms

| Term | Meaning |
| --- | --- |
| Development | The project copy where you edit code. |
| Staging | An environment for testing changes before production. This tool provides only a limited **local staging** installation and test check, described in Phase 2. |
| Virtual environment (`.venv`) | The project's isolated Python environment. Development and local staging each have their own. |
| Bootstrap | The generated script that installs required packages and the development project, then runs its tests. |
| Pinned version | An exact recorded version used when recreating an environment. |

## Prerequisites

- macOS or Linux with Bash.
- Python 3.12 or newer to run the generator.
- Git installed and available through the `git` command.
- `~/.pyprojectgenrc` configured in Phase 1.

Git is mandatory. GitHub integration and local staging are optional.

## Phase 1: Configure the generator

### Create and edit the configuration

Run these commands from the `pyprojectgen` directory, the folder containing
`pyprojectgen.py`. The examples run the source directly; installing the generator
as a package is optional.

```bash
python3 pyprojectgen.py config-init
```

If the configuration file already exists, this command leaves it unchanged.
Edit `~/.pyprojectgenrc` using its comments as guidance.

| File created | Initial contents and purpose |
| --- | --- |
| `~/.pyprojectgenrc` | A commented configuration template. Fill in your settings before creating a project. |

The Git name and email used in the development directory must match the settings
in this file. For optional GitHub integration, SSH access must already work with
the configured host. The generator checks the configured key files, while SSH
selects the identity through your SSH configuration or agent. The generator does
not change your Git or SSH settings.

### Validate the configuration

```bash
python3 pyprojectgen.py config-validate
```

Correct reported errors before creating a project. Warnings about unconfigured
GitHub settings are expected for local-only use. This command checks settings and
local paths. The `create` command also checks your Git name/email and, if
configured, GitHub access.

### Retrying configuration

Edit the existing file and rerun `config-validate` until errors are resolved.
Rerunning `config-init` preserves the existing file rather than replacing it.

## Phase 2: Create the project

Run commands in this phase from the `pyprojectgen` directory. The examples use
`demo` as the project name; replace it with your own project name.

### Select the Python version

Use `--python X.Y.Z` to select the exact Python version for the project's
development and local staging virtual environments. That version must already
be installed and discoverable by the generator.

New projects currently default to **3.12.10** and require that exact installed
version. A newer version alone does not satisfy the default. To use an installed
Python 3.12.14 instead, add `--python 3.12.14` to the commands below. The generator
does not install Python or automatically substitute another version.

### Preview with `--dry-run`

```bash
python3 pyprojectgen.py create demo --dry-run
```

Use the preview to review what will be created or reused and catch configuration
problems before making changes. It leaves project files unchanged and asks for no
confirmations. If GitHub is configured, it still tests SSH access. Package
installation and final remote-commit verification occur during actual execution.

### Run the `create` command

After reviewing the preview, run the command without `--dry-run`, retaining any
`--python` option you selected:

```bash
python3 pyprojectgen.py create demo
```

### Automated steps and outputs

`create` performs these steps in order:

| Step | Purpose |
| --- | --- |
| Validate | Check configuration, independent development/staging paths, selected Python version, project name, and Git. |
| Create directories | Prepare the development project directory structure. |
| Create the environment | Record the Python version and create or validate the development `.venv`. |
| Initialize project files | Create and populate the initial project files listed below. |
| Initialize Git | Initialize `main` if needed and check the Git name/email. |
| Commit | Ask before staging all unignored project files and committing them. |
| Connect to GitHub, if configured | Check SSH access, configure `origin`, and ask before pushing. |
| Set up local staging, if configured | Verify the published commit, clone it independently, install the project and packages, and run tests. |

Development outputs below are relative to
`<development_root>/<project_name>`. `development_root` is the setting in
`~/.pyprojectgenrc`; `project_name` is the name supplied to `create`. Replace
angle-bracket placeholders with your values before running commands.

| Creating step | Directory or file | Initial contents and purpose |
| --- | --- | --- |
| Create directories | Project directory; `src/<project_name>/`, `tests/`, `scripts/`, `.vscode/` | Locations for source, tests, scripts, and editor settings. |
| Create the environment | `.venv/` | Development Python environment, ready for Phase 3 installation. |
| Create the environment | `.python-version` | The selected exact Python version; checked again during file initialization. |
| Initialize project files | `pyproject.toml` | Project name, initial version `0.1.0`, exact Python requirement, setuptools build requirement, pytest test dependency, and package/test settings. Application dependencies start empty. |
| Initialize project files | `requirements-bootstrap.txt` | Exact versions of pip and setuptools used for installation. |
| Initialize project files | `requirements.txt` | Exact versions of pytest and its dependencies: iniconfig, packaging, pluggy, and Pygments. |
| Initialize project files | `src/<project_name>/__init__.py` | An empty Python package. |
| Initialize project files | `tests/test_import.py` | A test that imports the generated package. |
| Initialize project files | `scripts/bootstrap.sh` | Executable development installation and test script. |
| Initialize project files | `.gitignore` | Exclusions including `.venv`, caches, build output, and `.env`. |
| Initialize project files | `.env.example` | A commented placeholder for application environment variables. |
| Initialize project files | `.vscode/settings.json` | VS Code setting pointing to the project's `.venv`. |
| Initialize project files | `README.md` | Initial instructions for the generated project. |
| Initialize Git | `.git/` | Local Git history and repository settings. Later commit and remote steps update it. |
| Set up local staging | `<stage_root>/<project_name>/` and its `.venv/` | Verified source checkout and independently installed environment. `stage_root` comes from `~/.pyprojectgenrc`. |

In package metadata, underscores in the project name become hyphens, for example
`invoice_tools` becomes `invoice-tools`.

### Confirmation prompts

The three possible prompts are to create the initial commit, confirm that the
GitHub repository exists, and push the branch. Each defaults to No. Declining
retains completed work and stops dependent steps. Completed actions may be skipped
on retry. Inspect the project before approving a commit: it uses `git add .`.

If asked to create the GitHub repository, create an empty repository under the
configured owner with the project name, then confirm. GitHub repository creation
is manual. With integration unconfigured, `create` finishes its local portion and
skips GitHub and local staging. Invalid integration settings can stop execution.

### Local staging: purpose and limitations

Production-like staging should test the intended deployment method and relevant
runtime conditions before production. **The current local staging function is
much more limited: it checks package installation and runs project tests in a
separate environment.**

After publication, the generator verifies that the live GitHub branch matches
the development commit. It clones into the local staging directory and checks out
that exact commit directly, using detached HEAD mode. It creates a separate
`.venv`, installs the committed tools and test dependencies, installs the project
non-editably, checks dependency compatibility, and runs pytest. Non-editable
installation uses an installed package copy rather than linking to development
source. An existing staging copy must have the intended remote and commit and no
local or untracked changes.

This does not provision or validate a production-like deployment, containers,
databases, application services, networking, or application startup. It builds and
installs from the checked-out source rather than testing a separately supplied
production artifact. The generated import test is not application acceptance
or production-readiness testing.

Local staging is inexpensive and quick, but shares a machine with development:

| Limitation or risk | Consequence |
| --- | --- |
| Same operating system and machine setup | Machine-specific assumptions and differences from production may remain undetected. |
| Shared CPU, memory, and storage | Workloads can compete for resources; a machine failure affects both environments. |
| Same user permissions | Separate directories and `.venv` environments are not a security boundary. Code running as that user can access both locations. |

Moving this check to another machine alone would not provide full deployment
validation. Remote staging with production-like installation is planned; see
[Planned features](#planned-features).

### Retrying `create` and recovering from errors

Correct the reported cause and rerun the same `create` command from the
`pyprojectgen` directory. Compatible resources are reused; conflicts stop execution
without overwriting your files. Resumption checks the directories, files, and
Git state already present.

On retry, omitting `--python` uses the project's recorded `.python-version`.
Requesting a different version stops execution. A mismatched or incomplete
`.venv` requires manual review; it is not automatically deleted and rebuilt.

Generated files must match the initial templates. The generator does not merge
edits or update established projects. A matching bootstrap script with missing
executable permission has that permission restored. Stale or conflicting staging
copies are not automatically pulled, reset, or deleted.

Until initial setup completes, let the setup commands manage `.venv`. If a manual
repair is needed, preserve the declared package specifications.

#### Interrupted staging checkout recovery

An interruption between clone and checkout can leave Git history without source
files. The generator stops for review rather than resetting the directory.

1. Inspect the staging directory and its `git status`. Missing files alone do not
   distinguish an interrupted checkout from user changes.
2. Preserve the entire staging project directory by moving it to a separate,
   unused backup location outside the development checkout.
3. Once the intended staging project path is absent, rerun `create`. Keep the
   backup until the fresh staging setup succeeds.

The same approach applies to a partial staging clone. Preserve the development
project and keep its environment separate.

## Phase 3: Bootstrap development

### Run the bootstrap script

Run the generated bootstrap script to install the required packages and the
project in development, then run its tests:

```text
cd <development_root>/<project_name>
./scripts/bootstrap.sh
```

Use `development_root` from `~/.pyprojectgenrc` and the project name supplied to
`create`. Bootstrap reads the populated project specifications from Phase 2;
it does not populate or update them.

### Installation steps and outputs

| Step | Result in the development project |
| --- | --- |
| Check Python and environment | Find the recorded Python version; create `.venv/` if missing, or check its Python version if it exists. |
| Install tools | Install pip and setuptools from `requirements-bootstrap.txt` into `.venv/`. |
| Install test dependencies | Install pytest and its four dependencies from `requirements.txt` into `.venv/`. |
| Install the project | Read `pyproject.toml` and install the project into `.venv/` in editable mode. Source edits are available without reinstalling. |
| Validate | Check dependency compatibility and run the generated import test with pytest. |

The initial specifications contain seven external packages: two installation
tools and five test packages. The generated project itself is also installed.
A successful run ends with `[OK] Bootstrap complete`.

Initial setup is complete when the requested Phase 2 actions and development
bootstrap succeed. You can then begin development. To run project tests again:

```bash
.venv/bin/python -m pytest
```

### Retrying bootstrap

After correcting an error, rerun `./scripts/bootstrap.sh` from the generated
project directory. It retries installation and tests using the recorded
specifications. It reuses an existing `.venv`; it does not automatically repair
an incomplete environment, replace a wrong Python version, or remove extra
packages. Review environment conflicts manually before retrying.

## Testing the generator

These tests check `pyprojectgen` itself. Run them from the `pyprojectgen`
directory, not the generated project directory.

### Run the tests

Regression checks without package installation:

```bash
python3 -m unittest discover -s tests -v
```

Full suite, including development/local staging installation and reproduction:

```bash
PG_RUN_INSTALL_TESTS=1 python3 -m unittest discover -s tests -v
```

`PG_RUN_INSTALL_TESTS` is the suite's custom opt-in switch. The inline assignment
sets it to `1` for this command; no configuration file or persistent setting is
needed. Otherwise the installation test is skipped, unless the variable is
already exported as `1`. `unittest discover` finds tests under `tests/`, and
`-v` prints individual results.

To run only the installation/reproduction test:

```bash
PG_RUN_INSTALL_TESTS=1 python3 -m unittest discover -s tests \
  -p test_setup.py -k test_real_development_bootstrap -v
```

The current suite has 23 tests: the full run should pass all 23; the default run
should pass 22 and skip one. A skipped test did not run. Failures and errors
require investigation. See [VALIDATION.md](VALIDATION.md) for recorded results.

### Test design and temporary projects

The generator's suite uses `unittest`. Its installation test runs the generated
projects' pytest tests inside their own environments. Pytest is not required in
the environment running the generator's suite.

Tests create isolated workspaces with `tempfile.TemporaryDirectory()`, using test
configuration instead of your configured project directories. Workspaces contain
temporary development projects, local Git repositories, staging copies, and
virtual environments. They normally live under `/var/folders/.../T/` on macOS or
`/tmp/` on Linux, depending on system settings.

Cleanup runs after normal completion, including ordinary test failures. Forced
termination or a crash can leave files behind. Pip's download cache may remain
outside these workspaces.

Some checks run actual commands; others simulate operations and confirmation
responses. The full installation test executes development bootstrap, publishes
to a local Git remote, installs and tests a separate staging copy, compares package
versions, and retries staging. It needs Git, Bash, Python 3.12 or newer, and access
to the pinned packages. It uses the Python version running the suite. No manual
responses or personal GitHub access are required; live GitHub authentication and
production deployment are not covered.

## Recreating environments and current limits

Keep the source revision and package specifications together in Git. Recreate
`.venv` locally from those specifications and the recorded Python version rather
than copying it between machines. Maintain the specifications as dependencies
change after initial setup.

Pinned versions assume compatible operating systems and architectures and
available packages. They do not provide an offline package archive or guarantee
byte-identical builds. Installation checks do not detect every unexpected extra
package in an existing environment.

## Planned features

The following are not implemented:

- Separate invocation of local staging after development bootstrap, as a fourth
  phase. Local staging currently remains inside `create` (BL-001).
- Remote staging with production-like artifact installation and runtime checks
  (BL-002).
- Detection and reporting of unexpected installed packages. Automatic package
  removal is outside the current implementation.

See [BACKLOG.md](BACKLOG.md) for the staging enhancement scope and decisions.

## Command reference

| Command | Purpose |
| --- | --- |
| `python3 pyprojectgen.py --help` | Show commands. |
| `python3 pyprojectgen.py config-init` | Create the configuration template if missing. |
| `python3 pyprojectgen.py config-validate` | Validate configuration without modifying it. |
| `python3 pyprojectgen.py create NAME` | Run the automated creation workflow. |
| `python3 pyprojectgen.py create NAME --python X.Y.Z` | Select the exact Python version for the project's environments. |
| `python3 pyprojectgen.py create NAME --dry-run` | Preview creation without changing project resources. |

An installed `pyprojectgen` command accepts the same arguments. There are no
separate generator commands for bootstrap, staging, or production deployment.
Development bootstrap is the generated script run in Phase 3.

### Exit codes

| Code | Meaning |
| --- | --- |
| `0` | Success, including preview or creation with optional integration unconfigured. |
| `1` | Configuration, validation, or execution error. |
| `2` | Invalid command-line arguments. |
| `3` | A confirmation was declined; dependent steps stopped. |
| `130` | Execution was interrupted or confirmation input unavailable. |

These are generator CLI exit codes. The separate bootstrap script exits nonzero
if a command fails.

## Further information

- [BACKLOG.md](BACKLOG.md): planned enhancements and deferred work.
- [CHANGES.md](CHANGES.md): release changes and source-preservation history.
- [VALIDATION.md](VALIDATION.md): recorded test runs and limitations.
- [REPLACEMENT.md](REPLACEMENT.md): replacing an earlier generator version.
- [AGENTS.md](AGENTS.md): maintenance instructions for coding assistants.

## License

MIT. See [LICENSE](LICENSE).
