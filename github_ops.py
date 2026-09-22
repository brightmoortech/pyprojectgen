from pathlib import Path
import subprocess

from models import Result, Status, ValidationReport


def _run_command(
    args: list[str],
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )


def validate_github_configuration(
    organization: str,
    ssh_host: str,
    private_key: str,
    public_key: str,
) -> ValidationReport:
    results: list[Result] = []

    if not organization.strip():
        results.append(
            Result(
                Status.WARNING,
                "GitHub organization or username is not configured",
            )
        )
    else:
        results.append(
            Result(
                Status.OK,
                f"GitHub owner configured: {organization}",
            )
        )

    if not ssh_host.strip():
        results.append(
            Result(
                Status.WARNING,
                "GitHub SSH host is not configured",
            )
        )
    else:
        results.append(
            Result(
                Status.OK,
                f"GitHub SSH host configured: {ssh_host}",
            )
        )

    for label, value in (
        ("private key", private_key),
        ("public key", public_key),
    ):
        if not value.strip():
            results.append(
                Result(
                    Status.WARNING,
                    f"GitHub SSH {label} is not configured",
                )
            )
            continue

        path = Path(value).expanduser()

        if not path.exists():
            results.append(
                Result(
                    Status.ERROR,
                    f"GitHub SSH {label} does not exist: {path}",
                )
            )
        elif not path.is_file():
            results.append(
                Result(
                    Status.ERROR,
                    f"GitHub SSH {label} is not a file: {path}",
                )
            )
        else:
            results.append(
                Result(
                    Status.OK,
                    f"GitHub SSH {label} exists: {path}",
                )
            )

    return ValidationReport(results=tuple(results))


def validate_github_ssh(ssh_host: str) -> ValidationReport:
    if not ssh_host.strip():
        return ValidationReport(
            results=(
                Result(
                    Status.WARNING,
                    "GitHub SSH validation skipped because ssh_host is not configured",
                ),
            )
        )

    completed = _run_command(
        [
            "ssh",
            "-T",
            "-o",
            "BatchMode=yes",
            "-o",
            "ConnectTimeout=10",
            ssh_host,
        ]
    )

    output = "\n".join(
        part.strip()
        for part in (completed.stdout, completed.stderr)
        if part.strip()
    )

    if "successfully authenticated" in output.lower():
        return ValidationReport(
            results=(
                Result(
                    Status.OK,
                    f"GitHub SSH authentication succeeded via {ssh_host}",
                ),
            )
        )

    return ValidationReport(
        results=(
            Result(
                Status.ERROR,
                (
                    f"GitHub SSH authentication failed via {ssh_host}"
                    + (f": {output}" if output else "")
                ),
            ),
        )
    )


def expected_remote_url(
    organization: str,
    project_name: str,
    ssh_host: str,
) -> str:
    return f"git@{ssh_host}:{organization}/{project_name}.git"


def plan_github_remote(
    project_root: Path,
    organization: str,
    project_name: str,
    ssh_host: str,
) -> ValidationReport:
    if not organization.strip() or not ssh_host.strip():
        return ValidationReport(
            results=(
                Result(
                    Status.WARNING,
                    "GitHub remote cannot be planned because GitHub configuration is incomplete",
                ),
            )
        )

    expected = expected_remote_url(
        organization=organization,
        project_name=project_name,
        ssh_host=ssh_host,
    )

    completed = _run_command(
        ["git", "remote", "get-url", "origin"],
        cwd=project_root,
    )

    if completed.returncode != 0:
        return ValidationReport(
            results=(
                Result(
                    Status.CREATE,
                    f"Git remote origin: {expected}",
                ),
            )
        )

    actual = completed.stdout.strip()

    if actual == expected:
        return ValidationReport(
            results=(
                Result(
                    Status.SKIP,
                    f"Git remote origin already configured: {actual}",
                ),
            )
        )

    return ValidationReport(
        results=(
            Result(
                Status.ERROR,
                (
                    f"Git remote origin is '{actual}', "
                    f"expected '{expected}'"
                ),
            ),
        )
    )


def configure_github_remote(
    project_root: Path,
    organization: str,
    project_name: str,
    ssh_host: str,
) -> ValidationReport:
    plan = plan_github_remote(
        project_root=project_root,
        organization=organization,
        project_name=project_name,
        ssh_host=ssh_host,
    )

    if plan.has_errors:
        return plan

    if all(result.status is Status.SKIP for result in plan.results):
        return plan

    if all(result.status is Status.WARNING for result in plan.results):
        return plan

    remote_url = expected_remote_url(
        organization=organization,
        project_name=project_name,
        ssh_host=ssh_host,
    )

    completed = _run_command(
        ["git", "remote", "add", "origin", remote_url],
        cwd=project_root,
    )

    if completed.returncode != 0:
        message = completed.stderr.strip() or completed.stdout.strip()

        return ValidationReport(
            results=(
                Result(
                    Status.ERROR,
                    f"Could not configure GitHub remote: {message}",
                ),
            )
        )

    return ValidationReport(
        results=(
            Result(
                Status.CREATE,
                f"Git remote origin configured: {remote_url}",
            ),
        )
    )


def plan_initial_push(project_root: Path) -> ValidationReport:
    branch_result = _run_command(
        ["git", "branch", "--show-current"],
        cwd=project_root,
    )

    if branch_result.returncode != 0:
        message = branch_result.stderr.strip() or branch_result.stdout.strip()

        return ValidationReport(
            results=(
                Result(
                    Status.ERROR,
                    f"Could not determine current branch: {message}",
                ),
            )
        )

    branch = branch_result.stdout.strip()

    if not branch:
        return ValidationReport(
            results=(
                Result(
                    Status.ERROR,
                    "Current Git branch could not be determined",
                ),
            )
        )

    remote_result = _run_command(
        ["git", "remote", "get-url", "origin"],
        cwd=project_root,
    )

    if remote_result.returncode != 0:
        return ValidationReport(
            results=(
                Result(
                    Status.WARNING,
                    "Initial push cannot be planned because origin is not configured",
                ),
            )
        )

    return ValidationReport(
        results=(
            Result(
                Status.CREATE,
                f"Push branch '{branch}' to origin and set upstream",
            ),
        )
    )


def push_initial_branch(project_root: Path) -> ValidationReport:
    plan = plan_initial_push(project_root)

    if plan.has_errors:
        return plan

    if all(result.status is Status.WARNING for result in plan.results):
        return plan

    branch_result = _run_command(
        ["git", "branch", "--show-current"],
        cwd=project_root,
    )

    branch = branch_result.stdout.strip()

    completed = _run_command(
        ["git", "push", "-u", "origin", branch],
        cwd=project_root,
    )

    if completed.returncode != 0:
        message = completed.stderr.strip() or completed.stdout.strip()

        return ValidationReport(
            results=(
                Result(
                    Status.ERROR,
                    f"Initial GitHub push failed: {message}",
                ),
            )
        )

    return ValidationReport(
        results=(
            Result(
                Status.CREATE,
                f"Branch '{branch}' pushed to origin with upstream configured",
            ),
        )
    )