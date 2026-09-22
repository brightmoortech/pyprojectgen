
# pyprojectgen

`pyprojectgen` is a macOS-focused Python utility for creating and validating reproducible Python project environments.

The project is currently under development.

## Goals

`pyprojectgen` is designed to automate a repeatable Python project setup workflow while remaining:

* safe by default
* resumable after failures
* idempotent
* explicit about important user decisions
* conservative about overwriting existing files
* reproducible across development and staging environments

## Planned capabilities

The initial version is intended to support:

* project creation using a `src/<package_name>/` layout
* project-local `.venv` environments
* exact Python-version selection
* `pyproject.toml`
* frozen `requirements.txt`
* pytest
* VS Code interpreter configuration
* Git initialization
* optional GitHub integration over SSH
* development-environment bootstrapping
* separate staging clone and validation
* dry-run/preflight validation
* resumable phased execution

## Configuration

Machine-specific configuration is stored outside generated projects in:

```text
~/.projectgenrc
```

A public example is provided in:

```text
projectgenrc.example
```

Configuration includes values such as:

* development root
* staging root
* Git identity
* GitHub organization or username
* GitHub SSH host alias
* SSH key paths

The configuration file must not contain passwords, authentication tokens, private-key contents, or other secrets.

## Planned command model

The command interface is expected to include:

```text
pyprojectgen config-init
pyprojectgen config-validate
pyprojectgen create <project_name>
pyprojectgen validate <project_name>
pyprojectgen bootstrap <project_name>
pyprojectgen github <project_name>
pyprojectgen stage <project_name>
```

Applicable commands will also support dry-run validation.

Example:

```text
pyprojectgen create my_project --dry-run
```

## Project status

The functional specification is complete enough to begin implementation.

The first implementation milestone is:

```text
config-init
```

This command will create a safe `~/.projectgenrc` template when one does not already exist.

## Platform

Initial target:

* macOS
* zsh
* Python 3.12+
* Git
* VS Code
* GitHub with SSH authentication

Other platforms may be considered later.

## Not included in v0.1

The initial version does not include:

* automatic GitHub repository creation
* automatic rollback
* destructive cleanup
* GUI support
* Windows or Linux support
* multiple project layouts
* Docker integration
* CI/CD setup
* Ruff, mypy, or coverage tooling
* automatic dependency upgrades
* automatic modification of SSH configuration
* automatic modification of global Git identity

These capabilities may be considered in later versions.


## License

MIT License


