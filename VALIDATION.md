# Validation record

Release: 0.2.1
Date: 2026-10-31
Host: Linux, Python 3.12.14

## Current status (recorded 2026-11-01)

The 0.2.1 audit follow-up has passing 23-test results on Linux and on the user's
Mac. The later Mac entry below resolves the historical pending status. Subsequent
README and maintenance-record updates changed no executable code. Earlier entries
remain evidence for their original revisions and conditions.

## Measured results

All 16 tests passed with integration installation enabled (22.358 seconds).

```bash
PG_RUN_INSTALL_TESTS=1 PIP_NO_INDEX=1 \
  PIP_FIND_LINKS=/tmp/pg-reproduction-wheels \
  python3 -m unittest discover -s tests -v
```

The wheel directory was populated from the exact package versions declared by
the template. It is a temporary verification input, not part of the release or
a requirement to use the tool; ordinary bootstrap can obtain packages from its
configured package index.

Coverage includes:

- CLI help and exact Python option, default, recorded pin, conflicting pin, and
  unavailable-interpreter failure before project creation.
- Missing/malformed configuration and nonzero validation failure statuses.
- Dry-run without project writes, including a previously absent development root.
- Real local create, declining initial commit, resuming, and repeat setup without
  another commit; template version consistency and bootstrap executable mode.
- Preservation of edited generated files with a blocking error.
- Pinned build requirements, controlled install flags, and Bash syntax.
- Rejection of an existing environment with incompatible isolation settings.
- Live remote verification after another checkout advances the server without
  refreshing the development clone's tracking refs.
- Rejection of wrong-origin, stale, or dirty staging without installing into it.
- All three confirmation prompts and cancellation gates; staging is not called
  after a declined confirmation or failed remote verification.
- Actual generated development bootstrap, independent stage clone/install/test,
  non-default remote branch selection, and successful staging rerun.
- Equality of installed distribution names and versions between editable
  development and non-editable staging environments.

## Source and documentation review

Compared the corrected sources to the original archive. All eleven original
modules and their top-level functions/classes are retained; documentation-only
changes are separated in CHANGES.md. Retention of names alone is not treated as
proof of behavior: workflow gate tests and real resource/reproduction checks
provide additional evidence.

Reviewed the original/corrected diff, module/function docstrings, main README,
generated README, configuration comments, and generated bootstrap. Explanations
refer to observable behavior and rationale, not private conversation history.

The distribution wheel also built successfully using the pinned setuptools version.
Its contents include all eleven modules and the `pyprojectgen:main` console entry point.

## Limits

- macOS execution and Python 3.12.10 execution have not been run in this host.
  Repeat tests using that interpreter on the target Mac.
- Git interactions use temporary local bare repositories. The workflow controller
  test substitutes SSH/authentication and remote action results; personal GitHub
  authentication and network behavior are not verified here.
- The integration checks establish package-version reproduction on this platform,
  not byte-identical artifacts, offline availability, or cross-platform equivalence.
- Tests do not change the user's generator checkout, generated project, or deployment.


## User-reported Mac validation of the earlier 0.2.1 candidate

Date: 2026-10-31. Evidence: user-supplied terminal output. The changes were
uncommitted on branch `pyprojectgen-v0.2`. The host was identified as the user's
Mac; these commands did not print the exact OS or Python version, so those are
not independently established for these runs.

```bash
python3 -m unittest discover -s tests -v
```

Result: 16 discovered, 15 passed, 1 installation test skipped, no failures
(3.463 seconds).

```bash
PG_RUN_INSTALL_TESTS=1 python3 -m unittest discover -s tests \
  -p test_setup.py -k test_real_development_bootstrap -v
```

Result: 1 installation/reproduction test passed, no failures (8.258 seconds).
The user also supplied a successful `git diff --check` with no output. These
results supplement the original Linux evidence but precede the audit follow-up
code changes below. They do not validate those later changes.

## Pre-commit audit and follow-up validation

Date: 2026-10-31. Release: 0.2.1, uncommitted follow-up candidate.
Evidence: assistant-executed source review, temporary adversarial probes, and tests.
Host: Linux, Python 3.12.14. No user checkout or personal GitHub repository was changed.

The audit reproduced a path collision that let staging change an editable
development installation to a non-editable one. It also reproduced acceptance of
invalid package names, missing executable permissions, and safe but unclear stopping
after interruption between cloning and checkout. Follow-up regression checks cover
path aliases/shared environments, typed configuration diagnostics, naming,
permission repair, and interrupted-checkout guidance.

Unexpected-package retention was reproduced only by explicitly introducing an
extra package. That probe did not establish that normal workflow execution adds
unrelated packages. Given workflow ownership until setup completion, detection is
a documented future enhancement, not a current release blocker. An interrupted
checkout is a Minor manual-recovery inconvenience; no automatic recovery is added.
These conclusions supersede the initial audit's Major classification of those
two cases.

```bash
PG_RUN_INSTALL_TESTS=1 PIP_NO_INDEX=1 \
  PIP_FIND_LINKS=/tmp/pg-reproduction-wheels \
  python3 -m unittest discover -s tests -v
```

Result: 23 tests passed, no failures or skips (19.260 seconds), including actual
development bootstrap and independent staging reconstruction with matching
installed package versions. Tests preserve all three confirmation gates, failure
stops, existing-file conflict handling, and resource-based resumption.

All eleven original modules remain. No build/deployment features or automatic
package removal were introduced. Mac validation of this follow-up is pending;
the earlier Mac results above must not be treated as verification of this candidate.

## Mac validation of the audit follow-up

Recorded: 2026-11-01. Release: 0.2.1. Evidence: user-supplied terminal output,
reported after pushing commit `0b943f9` on branch `pyprojectgen-v0.2`. The test
output itself did not print the commit, exact macOS version, or Python version.
The actual execution date was not printed by the command.

```bash
PG_RUN_INSTALL_TESTS=1 python3 -m unittest discover -s tests -v
```

Result: 23 tests passed, no failures or skips, in 12.421 seconds. The output
includes the real development bootstrap and independent staging reproduction
test, as well as validation, confirmation, conflict, and retry checks.

This resolves the previously pending Mac test run for the audit follow-up. It
supplements the Linux evidence; it does not verify live GitHub authentication,
remote staging, production deployment, or every Python/OS combination.

## README review and documentation checks

Date: 2026-11-01. Release: 0.2.1, documentation-only working changes.
Evidence: assistant-executed source/CLI inspection and documentation checks.
These changes have not been committed to the user's repository by the assistant.

Completed two review-and-fix passes: implementation accuracy, followed by
terminology, information flow, repetition, and audience-appropriate detail.
Reviewed the three-phase structure, phase outputs and recovery, exact Python
selection, file population, separate development bootstrap, and local staging
limitations against the source. Corrected ambiguous wording about installing
Python and made the current exact-version default requirement explicit.

Checked CLI help with:

```bash
python3 pyprojectgen.py --help
python3 pyprojectgen.py create --help
```

Twenty documentation checks passed, covering links and anchors, Markdown fences
and whitespace, implemented phases, agreed terms and placeholders, current Python
default, test count, generated-file coverage, recovery-heading consistency, and
Bash example syntax checked with `bash -n`. Byte comparisons confirmed no
executable code changes. The delivery archive was checked for ZIP integrity and
consistency with its source files.

Installation tests were not rerun for these documentation-only changes. These
checks are documentation evidence, not additional runtime or deployment tests.
