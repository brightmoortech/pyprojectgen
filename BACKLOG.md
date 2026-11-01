# pyprojectgen backlog

Last updated: 2026-11-01

Planned enhancements only. Recording an item does not authorize implementation.
The current code remains unchanged; designs and implementation plans require
approval before work begins. No target release or implementation order is set.

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
