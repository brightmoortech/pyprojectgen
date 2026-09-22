from pathlib import Path
import subprocess

from models import Result, Status, ValidationReport


def _run_git(
    args: list[str],
    cwd: Path,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )


def plan_git_repository(project_root: Path) -> ValidationReport:
    results: list[Result] = []

    git_dir = project_root / ".git"

    if git_dir.exists():
        if git_dir.is_dir():
            results.append(
                Result(
                    Status.SKIP,
                    f"Git repository already initialized: {project_root}",
                )
            )
        else:
            results.append(
                Result(
                    Status.ERROR,
                    f"Expected .git directory but found another object: {git_dir}",
                )
            )
    else:
        results.append(
            Result(
                Status.CREATE,
                f"Git repository: {project_root}",
            )
        )

    return ValidationReport(results=tuple(results))


def initialize_git_repository(project_root: Path) -> ValidationReport:
    plan = plan_git_repository(project_root)

    if plan.has_errors:
        return plan

    if (project_root / ".git").exists():
        return plan

    completed = _run_git(
        ["init", "-b", "main"],
        cwd=project_root,
    )

    if completed.returncode != 0:
        message = completed.stderr.strip() or completed.stdout.strip()

        return ValidationReport(
            results=(
                Result(
                    Status.ERROR,
                    f"Git initialization failed: {message}",
                ),
            )
        )

    return ValidationReport(
        results=(
            Result(
                Status.CREATE,
                f"Git repository initialized: {project_root}",
            ),
        )
    )


def validate_git_identity(
    project_root: Path,
    expected_name: str,
    expected_email: str,
) -> ValidationReport:
    results: list[Result] = []

    name_result = _run_git(
        ["config", "--get", "user.name"],
        cwd=project_root,
    )

    email_result = _run_git(
        ["config", "--get", "user.email"],
        cwd=project_root,
    )

    actual_name = name_result.stdout.strip()
    actual_email = email_result.stdout.strip()

    if not actual_name:
        results.append(
            Result(
                Status.ERROR,
                "Effective Git user.name is not configured",
            )
        )
    elif actual_name != expected_name:
        results.append(
            Result(
                Status.ERROR,
                (
                    f"Effective Git user.name is '{actual_name}', "
                    f"expected '{expected_name}'"
                ),
            )
        )
    else:
        results.append(
            Result(
                Status.OK,
                f"Git user.name matches: {actual_name}",
            )
        )

    if not actual_email:
        results.append(
            Result(
                Status.ERROR,
                "Effective Git user.email is not configured",
            )
        )
    elif actual_email != expected_email:
        results.append(
            Result(
                Status.ERROR,
                (
                    f"Effective Git user.email is '{actual_email}', "
                    f"expected '{expected_email}'"
                ),
            )
        )
    else:
        results.append(
            Result(
                Status.OK,
                f"Git user.email matches: {actual_email}",
            )
        )

    return ValidationReport(results=tuple(results))


def plan_initial_commit(project_root: Path) -> ValidationReport:
    status_result = _run_git(
        ["status", "--porcelain"],
        cwd=project_root,
    )

    if status_result.returncode != 0:
        message = status_result.stderr.strip() or status_result.stdout.strip()

        return ValidationReport(
            results=(
                Result(
                    Status.ERROR,
                    f"Could not inspect Git status: {message}",
                ),
            )
        )

    if not status_result.stdout.strip():
        return ValidationReport(
            results=(
                Result(
                    Status.SKIP,
                    "No uncommitted files to stage",
                ),
            )
        )

    return ValidationReport(
        results=(
            Result(
                Status.CREATE,
                "Stage project files for initial commit",
            ),
            Result(
                Status.CREATE,
                "Create initial Git commit",
            ),
        )
    )


def create_initial_commit(
    project_root: Path,
    message: str = "Initial project setup",
) -> ValidationReport:
    plan = plan_initial_commit(project_root)

    if plan.has_errors:
        return plan

    if all(result.status is Status.SKIP for result in plan.results):
        return plan

    add_result = _run_git(
        ["add", "."],
        cwd=project_root,
    )

    if add_result.returncode != 0:
        message_text = add_result.stderr.strip() or add_result.stdout.strip()

        return ValidationReport(
            results=(
                Result(
                    Status.ERROR,
                    f"Git staging failed: {message_text}",
                ),
            )
        )

    commit_result = _run_git(
        ["commit", "-m", message],
        cwd=project_root,
    )

    if commit_result.returncode != 0:
        message_text = (
            commit_result.stderr.strip()
            or commit_result.stdout.strip()
        )

        return ValidationReport(
            results=(
                Result(
                    Status.ERROR,
                    f"Git commit failed: {message_text}",
                ),
            )
        )

    return ValidationReport(
        results=(
            Result(
                Status.CREATE,
                "Project files staged",
            ),
            Result(
                Status.CREATE,
                f"Git commit created: {message}",
            ),
        )
    )