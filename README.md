# pyprojectgen

**Version 0.2.1 · macOS and Linux · Python 3.12+**

## 1. What is pyprojectgen?

`pyprojectgen` creates the starting structure for a **new Python project**: folders for your code and tests, starter files, a separate Python environment (`.venv`), and a local Git repository. This saves you from setting up the same pieces for every project. If configured, it can also push the first commit to GitHub and test a separate local copy of the project.

This guide assumes you know basic Python and terminal commands. The generator creates the **initial** project; you maintain the code and dependencies afterward. It does not deploy applications to production.

Set up your first project in three phases:

| Phase | What you do | What you get |
| --- | --- | --- |
| **1. Configure** | Enter and validate your preferences once. | Reusable settings for future projects. |
| **2. Create** | Name the project, use the default Python version or choose another, and respond to prompts. | Project structure, starter files, `.venv`, and local Git repository; optional GitHub publishing and staging check. |
| **3. Bootstrap** | Run the script created in your new project. | Development project and test packages installed; starter test run. |

Phase 2 creates the development environment, but **Phase 3 is required to install the project and run its initial test**. Optional GitHub publishing and staging occur during Phase 2.

## 2. What do I need?

- **macOS or Linux** with Bash.
- **Python 3.12 or newer** to run `pyprojectgen`.
- **Git** installed and available as `git`, with a name and email configured for commits.
- An **exact Python version** for the new project. The default is **3.12.10**, which must be installed even if you have a newer version. You can instead specify another installed version with `--python X.Y.Z` (for example, `--python 3.12.14`).
- Access to the required Python packages from your configured package index when running bootstrap (normally an internet connection).

Check your environment in a terminal:

```bash
python3 --version
git --version
git config user.name
git config user.email
```

If either Git value is blank, configure it in Git before continuing. In the current release, you must repeat the **same name and email** in the generator's configuration (Section 4). The generator checks the effective Git values where it creates the project and does not change them.

GitHub is **optional**. If you want it, you also need a GitHub account or organization, working SSH access, and existing SSH key files; see [Section 8](#8-what-are-the-optional-capabilities).

## 3. How do I install or run pyprojectgen?

**Use the source folder for this release.** Download the repository ZIP and extract it, or clone the repository. Open a terminal in the `pyprojectgen` folder containing `pyprojectgen.py`.

Whenever you run a generator command in this guide, use that folder. You can keep the source folder and reuse it to create additional projects.

Verify that it runs:

```bash
python3 pyprojectgen.py --help
```

You should see the `config-init`, `config-validate`, and `create` commands. The commands in this guide run directly from the source; no installation step is needed for that method. The package also supports installation as a Python CLI, but the all-users installer is not implemented. Proposed installation improvements are tracked in [BACKLOG.md](BACKLOG.md).

All generator commands below use `python3 pyprojectgen.py` from the source folder. Bootstrap and project tests run from the generated project folder.

## 4. How do I configure it? (Phase 1)

Each user creates their own `~/.pyprojectgenrc` file once. It tells the generator where to put projects and whether to use GitHub. You can edit it later when your preferences change.

**Step 1: Create the configuration file.** From the generator source folder:

```bash
python3 pyprojectgen.py config-init
```

This creates `~/.pyprojectgenrc` in your home directory if it does not exist; an existing file is left unchanged. Open the file in a text editor and enter your settings. Here is a **local-only example** (replace the paths, name, and email; keep the GitHub and SSH values empty):

```toml
[paths]
development_root = "/absolute/path/to/develop"
stage_root = "/absolute/path/to/stage"

[github]
organization = ""
ssh_host = ""

[git]
user_name = "Your Git Name"
user_email = "you@example.com"

[ssh]
private_key = ""
public_key = ""
```

| Setting | Your responsibility | What pyprojectgen does |
| --- | --- | --- |
| `paths.development_root` | Set an absolute path for development projects. | Creates `<development_root>/<project_name>` during project creation. |
| `paths.stage_root` | Set a **different**, independent absolute path, even if you won't use staging. | Uses it only when optional staging runs. |
| `git.user_name`, `git.user_email` | Match the effective `git config user.name` and `git config user.email`. | Checks that they match; does not change Git settings. |
| `github.*`, `ssh.*` | Leave values empty for local-only use. | Skips GitHub and staging when integration is not configured. |

Use two different paths for development and staging, preferably in separate sibling directories. Both must be writable by your user or available to create. The generator creates the project-specific subdirectory; you do **not** create it yourself. GitHub/SSH settings are explained in [Section 8](#8-what-are-the-optional-capabilities).

**Step 2: Validate the file.**

```bash
python3 pyprojectgen.py config-validate
```

Correct any errors and rerun validation. Warnings about GitHub being unconfigured are normal for local-only use. **You can proceed when validation reports success, including success with GitHub warnings.** The generator will not create a missing configuration file when you run `create`.

## 5. How do I create my first project? (Phase 2)

We'll create a local project named `demo`. For the first run, leave GitHub/SSH values empty in the configuration. Run these commands from the **generator source folder**, not the directory where `demo` will be created.

**Step 1: Preview the project.**

```bash
python3 pyprojectgen.py create demo --dry-run
```

The preview checks the configuration and planned actions without creating project resources or asking for confirmations. It also checks SSH access if GitHub integration is configured.

If Python **3.12.10** is not installed, supply another exact version you already have. For example, with Python 3.12.14:

```bash
python3 pyprojectgen.py create demo --python 3.12.14 --dry-run
```

**Step 2: Create the project.** Keep the same Python version you used for the preview:

```bash
python3 pyprojectgen.py create demo
```

If you previewed with the alternate Python version, run this instead:

```bash
python3 pyprojectgen.py create demo --python 3.12.14
```

The generator creates the project folder, `.venv`, and starter files, then initializes Git on `main`. It asks whether to make the first commit. **`y` approves; Enter or `n` declines** (the default is No). The commit stages all unignored files using `git add .`. If you want to review them first, decline, inspect the project, then rerun the same `create` command to reach the commit prompt again. Declining does not undo files already created.

With the local-only configuration in this example, creation stops after the Git steps. If you enable GitHub publishing, additional work runs during this phase; see [Section 8](#8-what-are-the-optional-capabilities).

After the local creation steps finish, your files are in `<development_root>/demo`. **You still need to bootstrap the development environment** (Section 7). Before that, Section 6 shows you what was created.

## 6. What did the tool create?

Look in the project folder under your configured development root. For the example named `demo`, you'll find:

```text
<development_root>/demo/
├── src/demo/__init__.py         # Python source package
├── tests/test_import.py         # starter test
├── scripts/bootstrap.sh         # next command to run
├── pyproject.toml               # package metadata and requirements
├── requirements.txt             # pinned test packages
├── requirements-bootstrap.txt   # pinned installation tools
├── .python-version              # exact Python version for this project
├── .venv/                       # development Python environment
├── .git/                        # local Git repository
├── .gitignore                   # files excluded from Git
├── .env.example                 # example application settings
├── .vscode/settings.json        # VS Code interpreter setting
└── README.md                    # instructions for this generated project
```

The generated package starts at version `0.1.0`. It has **no application dependencies yet**; `requirements.txt` lists test packages, while `requirements-bootstrap.txt` lists installation tools. The starter test only checks that Python can import your package. When a project name contains underscores, the package keeps them but its published distribution name uses hyphens (`invoice_tools` → `invoice-tools`).

You maintain these files after initial setup. `pyprojectgen` does not merge changes into established projects or silently overwrite conflicting files.

## 7. How do I use it afterward? (Phase 3)

Now switch to the **new project directory**. Replace the example path with the `development_root` you entered in Phase 1:

```bash
cd /absolute/path/to/develop/demo
./scripts/bootstrap.sh
```

The generated script uses the version in `.python-version` to prepare or check the development `.venv`, install the pinned installation tools and test packages, install **your project in editable mode**, check package compatibility, and run the starter test. Editable mode means edits to your source are reflected without reinstalling the project each time.

A successful run ends with:

```text
[OK] Bootstrap complete
```

**Your project is now ready for development.** Write your code under `src/demo/` and add tests under `tests/`. To run the tests again from the project directory:

```bash
.venv/bin/python -m pytest
```

Going forward, you own the source code, dependency specifications, and tests. Commit the source revision and package specifications to Git; do not copy `.venv` between machines. Pinned versions improve reproducibility but do not guarantee byte-identical builds or provide an offline package archive.

## 8. What are the optional capabilities?

### GitHub publishing

GitHub is optional. If you want the generator to publish the first commit, set up SSH authentication to GitHub first. Then fill in these settings in `~/.pyprojectgenrc` and rerun `config-validate` **before** running `create`:

| Setting | What to enter |
| --- | --- |
| `github.organization` | The GitHub username or organization that will own the project repository. |
| `github.ssh_host` | A usable SSH host or alias, such as `github.com`. |
| `ssh.private_key`, `ssh.public_key` | Absolute paths to your existing SSH key files. |

The generator checks the key files and SSH connectivity; it does **not** generate keys, modify SSH configuration, or authenticate for you. During `create`, it asks you to confirm that an **empty GitHub repository** with the project name exists under the configured owner. You create that repository yourself. The generator then configures `origin`, asks before pushing (default **No**), and **runs the Git push** if you approve.

### Local staging check

If GitHub publishing succeeds, `create` automatically proceeds to local staging; **there is no separate staging choice or command in this version**. It verifies the published commit, clones that revision into `<stage_root>/<project_name>`, creates a **separate** `.venv`, installs the project **non-editably**, checks installed package compatibility, and runs tests.

Unlike Phase 3's editable development install, this installation uses a separate copy of the committed code. It is a **limited installation-and-test check**, not a full rehearsal for production. It does **not** test application startup, containers, services, databases, networking, or a separately built production artifact. Both directories are on the same machine and share its resources and user permissions; they are not a security boundary. Passing the generated import test is not production-readiness evidence.

This optional staging operation currently runs **within Phase 2**, before you run development bootstrap in Phase 3; it has no standalone command.

## 9. Reference information

### Generator commands

Run these from the **generator source folder**. `NAME` stands for your desired project name; `X.Y.Z` stands for an exact installed Python version.

| Command | Meaning |
| --- | --- |
| `python3 pyprojectgen.py --help` | Show CLI help. |
| `python3 pyprojectgen.py config-init` | Create configuration template if absent. |
| `python3 pyprojectgen.py config-validate` | Validate configuration without modifying it. |
| `python3 pyprojectgen.py create NAME --dry-run` | Preview planned creation. |
| `python3 pyprojectgen.py create NAME` | Create project (new-project default: Python 3.12.10). |
| `python3 pyprojectgen.py create NAME --python X.Y.Z` | Use a specific installed Python version. |

Project names must be ASCII Python identifiers, not keywords; start with a letter and end with a letter or digit. Names may contain underscores but not hyphens or spaces.

| Exit code | Meaning |
| --- | --- |
| `0` | Success, including local-only creation and preview. |
| `1` | Configuration, validation, or execution failure. |
| `2` | Invalid command-line arguments. |
| `3` | Confirmation declined; dependent operations stopped. |
| `130` | Interrupted execution or unavailable confirmation input. |

The **generated** bootstrap script exits with a nonzero status if it fails. The generator has no separate bootstrap, staging, or production command.

### Testing pyprojectgen itself (for maintainers)

These commands test the **generator**, not the new project's starter test. Run from the generator source folder:

```bash
# Regression tests (installation test skipped unless enabled)
python3 -m unittest discover -s tests -v

# Full suite, including real installation/reproduction test
PG_RUN_INSTALL_TESTS=1 python3 -m unittest discover -s tests -v
```

To run just the installation/reproduction test:

```bash
PG_RUN_INSTALL_TESTS=1 python3 -m unittest discover -s tests \
  -p test_setup.py -k test_real_development_bootstrap -v
```

The generator's test suite uses `unittest`; generated projects use `pytest` inside their own `.venv`. The opt-in installation test requires access to pinned packages and exercises development and staging using a **temporary local Git remote**, not live GitHub authentication. Tests normally use temporary directories (often `/tmp/` on Linux or `/var/folders/.../T/` on macOS) and clean them up. Forced termination may leave files, and pip's cache may remain. For dated execution results, consult [VALIDATION.md](VALIDATION.md).

### Related documents

- [BACKLOG.md](pyprojectgen.wiki/BACKLOG.md): future changes (not implemented commands).
- [CHANGES.md](pyprojectgen.wiki/CHANGES.md): release history.
- [VALIDATION.md](pyprojectgen.wiki/VALIDATION.md): test evidence and limitations.
- [REPLACEMENT.md](pyprojectgen.wiki/REPLACEMENT.md): replacing an earlier generator release.
- [AGENTS.md](AGENTS.md): repository maintenance instructions.
- [LICENSE](LICENSE): MIT license.
