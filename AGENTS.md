# Instructions for maintaining pyprojectgen

Instruction version: 1.2

## Purpose and scope

Maintain the source, documentation, and tests together as part of each relevant
change. Do not leave documentation maintenance to the user after delivering code.
Apply the universal extension for Markdown documentation work; the coding rules below remain in force for source and test changes.

This is a generic initial Python project setup tool. Its responsibility ends at
handover of the initial project scaffold and environment reconstruction recipe.
The generated project's owner maintains that project's specifications afterward.
Do not embed a particular customer's project, deployment stack, credentials, or
machine paths in the generator.

## Understand before changing code

Before code changes, read the relevant source and documentation and inspect the Git
branch, working tree, and staged changes. Preserve unrelated or uncommitted work.
Trace the affected behavior and prerequisites, including workflow order,
confirmation gates, restart checks, generated files, and error handling.

Validate the premise and assumptions against evidence. Identify existing behavior
that must be preserved and obtain agreement for material changes outside the
requested scope. Do not refactor, consolidate, remove files, or add features just
to simplify the implementation. Account for each removed file's responsibilities.
Fewer files or passing newly written tests alone do not prove equivalence.

Treat implementation as evidence of current behavior and approved requirements
as evidence of intended behavior. If they conflict, explain the discrepancy;
do not silently change either to make them agree. Ask only when a material
uncertainty prevents reliable progress.

## Markdown Documentation Contracts

Use `llm.software.documentation.process.md` for the universal documentation workflow and writing/review standards. Its first-time requirements clarification uses `llm.clarification.process.md`. The invoking prompt must provide access to those extensions; they are not assumed to be files in this repository. This section defines only pyprojectgen's Markdown inventory and document-specific requirements.

The six repository-level documents below are required. Repository documentation filenames are uppercase. Generated project READMEs are template outputs, not additional repository-level maintenance records. Do not create additional reports or status files unless required by the assigned work.

### README.md

- **Audience:** developers with basic Python and terminal knowledge who want to use pyprojectgen.
- **Purpose:** current user guide for the generator.
- **Include:** purpose and scope; key concepts; prerequisites; configuration; commands, options, defaults, and exit codes; generated files; automated workflow and confirmation gates; development bootstrap; local staging; recovery; test-running instructions; current limitations; links to related records.
- **Exclude:** detailed release history, execution logs, and backlog item tracking. Summarize relevant limitations and link to their owning records.
- **Update when:** user-visible commands, defaults, prerequisites, configuration, outputs, workflow, bootstrap/reproduction, restart behaviour, test-running instructions, or limitations change.
- **Specific rules:** distinguish the generator from generated projects. Use phases for the high-level setup process and steps within each phase. Explain that development bootstrap runs separately from `create`, while optional local staging currently runs within `create`. Describe local staging as a limited independent Python installation/test check, including shared-machine risks; it does not validate a production-like deployment. Explain development versus staging installation and where the generator's initial-setup responsibility ends. Describe the generator's unittest runner, generated projects' pytest tests, the opt-in installation switch, and temporary-project isolation and cleanup. Keep test counts tied to recorded runs rather than permanent promises about future suites.

### CHANGES.md

- **Audience:** users upgrading the generator and maintainers reviewing releases.
- **Purpose:** concise release history.
- **Include:** meaningful delivered changes, reasons, compatibility effects, and required user actions, grouped by actual release.
- **Exclude:** individual editorial adjustments, working review conversations, future proposals, and detailed test evidence.
- **Update when:** a delivered change materially affects functionality, compatibility, or use. Routine documentation edits need no release entry.
- **Specific rules:** do not invent a release or bump the project version for documentation alone. Put later release sections above earlier ones. The existing 0.2.1 preservation map is evidence for that release; do not rewrite it for every edit. Add a new comparison only when warranted. Make factual corrections explicit within their release context.

### BACKLOG.md

- **Audience:** the repository owner and maintainers planning future work.
- **Purpose:** track proposals, planned enhancements, deferred work, and unresolved design decisions.
- **Include:** stable item ID, status, current limitation, desired outcome, material dependencies, unresolved decisions, and last-updated date; approval scope and implementation/validation references where applicable.
- **Exclude:** full user instructions, release history, and detailed validation logs.
- **Update when:** a relevant proposal, decision, scope, dependency, progress, or completion status changes. Read related entries before proposing or implementing related work.
- **Specific rules:** reuse existing IDs and entries. Keep completed, deferred, and superseded entries, linking replacements. Distinguish proposal approval from authorization to implement; an implementation plan needs approval unless the current request already authorizes it. Completion requires implementation and validation references. Delivered changes belong in CHANGES.md; test evidence belongs in VALIDATION.md.

### VALIDATION.md

- **Audience:** maintainers and reviewers assessing what was verified.
- **Purpose:** evidence record for material validation runs and reviews.
- **Include:** date; release and commit when available, or explicit uncommitted-working-tree identification; operating system, Python version, relevant execution conditions; exact test commands and pass/fail/skip counts for test runs; review scope and method for documentation reviews; evidence source; important coverage, failures, limitations, and corrective retests.
- **Exclude:** general claims that the tool works everywhere, operating instructions, and planned tests presented as completed evidence.
- **Update when:** meaningful new validation evidence, corrective retests, or evidence resolving a recorded limitation becomes available.
- **Specific rules:** append concise dated entries. State unknown revision or environment details rather than infer them. Identify assistant-executed, user-supplied, or other reported evidence. Mac evidence supplements Linux evidence. Limit conclusions to the tested revision, platform, and scenarios; local-remote tests do not establish real GitHub authentication or deployment behaviour. Mark resolved or superseded limitations with references to the later evidence while retaining earlier results.

### REPLACEMENT.md

- **Audience:** users replacing an older generator checkout or package.
- **Purpose:** version-scoped replacement and migration guide.
- **Include:** applicable source/destination versions or layouts; backup and inspection steps; replacement actions; obsolete-file handling; compatibility effects; validation steps.
- **Exclude:** routine project setup, universal cleanup rules, and unsupported automatic migration of generated projects.
- **Update when:** delivery layout, obsolete files, installation methods, or compatibility changes affect replacement.
- **Specific rules:** limit historical removal instructions to their applicable versions. Protect Git history, environments, user files, and unrelated work. Identify destructive actions and recovery options; absence from an archive is insufficient reason to delete a file. Do not imply that existing generated projects can be overwritten or migrated automatically.

### AGENTS.md

- **Audience:** agents and maintainers working on pyprojectgen.
- **Purpose:** repository-specific working instructions and Markdown document contracts.
- **Include:** product boundaries, coding safeguards, the Markdown inventory and per-document responsibilities, repository-specific test and completion requirements, and references to the universal documentation process.
- **Exclude:** duplicated universal documentation procedures, user operating instructions, release history, and progress or test-result logs.
- **Update when:** repository responsibilities, required document inventory, document contracts, or working policy change.
- **Specific rules:** increment the instruction version for substantive policy changes. Preserve coding safeguards when restructuring documentation instructions. This file does not authorize deployment, publication, merging, or unrelated changes.

## Code and Test Maintenance

The following rules govern code work and remain separate from the Markdown documentation process.

### tests/test_setup.py and other tests

Maintain tests with behavior changes. Cover the requested behavior, preservation
of affected existing behavior, and meaningful failure/restart paths. Keep the
fast regression checks separate from opt-in dependency installation checks.
Use temporary projects and local Git remotes; do not use personal repositories,
credentials, or live deployments by default. Do not remove or weaken a test merely
to obtain a pass; establish whether its expected behavior is still correct.

Keep README test commands and VALIDATION coverage descriptions accurate when
test names, counts, prerequisites, or behavior change. Counts belong to a specific
recorded run, not a permanent promise about all future suites.

### Source comments, docstrings, and generated documentation

Explain high-level behavior, non-obvious constraints, and rationale. Keep comments
consistent with implementation. Do not merely narrate each statement. Never rely
on private discussions, phrases such as "as agreed," or unexplained chat history.
Explain the reason directly so a new maintainer can understand the code alone.

When template behavior changes, also inspect generated README text, bootstrap
instructions, configuration examples, and relevant metadata/dependency files.
Keep the selected interpreter and reproduction specifications consistent. Preserve
the initial-template conflict policy unless a change is explicitly requested.

## Repository Completion Checks

For Markdown work, apply the universal extension's review and delivery process. In addition, inspect the Git branch, working tree, staged and unstaged diffs, and relevant untracked files before replacing repository files. Preserve unrelated work. Check whitespace and repository-specific commands, filenames, versions, defaults, and limitations.

For source or test changes:

1. Review the diff against the starting point and account for behaviour changes and removed files. Passing new tests alone does not establish preservation.
2. Maintain affected tests and apply the universal extension to affected Markdown documentation.
3. Run appropriate checks and record results in VALIDATION.md. After corrections, rerun affected checks; avoid unrelated expensive reruns without a reason.
4. Inspect staged and unstaged changes separately, including relevant new files, and check whitespace.
5. Summarize code changes, preserved behaviour, verification, and remaining limits. Report execution or repository updates only with evidence.
