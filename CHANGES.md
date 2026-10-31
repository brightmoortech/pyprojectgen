# Changes in 0.2.1

## Scope

This release retains the original 0.1.0 guided initial-setup architecture and
all eleven Python modules. It does not introduce a new CLI architecture or a
persistent phase ledger. Project development and dependency maintenance after
initial setup remain the project owner's responsibility.

## Corrections

1. **Consistent Python selection.** Add `create --python X.Y.Z`; default new pins
   to 3.12.10 and retain recorded pins on resume. Find the exact installed
   interpreter before creating resources. Use it consistently for generated
   Python requirements, environment creation, bootstrap, and staging validation.
2. **Reproduction specifications.** Pin setuptools 80.9.0 in build metadata and
   bootstrap requirements. Preserve pip and test-package pins. Install project
   code without build isolation or dependency resolution after installing the
   specified tools/packages; check dependency compatibility. Preserve separate
   editable development and non-editable staging installations.
3. **Verified staging source.** Verify live origin branch tip against development
   HEAD after publication. Clone/check out that exact commit regardless of remote
   default branch. Refuse an existing staging copy with a different origin,
   revision, or local changes. Do not pull/reset automatically. Report execution
   checks deferred during preview.
4. **Outcome exit codes.** Return failure for reported validation/execution errors,
   cancellation for declined gates, and interruption status for interrupted input.
   Validate configuration before loading required settings so configuration
   failures produce clear diagnostics. Preserve partial work for review/resume.
5. **Documentation.** Replace outdated README descriptions with implemented command
   behavior, completion boundaries, bootstrap/reproduction instructions, restart
   semantics, and limits. Add module/function docstrings explaining behavior and
   rationale independently of external discussions.

## Preservation map

| Original module | Responsibilities retained | Targeted changes |
| --- | --- | --- |
| `pyprojectgen.py` | config-init, config-validate, create, argparse help | Python option and outcome handling |
| `config.py` | Machine-local template and preference validation | Documentation only |
| `models.py` | Status, Result, ValidationReport | Documentation only |
| `preflight.py` | Configuration, project name, interpreter availability, Git checks | Documentation only |
| `project_structure.py` | Fixed src-layout scaffold, existing-resource checks | Documentation only |
| `python_env.py` | Version file, isolated venv creation and validation | Exact interpreter selection, existing environment isolation checks |
| `project_files.py` | Initial templates, equality checks, preservation on conflict, executable bootstrap | Selected version and exact build-tool specification, bootstrap installation flags and documentation |
| `git_ops.py` | Git initialization, identity checks, commit planning/execution | Documentation only |
| `github_ops.py` | Key checks, SSH test, expected origin, branch/upstream checks, non-force push | Live branch-tip verification and documentation |
| `stage.py` | Independent clone/venv, tooling/dependency installation, non-editable install, tests | Commit/origin/clean-state checks, build-tool control, dependency check |
| `workflow.py` | Ordered phases, all three confirmation gates, optional GitHub, failure stops and resource-based resumption | Selected version, verified staging commit, outcome propagation, preview fixes |

Original LICENSE, example configuration, and .gitignore are retained. Tool
package metadata is versioned 0.2.1 with an exact setuptools build requirement.
Added files: this change map, validation report, replacement guide, and tests.
No original module was removed or consolidated.

## Existing boundaries retained

- Initial commits still use `git add .`; inspect project contents before agreeing.
- GitHub repository creation remains manual.
- Dry-run can perform SSH authentication over the network.
- Generated files must match the initial template. User edits are not merged.
- Development bootstrap remains a separate generated script.
- Configuration does not enforce independent development/stage roots.
- Pins assume compatible platforms and available packages; no artifact-hash or
  offline archive guarantee is added.


## Pre-commit audit follow-up (0.2.1)

The following corrections extend this release's initial changes; it remains an
uncommitted release candidate rather than a separately numbered release.

- `config.py`: validate TOML table/value types with setting-specific diagnostics;
  reject development/staging root aliases. This adds executable behavior beyond
  the documentation-only changes listed in the initial preservation map.
- `workflow.py`: reject project/environment aliases before setup and recheck before
  staging; simplify exception-based error stops and return explicit success codes.
- `preflight.py`: reject Python keywords and names incompatible with generated
  distribution metadata. This also extends the initial documentation-only change.
- `project_files.py`: repair missing bootstrap executable permission only after
  matching content passes validation; preserve the existing conflict policy.
- `stage.py` and README: identify possible interrupted checkouts and provide manual
  preserve-and-retry guidance. No automatic reset or recovery machinery is added.
- Tests: cover collision/alias guards, naming, typed configuration errors, executable
  permission recovery, and safe stopping after an interrupted checkout.
- README: document workflow ownership of the environment before handover. Detection
  of extra installed packages is deferred as a future enhancement; the workflow does
  not remove unexpected packages.
- VALIDATION: retain the original Linux run, append user-reported Mac results, and
  record follow-up checks separately. Earlier results do not verify later code.

The original guided phases, three confirmation gates, and eleven modules remain.
