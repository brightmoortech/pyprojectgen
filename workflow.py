from pathlib import Path
import sys
import tomllib

from config import CONFIG_PATH
from git_ops import (
    create_initial_commit,
    initialize_git_repository,
    plan_initial_commit,
    validate_git_identity,
)
from github_ops import (
    configure_github_remote,
    expected_remote_url,
    plan_github_remote,
    plan_initial_push,
    push_initial_branch,
    validate_github_configuration,
    validate_github_ssh,
)
from models import Result, Status, ValidationReport
from preflight import run_preflight
from project_files import create_project_files, plan_project_files
from project_structure import (
    create_project_structure,
    plan_project_structure,
)
from python_env import (
    create_python_environment,
    plan_python_environment,
)
from stage import create_stage, plan_stage


def _print_result(result: Result) -> None:
    print(f"[{result.status.value}] {result.message}")


def _print_report(
    title: str,
    report: ValidationReport,
) -> None:
    print()
    print(f"--- {title} ---")

    for result in report.results:
        _print_result(result)


def _confirm(prompt: str) -> bool:
    print()
    response = input(f"{prompt} [y/N] ").strip().lower()
    return response in {"y", "yes"}


def _load_config() -> dict:
    with CONFIG_PATH.open("rb") as file:
        return tomllib.load(file)


def _stop_if_errors(report: ValidationReport) -> bool:
    if report.has_errors:
        print()
        print("[ERROR] Workflow stopped")
        return True

    return False


def _dry_run_git_repository(
    project_root: Path,
) -> ValidationReport:
    if (project_root / ".git").is_dir():
        status = Status.SKIP
        message = (
            f"Git repository already initialized: {project_root}"
        )
    else:
        status = Status.CREATE
        message = f"Git repository: {project_root}"

    return ValidationReport(
        results=(
            Result(status, message),
        )
    )


def _dry_run_initial_commit(
    project_root: Path,
) -> ValidationReport:
    if (project_root / ".git").is_dir():
        return plan_initial_commit(project_root)

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


def _dry_run_github_remote(
    project_root: Path,
    organization: str,
    project_name: str,
    ssh_host: str,
) -> ValidationReport:
    if (project_root / ".git").is_dir():
        return plan_github_remote(
            project_root,
            organization,
            project_name,
            ssh_host,
        )

    remote_url = expected_remote_url(
        organization,
        project_name,
        ssh_host,
    )

    return ValidationReport(
        results=(
            Result(
                Status.CREATE,
                f"Git remote origin: {remote_url}",
            ),
        )
    )


def _dry_run_initial_push(
    project_root: Path,
) -> ValidationReport:
    if (project_root / ".git").is_dir():
        return plan_initial_push(project_root)

    return ValidationReport(
        results=(
            Result(
                Status.CREATE,
                "Push branch 'main' to origin and set upstream",
            ),
        )
    )


def run_create_workflow(
    project_name: str,
    dry_run: bool = False,
) -> None:
    config = _load_config()

    development_root = Path(
        config["paths"]["development_root"]
    ).expanduser()

    stage_root = Path(
        config["paths"]["stage_root"]
    ).expanduser()

    project_root = development_root / project_name
    python_executable = Path(sys.executable)

    github_owner = config["github"]["organization"]
    ssh_host = config["github"]["ssh_host"]

    git_user_name = config["git"]["user_name"]
    git_user_email = config["git"]["user_email"]

    private_key = config["ssh"]["private_key"]
    public_key = config["ssh"]["public_key"]

    print()
    print(f"Project: {project_name}")
    print(f"Mode: {'DRY RUN' if dry_run else 'CREATE'}")

    preflight_report = run_preflight(project_name)
    _print_report("Preflight", preflight_report)

    if _stop_if_errors(preflight_report):
        return

    if dry_run:
        structure_report = plan_project_structure(
            development_root,
            project_name,
        )
    else:
        structure_report = create_project_structure(
            development_root,
            project_name,
        )

    _print_report(
        "Project structure",
        structure_report,
    )

    if _stop_if_errors(structure_report):
        return

    if dry_run:
        python_report = plan_python_environment(
            project_root,
            python_executable,
        )
    else:
        python_report = create_python_environment(
            project_root,
            python_executable,
        )

    _print_report(
        "Python environment",
        python_report,
    )

    if _stop_if_errors(python_report):
        return

    if dry_run:
        files_report = plan_project_files(
            project_root,
            project_name,
        )
    else:
        files_report = create_project_files(
            project_root,
            project_name,
        )

    _print_report(
        "Project files",
        files_report,
    )

    if _stop_if_errors(files_report):
        return

    if dry_run:
        git_init_report = _dry_run_git_repository(
            project_root,
        )
    else:
        git_init_report = initialize_git_repository(
            project_root,
        )

    _print_report(
        "Git repository",
        git_init_report,
    )

    if _stop_if_errors(git_init_report):
        return

    identity_cwd = (
        project_root
        if project_root.exists()
        else development_root
    )

    git_identity_report = validate_git_identity(
        identity_cwd,
        git_user_name,
        git_user_email,
    )

    _print_report(
        "Git identity",
        git_identity_report,
    )

    if _stop_if_errors(git_identity_report):
        return

    if dry_run:
        commit_plan = _dry_run_initial_commit(
            project_root,
        )
    else:
        commit_plan = plan_initial_commit(
            project_root,
        )

    _print_report(
        "Initial commit",
        commit_plan,
    )

    if _stop_if_errors(commit_plan):
        return

    if not dry_run and not all(
        result.status is Status.SKIP
        for result in commit_plan.results
    ):
        if _confirm("Create the initial Git commit?"):
            commit_report = create_initial_commit(
                project_root,
            )

            _print_report(
                "Initial commit execution",
                commit_report,
            )

            if _stop_if_errors(commit_report):
                return
        else:
            print()
            print("[SKIP] Initial Git commit not created")
            print(
                "[ERROR] Workflow stopped before "
                "GitHub integration"
            )
            return

    github_config_report = validate_github_configuration(
        github_owner,
        ssh_host,
        private_key,
        public_key,
    )

    _print_report(
        "GitHub configuration",
        github_config_report,
    )

    if _stop_if_errors(github_config_report):
        return

    github_configured = (
        bool(github_owner.strip())
        and bool(ssh_host.strip())
        and bool(private_key.strip())
        and bool(public_key.strip())
    )

    if not github_configured:
        print()
        print("[SKIP] GitHub integration not configured")
        print("[SKIP] Staging not configured")
        return

    ssh_report = validate_github_ssh(
        ssh_host,
    )

    _print_report(
        "GitHub SSH",
        ssh_report,
    )

    if _stop_if_errors(ssh_report):
        return

    remote_url = expected_remote_url(
        github_owner,
        project_name,
        ssh_host,
    )

    if dry_run:
        remote_plan = _dry_run_github_remote(
            project_root,
            github_owner,
            project_name,
            ssh_host,
        )
    else:
        remote_plan = plan_github_remote(
            project_root,
            github_owner,
            project_name,
            ssh_host,
        )

    _print_report(
        "GitHub remote",
        remote_plan,
    )

    if _stop_if_errors(remote_plan):
        return

    if dry_run:
        print()
        print(
            "[CREATE] GitHub repository must exist before "
            f"remote/push execution: "
            f"{github_owner}/{project_name}"
        )

        push_plan = _dry_run_initial_push(
            project_root,
        )

        _print_report(
            "Initial push",
            push_plan,
        )

        stage_report = plan_stage(
            stage_root,
            project_name,
            remote_url,
        )

        _print_report(
            "Staging",
            stage_report,
        )

        if _stop_if_errors(stage_report):
            return

        print()
        print(
            "[OK] Dry run complete; no changes were made"
        )
        return

    remote_needs_creation = any(
        result.status is Status.CREATE
        for result in remote_plan.results
    )

    if remote_needs_creation:
        print()
        print(
            "Create the GitHub repository manually if it "
            "does not already exist:"
        )
        print(
            f"  {github_owner}/{project_name}"
        )

        if not _confirm(
            "Has the GitHub repository been created?"
        ):
            print()
            print(
                "[SKIP] GitHub integration skipped"
            )
            print(
                "[SKIP] Staging not configured"
            )
            return

    remote_report = configure_github_remote(
        project_root,
        github_owner,
        project_name,
        ssh_host,
    )

    _print_report(
        "GitHub remote execution",
        remote_report,
    )

    if _stop_if_errors(remote_report):
        return

    push_plan = plan_initial_push(
        project_root,
    )

    _print_report(
        "Initial push",
        push_plan,
    )

    if _stop_if_errors(push_plan):
        return

    push_needed = any(
        result.status is Status.CREATE
        for result in push_plan.results
    )

    if push_needed:
        if _confirm(
            "Push the current branch to GitHub?"
        ):
            push_report = push_initial_branch(
                project_root,
            )

            _print_report(
                "Initial push execution",
                push_report,
            )

            if _stop_if_errors(push_report):
                return
        else:
            print()
            print(
                "[SKIP] GitHub push not performed"
            )
            print(
                "[SKIP] Staging not configured"
            )
            return

    stage_report = create_stage(
        stage_root,
        project_name,
        remote_url,
        python_executable,
    )

    _print_report(
        "Staging",
        stage_report,
    )

    if _stop_if_errors(stage_report):
        return

    print()
    print(
        "[OK] Project creation workflow complete"
    )