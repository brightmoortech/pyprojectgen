from pathlib import Path
import os
import re
import tomllib

from models import Result, Status, ValidationReport


CONFIG_PATH = Path.home() / ".pyprojectgenrc"

CONFIG_TEMPLATE = """[paths]
# Root directory under which development projects will be created.
# Example: /Users/alice/code/develop
development_root = ""

# Root directory under which staging projects will be created.
# Example: /Users/alice/code/stage
stage_root = ""

[github]
# GitHub organization or username that owns repositories.
organization = ""

# Allowed values: "private" or "public".
default_visibility = "private"

# SSH host or alias from ~/.ssh/config.
# Example: github.com or github.com-work
ssh_host = ""

[git]
# Must match: git config user.name
user_name = ""

# Must match: git config user.email
user_email = ""

[ssh]
# Optional unless GitHub SSH integration is used.
private_key = ""
public_key = ""
"""


def init_config() -> Result:
    if CONFIG_PATH.exists():
        return Result(
            status=Status.SKIP,
            message=f"{CONFIG_PATH} already exists",
        )

    CONFIG_PATH.write_text(CONFIG_TEMPLATE, encoding="utf-8")

    return Result(
        status=Status.CREATE,
        message=f"{CONFIG_PATH}",
    )


def _validate_root(name: str, value: str) -> list[Result]:
    results: list[Result] = []

    if not value.strip():
        results.append(
            Result(Status.ERROR, f"{name} is not configured")
        )
        return results

    path = Path(value).expanduser()

    if not path.is_absolute():
        results.append(
            Result(Status.ERROR, f"{name} must be an absolute path")
        )
        return results

    if path.exists():
        if not path.is_dir():
            results.append(
                Result(Status.ERROR, f"{name} exists but is not a directory")
            )
            return results

        if not os.access(path, os.W_OK):
            results.append(
                Result(Status.ERROR, f"{name} is not writable")
            )
            return results

        results.append(
            Result(Status.OK, f"{name} exists and is writable")
        )
    else:
        results.append(
            Result(
                Status.WARNING,
                f"{name} does not exist and may be created later",
            )
        )

    return results


def _validate_email(value: str) -> bool:
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value))


def validate_config() -> ValidationReport:
    results: list[Result] = []

    if not CONFIG_PATH.exists():
        return ValidationReport(
            results=(
                Result(
                    Status.ERROR,
                    f"{CONFIG_PATH} does not exist",
                ),
            )
        )

    try:
        with CONFIG_PATH.open("rb") as file:
            config = tomllib.load(file)
    except tomllib.TOMLDecodeError as exc:
        return ValidationReport(
            results=(
                Result(
                    Status.ERROR,
                    f"Invalid TOML: {exc}",
                ),
            )
        )

    required_sections = {
        "paths",
        "github",
        "git",
        "ssh",
    }

    for section in required_sections:
        if section not in config:
            results.append(
                Result(
                    Status.ERROR,
                    f"Missing required section: [{section}]",
                )
            )

    if any(result.status is Status.ERROR for result in results):
        return ValidationReport(results=tuple(results))

    paths = config["paths"]
    github = config["github"]
    git = config["git"]
    ssh = config["ssh"]

    required_keys = {
        "paths": ("development_root", "stage_root"),
        "github": ("organization", "default_visibility", "ssh_host"),
        "git": ("user_name", "user_email"),
        "ssh": ("private_key", "public_key"),
    }

    sections = {
        "paths": paths,
        "github": github,
        "git": git,
        "ssh": ssh,
    }

    for section_name, keys in required_keys.items():
        for key in keys:
            if key not in sections[section_name]:
                results.append(
                    Result(
                        Status.ERROR,
                        f"Missing required setting: {section_name}.{key}",
                    )
                )

    if any(result.status is Status.ERROR for result in results):
        return ValidationReport(results=tuple(results))

    results.extend(
        _validate_root(
            "paths.development_root",
            paths["development_root"],
        )
    )

    results.extend(
        _validate_root(
            "paths.stage_root",
            paths["stage_root"],
        )
    )

    organization = github["organization"]

    if not organization.strip():
        results.append(
            Result(
                Status.WARNING,
                "GitHub support is not fully configured: "
                "github.organization is empty",
            )
        )
    else:
        results.append(
            Result(
                Status.OK,
                "github.organization configured",
            )
        )

    visibility = github["default_visibility"]

    if visibility not in {"private", "public"}:
        results.append(
            Result(
                Status.ERROR,
                "github.default_visibility must be 'private' or 'public'",
            )
        )
    else:
        results.append(
            Result(
                Status.OK,
                f"github.default_visibility is '{visibility}'",
            )
        )

    ssh_host = github["ssh_host"]

    if not ssh_host.strip():
        results.append(
            Result(
                Status.WARNING,
                "GitHub support is not fully configured: "
                "github.ssh_host is empty",
            )
        )
    else:
        results.append(
            Result(
                Status.OK,
                "github.ssh_host configured",
            )
        )

    user_name = git["user_name"]

    if not user_name.strip():
        results.append(
            Result(
                Status.ERROR,
                "git.user_name is not configured",
            )
        )
    else:
        results.append(
            Result(
                Status.OK,
                "git.user_name configured",
            )
        )

    user_email = git["user_email"]

    if not user_email.strip():
        results.append(
            Result(
                Status.ERROR,
                "git.user_email is not configured",
            )
        )
    elif not _validate_email(user_email):
        results.append(
            Result(
                Status.ERROR,
                "git.user_email is not a valid email address",
            )
        )
    else:
        results.append(
            Result(
                Status.OK,
                "git.user_email configured",
            )
        )

    for key_name in ("private_key", "public_key"):
        value = ssh[key_name]

        if not value.strip():
            results.append(
                Result(
                    Status.WARNING,
                    f"GitHub SSH support is not configured: "
                    f"ssh.{key_name} is empty",
                )
            )
            continue

        path = Path(value).expanduser()

        if not path.is_absolute():
            results.append(
                Result(
                    Status.ERROR,
                    f"ssh.{key_name} must be an absolute path",
                )
            )
        elif not path.exists():
            results.append(
                Result(
                    Status.WARNING,
                    f"ssh.{key_name} does not exist",
                )
            )
        elif not path.is_file():
            results.append(
                Result(
                    Status.ERROR,
                    f"ssh.{key_name} exists but is not a file",
                )
            )
        else:
            results.append(
                Result(
                    Status.OK,
                    f"ssh.{key_name} exists",
                )
            )

    return ValidationReport(results=tuple(results))