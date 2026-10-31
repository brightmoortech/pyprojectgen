"""Regression checks for initial setup, interruption recovery, and environment reproduction."""
import contextlib
import ast
import io
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import tomllib
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config
import github_ops
import project_files
import python_env
import stage
import workflow
import pyprojectgen
from models import Result, Status, ValidationReport

ROOT = Path(__file__).resolve().parents[1]
VERSION = platform.python_version()


def run(*args, cwd=None, env=None):
    return subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True, check=True)


class SetupTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.project = self.root / "develop" / "demo"
        self.stage_root = self.root / "stage"
        self.environment = os.environ.copy()
        self.environment.update({"HOME": str(self.root), "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": str(self.root / "gitconfig")})
        (self.root / 'gitconfig').write_text('[user]\n name = Setup Test\n email = setup@example.invalid\n')
        self.config_path = self.root / '.pyprojectgenrc'
        self.config_path.write_text(f'''[paths]
development_root = "{self.root / 'develop'}"
stage_root = "{self.stage_root}"
[github]
organization = ""
ssh_host = ""
[git]
user_name = "Setup Test"
user_email = "setup@example.invalid"
[ssh]
private_key = ""
public_key = ""
''')

    def cli(self, *args, input=None):
        return subprocess.run([sys.executable, str(ROOT / 'pyprojectgen.py'), *args], env=self.environment, input=input, capture_output=True, text=True)

    def scaffold(self):
        self.project.mkdir(parents=True)
        report = project_files.create_project_files(self.project, "demo", VERSION)
        self.assertFalse(report.has_errors)

    def repo(self):
        self.scaffold()
        run('git', 'init', '-b', 'main', cwd=self.project, env=self.environment)
        run('git', 'add', '.', cwd=self.project, env=self.environment)
        run('git', 'commit', '-m', 'Initial project setup', cwd=self.project, env=self.environment)
        remote = self.root / 'remote.git'
        run('git', 'init', '--bare', '-b', 'main', str(remote), env=self.environment)
        run('git', 'remote', 'add', 'origin', str(remote), cwd=self.project)
        run('git', 'push', '-u', 'origin', 'main', cwd=self.project, env=self.environment)
        commit = run('git', 'rev-parse', 'HEAD', cwd=self.project).stdout.strip()
        return str(remote), commit

    def test_identical_configured_roots_fail_before_project_writes(self):
        self.config_path.write_text(self.config_path.read_text().replace(str(self.stage_root), str(self.project.parent)))
        result = self.cli('create', 'demo', '--python', VERSION)
        self.assertEqual(result.returncode, 1)
        self.assertIn('same location', result.stdout + result.stderr)
        self.assertFalse(self.project.parent.exists())

    def test_symlinked_roots_and_project_paths_are_rejected(self):
        self.project.mkdir(parents=True)
        alias = self.root / 'alias'
        alias.symlink_to(self.project.parent, target_is_directory=True)
        self.config_path.write_text(self.config_path.read_text().replace(str(self.stage_root), str(alias)))
        result = self.cli('config-validate')
        self.assertEqual(result.returncode, 1)
        self.assertIn('same location', result.stdout)
        # Distinct roots can still alias the same project through a child symlink.
        self.config_path.write_text(self.config_path.read_text().replace(str(alias), str(self.stage_root)))
        self.stage_root.mkdir()
        (self.stage_root / 'demo').symlink_to(self.project, target_is_directory=True)
        result = self.cli('create', 'demo', '--python', VERSION)
        self.assertEqual(result.returncode, 1)
        self.assertIn('same location', result.stdout)
        self.assertFalse((self.project / '.venv').exists())

    def test_shared_venv_alias_is_rejected_before_installation(self):
        self.project.mkdir(parents=True)
        destination = self.stage_root / 'demo'
        destination.mkdir(parents=True)
        (self.project / '.venv').mkdir()
        (destination / '.venv').symlink_to(self.project / '.venv', target_is_directory=True)
        result = self.cli('create', 'demo', '--python', VERSION)
        self.assertEqual(result.returncode, 1)
        self.assertIn('same environment', result.stdout)
        self.assertFalse((self.project / 'pyproject.toml').exists())

    def test_config_type_diagnostics_identify_the_setting(self):
        original = self.config_path.read_text()
        for text, setting in [
            (original.replace(f'development_root = "{self.project.parent}"', 'development_root = 123'), 'paths.development_root'),
            ('paths = 123\n' + original[original.index('[github]'):], '[paths]'),
            (original.replace('organization = ""', 'organization = false'), 'github.organization'),
        ]:
            with self.subTest(setting=setting):
                self.config_path.write_text(text)
                result = self.cli('config-validate')
                self.assertEqual(result.returncode, 1)
                self.assertIn(setting, result.stdout)
                self.assertNotIn('Traceback', result.stderr)

    def test_project_names_must_generate_valid_python_and_distribution_names(self):
        for name in ['class', 'for', '_demo', 'demo_', 'démo', '123demo']:
            with self.subTest(name=name):
                result = self.cli('create', name, '--python', VERSION)
                self.assertEqual(result.returncode, 1)
                self.assertIn('Project name', result.stdout)
                self.assertFalse((self.project.parent / name).exists())
        import preflight
        for name in ['demo', 'demo_2', 'D']:
            self.assertFalse(any(r.status is Status.ERROR for r in preflight._validate_project_name(name)))
            ast.parse(project_files._file_contents(name, VERSION)['tests/test_import.py'])

    def test_missing_bootstrap_execute_permission_is_repaired_on_resume(self):
        self.scaffold()
        script = self.project / 'scripts/bootstrap.sh'
        content = script.read_bytes()
        script.chmod(0o644)
        plan = project_files.plan_project_files(self.project, 'demo', VERSION)
        self.assertFalse(plan.has_errors)
        self.assertTrue(any('executable permission' in r.message for r in plan.results))
        self.assertFalse(script.stat().st_mode & 0o111)  # Planning must not repair it.
        report = project_files.create_project_files(self.project, 'demo', VERSION)
        self.assertFalse(report.has_errors)
        self.assertTrue(script.stat().st_mode & 0o111)
        self.assertEqual(script.read_bytes(), content)

    def test_interrupted_checkout_stops_with_manual_recovery_guidance(self):
        remote, commit = self.repo()
        dest = self.stage_root / 'demo'
        run('git', 'clone', '--no-checkout', remote, str(dest))
        report = stage.create_stage(self.stage_root, 'demo', remote, Path(sys.executable), commit)
        self.assertTrue(report.has_errors)
        messages = ' '.join(r.message for r in report.results)
        self.assertIn('interrupted checkout', messages)
        self.assertIn('README.md', messages)
        self.assertFalse((dest / '.python-version').exists())
        self.assertFalse((dest / '.venv').exists())

    def test_help_and_version_option(self):
        result = self.cli('create', '--help')
        self.assertEqual(result.returncode, 0)
        self.assertIn('--python', result.stdout)
        self.assertFalse(self.project.exists())

    def test_exact_option_default_and_recorded_pin(self):
        self.assertEqual(python_env.select_python_version(self.project, None), '3.12.10')
        self.assertEqual(python_env.select_python_version(self.project, VERSION), VERSION)
        self.project.mkdir(parents=True)
        (self.project / '.python-version').write_text(VERSION + '\n')
        self.assertEqual(python_env.select_python_version(self.project, None), VERSION)
        with self.assertRaisesRegex(ValueError, 'conflicts'):
            python_env.select_python_version(self.project, '0.0.1')
        with self.assertRaisesRegex(ValueError, 'exact'):
            python_env.select_python_version(self.root / 'new', '3.12')

    def test_current_exact_interpreter_found(self):
        self.assertEqual(python_env.get_python_version(python_env.find_python(VERSION)), VERSION)

    def test_unavailable_python_creates_nothing(self):
        result = self.cli('create', 'demo', '--python', '0.0.1')
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn('Install that exact version', result.stderr)
        self.assertFalse(self.project.exists())

    def test_invalid_config_and_missing_config_fail_cleanly(self):
        for contents in ['bad = [', '[paths]\n', None]:
            if contents is None:
                self.config_path.unlink()
            else:
                self.config_path.write_text(contents)
            result = self.cli('create', 'demo', '--python', VERSION)
            self.assertEqual(result.returncode, 1)
            self.assertNotIn('Traceback', result.stderr)
            self.assertFalse(self.project.exists())

    def test_config_validation_exit_code(self):
        self.assertEqual(self.cli('config-validate').returncode, 0)
        self.config_path.write_text('broken = [')
        self.assertEqual(self.cli('config-validate').returncode, 1)

    def test_dry_run_has_no_project_writes(self):
        result = self.cli('create', 'demo', '--python', VERSION, '--dry-run')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('Project structure', result.stdout)
        self.assertIn('Initial commit', result.stdout)
        self.assertFalse(self.project.parent.exists())

    def test_guided_commit_decline_and_resume(self):
        declined = self.cli('create', 'demo', '--python', VERSION, input='n\n')
        self.assertEqual(declined.returncode, 3, declined.stdout + declined.stderr)
        self.assertIn('Create the initial Git commit?', declined.stdout)
        resumed = self.cli('create', 'demo', input='y\n')
        self.assertEqual(resumed.returncode, 0, resumed.stdout + resumed.stderr)
        self.assertIn('GitHub integration not configured', resumed.stdout)
        again = self.cli('create', 'demo')
        self.assertEqual(again.returncode, 0, again.stdout + again.stderr)
        self.assertNotIn('Create the initial Git commit?', again.stdout)
        self.assertEqual(run('git', 'rev-list', '--count', 'HEAD', cwd=self.project).stdout.strip(), '1')
        self.assertEqual(tomllib.loads((self.project / 'pyproject.toml').read_text())['project']['requires-python'], '==' + VERSION)
        self.assertTrue((self.project / 'scripts/bootstrap.sh').stat().st_mode & 0o111)

    def test_user_edit_still_blocks_without_overwriting(self):
        self.scaffold()
        readme = self.project / 'README.md'
        readme.write_text('User edit\n')
        report = project_files.create_project_files(self.project, 'demo', VERSION)
        self.assertTrue(report.has_errors)
        self.assertEqual(readme.read_text(), 'User edit\n')

    def test_bootstrap_recipe_and_build_pins(self):
        files = project_files._file_contents('demo', VERSION)
        project = tomllib.loads(files['pyproject.toml'])
        self.assertEqual(project['build-system']['requires'], ['setuptools==80.9.0'])
        self.assertIn('setuptools==80.9.0', files['requirements-bootstrap.txt'])
        self.assertIn('--no-build-isolation --no-deps', files['scripts/bootstrap.sh'])
        self.assertIn('pip check', files['scripts/bootstrap.sh'])
        for name in ['requirements-bootstrap.txt', 'requirements.txt']:
            self.assertTrue(all('==' in line for line in files[name].splitlines() if line.strip()))
        script = self.root / 'bootstrap.sh'
        script.write_text(files['scripts/bootstrap.sh'])
        run('bash', '-n', str(script))

    def test_wrong_existing_venv_is_rejected_before_changes(self):
        self.scaffold()
        run(sys.executable, '-m', 'venv', str(self.project / '.venv'))
        (self.project / '.venv/pyvenv.cfg').write_text('include-system-site-packages = true\n')
        report = python_env.plan_python_environment(self.project, Path(sys.executable))
        self.assertTrue(report.has_errors)

    def test_remote_freshness_uses_server_not_cached_refs(self):
        remote, commit = self.repo()
        resolved, report = github_ops.verify_remote_commit(self.project)
        self.assertFalse(report.has_errors)
        self.assertEqual(resolved, commit)
        other = self.root / 'other'
        run('git', 'clone', remote, str(other), env=self.environment)
        (other / 'extra').write_text('new')
        run('git', 'add', '.', cwd=other)
        run('git', 'commit', '-m', 'new remote revision', cwd=other, env=self.environment)
        run('git', 'push', cwd=other, env=self.environment)
        resolved, report = github_ops.verify_remote_commit(self.project)
        self.assertTrue(report.has_errors)
        self.assertIsNone(resolved)

    def test_stage_rejects_stale_dirty_and_wrong_origin(self):
        remote, commit = self.repo()
        dest = self.stage_root / 'demo'
        run('git', 'clone', remote, str(dest))
        self.assertFalse(stage.validate_stage_checkout(dest, remote, commit).has_errors)
        self.assertTrue(stage.validate_stage_checkout(dest, remote, '0' * 40).has_errors)
        self.assertTrue(stage.validate_stage_checkout(dest, 'other', commit).has_errors)
        (dest / 'extra').write_text('keep me')
        report = stage.create_stage(self.stage_root, 'demo', remote, Path(sys.executable), commit)
        self.assertTrue(report.has_errors)
        self.assertFalse((dest / '.venv').exists())
        self.assertEqual((dest / 'extra').read_text(), 'keep me')

    def test_stage_requires_verified_commit(self):
        report = stage.create_stage(self.stage_root, 'demo', 'remote', Path(sys.executable))
        self.assertTrue(report.has_errors)
        self.assertFalse(self.stage_root.exists())

    @unittest.skipUnless(os.environ.get('PG_RUN_INSTALL_TESTS') == '1', 'Set PG_RUN_INSTALL_TESTS=1 to install dependencies and test reproduction')
    def test_real_development_bootstrap_and_independent_stage_reproduction(self):
        self.scaffold()
        # Dependency installation runs from the generated recipe, not from test doubles.
        run('bash', str(self.project / 'scripts/bootstrap.sh'), env=self.environment)
        run('git', 'init', '-b', 'main', cwd=self.project, env=self.environment)
        run('git', 'add', '.', cwd=self.project, env=self.environment)
        run('git', 'commit', '-m', 'Initial project setup', cwd=self.project, env=self.environment)
        remote = self.root / 'remote.git'
        run('git', 'init', '--bare', '-b', 'main', str(remote), env=self.environment)
        run('git', 'remote', 'add', 'origin', str(remote), cwd=self.project)
        run('git', 'push', '-u', 'origin', 'main', cwd=self.project, env=self.environment)
        # Staging must use the verified branch even if the remote default points elsewhere.
        run('git', 'symbolic-ref', 'HEAD', 'refs/heads/another-default', cwd=remote)
        commit, verification = github_ops.verify_remote_commit(self.project)
        self.assertFalse(verification.has_errors)
        report = stage.create_stage(self.stage_root, 'demo', str(remote), Path(sys.executable), commit)
        self.assertFalse(report.has_errors, '\n'.join(r.message for r in report.results))
        dest = self.stage_root / 'demo'
        inventory = "import importlib.metadata as m,json; print(json.dumps(sorted((d.metadata['Name'].lower(),d.version) for d in m.distributions())))"
        dev_inventory = run(str(self.project / '.venv/bin/python'), '-I', '-c', inventory, cwd=self.root).stdout
        stage_inventory = run(str(dest / '.venv/bin/python'), '-I', '-c', inventory, cwd=self.root).stdout
        self.assertEqual(dev_inventory, stage_inventory)
        # Repeating setup uses the same checkout and an independent, matching environment.
        again = stage.create_stage(self.stage_root, 'demo', str(remote), Path(sys.executable), commit)
        self.assertFalse(again.has_errors, '\n'.join(r.message for r in again.results))

    def test_workflow_preserves_three_confirmation_gates_and_stage_order(self):
        ok = ValidationReport((Result(Status.OK, 'ok'),))
        create = ValidationReport((Result(Status.CREATE, 'needed'),))
        configuration = {'paths': {'development_root': str(self.root), 'stage_root': str(self.stage_root)},
                         'github': {'organization': 'owner', 'ssh_host': 'github.example'},
                         'git': {'user_name': 'Test', 'user_email': 'test@example.invalid'},
                         'ssh': {'private_key': 'key', 'public_key': 'key.pub'}}
        import contextlib
        with contextlib.ExitStack() as stack:
            stack.enter_context(patch.object(workflow, '_load_config', return_value=configuration))
            stack.enter_context(patch.object(workflow, 'select_python_version', return_value=VERSION))
            stack.enter_context(patch.object(workflow, 'find_python', return_value=Path(sys.executable)))
            for name in ['validate_config', 'run_preflight', 'create_project_structure', 'create_python_environment',
                         'create_project_files', 'initialize_git_repository', 'validate_git_identity', 'create_initial_commit',
                         'validate_github_configuration', 'validate_github_ssh', 'configure_github_remote', 'push_initial_branch']:
                stack.enter_context(patch.object(workflow, name, return_value=ok))
            for name in ['plan_initial_commit', 'plan_github_remote', 'plan_initial_push']:
                stack.enter_context(patch.object(workflow, name, return_value=create))
            confirm = stack.enter_context(patch.object(workflow, '_confirm', return_value=True))
            verify = stack.enter_context(patch.object(workflow, 'verify_remote_commit', return_value=('a' * 40, ok)))
            staging = stack.enter_context(patch.object(workflow, 'create_stage', return_value=ok))
            stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
            self.assertEqual(workflow.run_create_workflow('demo', python_version=VERSION), 0)
            self.assertEqual([c.args[0] for c in confirm.call_args_list], ['Create the initial Git commit?', 'Has the GitHub repository been created?', 'Push the current branch to GitHub?'])
            verify.assert_called_once()
            self.assertEqual(staging.call_args.kwargs['expected_commit'], 'a' * 40)
            for answers in [[False], [True, False], [True, True, False]]:
                staging.reset_mock()
                confirm.side_effect = answers
                self.assertEqual(workflow.run_create_workflow('demo', python_version=VERSION), 3)
                staging.assert_not_called()
            confirm.side_effect = None
            staging.reset_mock()
            verify.return_value = (None, ValidationReport((Result(Status.ERROR, 'remote mismatch'),)))
            with self.assertRaisesRegex(ValueError, 'Setup failed'):
                workflow.run_create_workflow('demo', python_version=VERSION)
            staging.assert_not_called()


if __name__ == '__main__':
    unittest.main()
