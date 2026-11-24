# pyprojectgen backlog

Last updated: 2026-11-22

Planned enhancements only; the current code is unchanged. Recording an item
is not evidence that the feature is available. The original task authorizes system-wide installation and per-user
configuration implementation; Git identity and GitHub automation are agreed future
requirements but have not been authorized for implementation. Other entries
retain their individual proposal/deferred status. No target release or
implementation order is set.

## BL-001: Separate local staging from project creation

Status: Deferred; recorded for future planning.

Current behaviour: `create` performs optional local staging before the separately
run development bootstrap. Local staging clones the verified published commit,
creates its own `.venv`, installs the project and dependencies, and runs tests.

Desired behaviour: make local staging an independently invoked fourth phase,
after development installation and tests have succeeded:

1. Configure the generator.
2. Create the development project.
3. Bootstrap and test development.
4. Set up and test local staging, if requested.

Provide a separate way to invoke local staging. Retain commit verification,
independent environments, confirmation controls, and preservation of conflicting
user work. Define retry behaviour and update documentation and tests with the
approved design. The command name and whether development success is enforced
automatically remain design decisions.

## BL-002: Remote staging with production-like installation

Status: Planned; not implemented.

Current limitation: local staging is a limited Python installation and test check
on the development machine. It does not reproduce a production deployment.

Desired behaviour: support staging on a separate machine using the intended
production installation method. Install the same built package artifact or
container image intended for production, as applicable, rather than relying only
on cloning source and building again on the staging host.

Include the runtime, application configuration, supporting services, startup,
and connectivity needed to exercise the deployment. Match relevant production
conditions and run installation, startup, and application checks. Document any
differences that remain. Moving the existing local check to another machine
alone does not fulfil this item.

Before implementation, agree the supported deployment methods, target platform,
remote access and credentials handling, artifact transfer, isolation, and recovery
approach. Keep these configurable rather than embedding a specific customer's
deployment. Coordinate the invocation with BL-001.

## BL-003: Default to the Python version running the generator

Status: Proposed; design and implementation approval pending.

Current behaviour: new projects default to Python 3.12.10. Setup fails if that
exact version cannot be found, even when a newer Python runs the generator.

Proposed behaviour: for a new project, use the exact Python version running the
generator as the default for development and staging virtual environments. Record
that version in the project specifications. Retain `--python X.Y.Z` as an explicit
override and use the project's recorded version on retries.

If approved, update selection logic, CLI help, generated specifications, README,
and regression checks together. Preserve exact-version validation and rejection
of conflicts with an existing project pin. The current default remains unchanged.

## BL-004: System-wide installer for macOS and Linux

Status: Agreed requirement; not implemented. Original task includes
implementation, subject to completing design and verification.
Last updated: 2026-11-22.

Current limitation: The generator has a packaged CLI entry point but no
specified administrator-managed shared installation workflow. The README
primarily demonstrates invocation from a source checkout.

Desired outcome: A user downloads and extracts or clones the repository, then
invokes one installer command from that local source. The tool becomes available to all
local users without elevated privileges for ordinary commands. Use an
administrator-controlled isolated Python environment and a shared command
entry point, avoiding modifications to the system Python installation.

Installer behavior: install when absent; upgrade an older installed version;
reinstall when the installed version is the same (including repair of a damaged
installation); prevent downgrades unless explicitly authorized; and attempt
controlled recovery for incomplete installations. Preserve per-user
configurations, avoid partial installation states, and provide actionable errors.
No background or automatic updates. GitHub-hosted release installation is
deferred; the agreed initial distribution method is a local checkout/download.

Dependencies and open design: specify install paths and privileges for both
platforms, reliable version detection when an installation is damaged,
rollback/atomicity, downgrade override, ownership, and executable resolution.
Verify install/upgrade/reinstall/recovery on macOS and Linux before describing
commands as operational.

## BL-005: Per-user configuration and first-use template

Status: Agreed requirement; not implemented. Original task includes
implementation, subject to verification.
Last updated: 2026-11-22.

Current behavior: `config.py` uses `Path.home() / ".pyprojectgenrc"`.
`config-init` creates a template only when explicitly run. The current file
is already TOML-formatted, though named `.pyprojectgenrc`.

Desired outcome: Use one configuration file per invoking user at
`$XDG_CONFIG_HOME/pyprojectgen/config.toml`, or
`~/.config/pyprojectgen/config.toml` if `XDG_CONFIG_HOME` is unset. Use
invoking-user resolution, not the administrator/installing user's home or a
fixed path. When a user first invokes a configuration-dependent command and
the file is missing, automatically create a commented template, show its
location, and instruct the user to edit and validate it. Do not create a
project during this initial configuration step. Retain
explicit configuration initialization and validation commands; avoid
interactive setup and competing configuration files.

Dependencies and open design: validate ownership and permission boundaries,
behavior under `sudo`, invalid `XDG_CONFIG_HOME`, missing parent directories,
and compatibility with the current schema. Migration support is not required
for this new tool.

## BL-006: Read identity from Git configuration

Status: Agreed future requirement; not implemented; implementation not yet
authorized.
Last updated: 2026-11-22.

Current behavior: The generator expects Git name and email in its own
configuration and verifies them against Git identity.

Desired outcome: Resolve the invoking user's effective Git `user.name` and
`user.email`, validate both, and report actionable setup instructions if
missing. Do not store duplicate identity values in the generator's `config.toml`
and do not modify the user's Git configuration.

Dependencies and open design: determine the correct lookup scope (global versus
repository-local configuration) when creating a new project, and test absent,
invalid, or conflicting values.

## BL-007: Optional GitHub repository creation using gh

Status: Agreed future requirement; implementation deferred, not implemented.
Last updated: 2026-11-22.

Current behavior: The user manually creates an empty GitHub repository, then
confirms so the generator can configure `origin` and push via existing SSH
integration. GitHub integration is optional.

Desired outcome: GitHub integration remains optional. When automated repository
creation is requested, check the separately installed and authenticated GitHub
CLI (`gh`). Ask for explicit confirmation before creating a GitHub repository; default visibility to private and permit an
explicit public choice. Prefer the authenticated user's personal account;
allow an optional configured organization. Connect and push the initial commit,
with safe handling of existing repositories. Do not create SSH keys, edit SSH
configuration, or manage GitHub authentication. Require no paid GitHub features.

Dependencies and open design: CLI availability/authentication, GitHub owner
permissions, choice of account/visibility interface, existing-repository
conflict handling, retry behavior, and preservation of the current manual
workflow when automation is not available or requested.

## BL-008: Report unexpected installed packages

Status: Proposed; not implemented.
Last updated: 2026-11-22.

Current limitation: Existing environments can contain extra installed packages
that are not detected by the generator's environment reproduction checks.

Desired outcome: identify and report unexpected packages without automatically
removing them. Define the authoritative expected package set and the behavior
for transitive dependencies before implementation.
