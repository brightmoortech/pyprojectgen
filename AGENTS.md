# Instructions for maintaining pyprojectgen

Instruction version: 1.1

## Purpose and scope

Maintain the source, documentation, and tests together as part of each relevant
change. Do not leave documentation maintenance to the user after delivering code.
Keep updates concise and proportional; unchanged files need no cosmetic edits.

This is a generic initial Python project setup tool. Its responsibility ends at
handover of the initial project scaffold and environment reconstruction recipe.
The generated project's owner maintains that project's specifications afterward.
Do not embed a particular customer's project, deployment stack, credentials, or
machine paths in the generator.

## Understand before changing

Before editing, read the relevant source and documentation and inspect the Git
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

## File responsibilities and update rules

### README.md

Maintain this as the current user guide. Update affected sections when changing
commands, options, defaults, prerequisites, configuration, generated files,
workflow, confirmation gates, exit codes, bootstrap/reproduction instructions,
restart behavior, or limitations.

Check examples against the implementation and CLI help. Distinguish implemented
features from proposals. Explain development and staging differences and where
initial setup finishes. Keep release details and test logs in their own records.

### CHANGES.md

Maintain a concise release history: what changed, why, relevant compatibility
effects, and any required user action. Group multiple edits for the same release
in one section. Use the actual project version; do not invent a new release or
bump the version merely to update documentation.

Preserve previous release sections. Add future releases above them rather than
rewriting earlier behavior as if it had always existed. The existing 0.2.1
preservation map is historical evidence for that release, not a table to rewrite
for every later edit. Add a new comparison only when a later change warrants it.
Correct factual errors transparently without erasing the original context.

### BACKLOG.md

Maintain planned enhancements and deferred work here, using the uppercase filename
`BACKLOG.md`. Read relevant entries before proposing or implementing related changes.

Give each item a stable ID, status, current limitation, desired outcome, and any
material dependencies or unresolved decisions. Reuse existing entries rather than
duplicating them; update the last-updated date when content changes. Distinguish
proposals, approved scope, and completed implementation. Recording or approving a
backlog item does not itself authorize implementation; obtain approval for its
implementation plan unless the current request already provides that approval.

Update affected entries when scope, decisions, progress, or completion changes.
Retain completed, deferred, and superseded entries as history, linking replacements
where relevant. Mark work complete only with implementation and validation evidence.
Keep README descriptions of current behaviour separate from planned features;
record delivered changes in CHANGES.md and test evidence in VALIDATION.md.

### VALIDATION.md

Maintain an evidence record, not a general assertion that the tool works. For
each material validation run, record:

- Date and release, plus commit ID when available. If testing uncommitted changes,
  label the working tree accordingly; do not attribute results to an older commit.
- Operating system, Python version, and relevant execution conditions.
- Exact command and pass/fail/skip counts. Separate skipped, untested, and failed
  checks from passing checks.
- Evidence source: assistant-executed output, user-supplied output, or another
  identified report. Do not present user-executed checks as your own execution.
- Important coverage, failures, unresolved limitations, and corrective retests.

Append concise dated entries for meaningful new evidence; preserve earlier
results and label superseded limitations appropriately. User-supplied Mac results
supplement Linux results rather than replacing them. If an exact interpreter or
OS version is not established for a run, state that instead of inferring it.
Results apply to the tested revision, platform, and scenarios; do not extend them
to later code changes, real GitHub authentication, or other environments without
evidence. A documentation-only edit does not require rerunning installation tests.

### REPLACEMENT.md

Maintain this as a version-scoped replacement/migration guide. Update it when
delivery layout, obsolete files, installation methods, or compatibility changes
affect replacement. Label source and destination versions or affected layouts
where known. Keep historical removal instructions clearly limited to the version
they apply to; never present them as cleanup rules for every future release.

Protect Git history, environments, user files, and unrelated changes. State backup,
inspection, and validation steps. Identify destructive actions explicitly; do not
authorize deletion merely because a file is absent from a new archive. Do not
assume existing generated projects can be overwritten or migrated automatically.

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

### AGENTS.md

Change this file only when maintenance policy or repository responsibilities
change. Do not turn it into another progress log or duplicate the README. It does
not grant authority to deploy, publish, merge, or perform unrelated changes.

## Completion check

Before delivering a change:

1. Review the diff against the starting point and account for behavior changes
   and file removals. Check tracked changes and relevant new files.
2. Update only the documentation and tests affected by the change. Explain any
   documentation that remains incomplete because evidence is unavailable.
3. Run appropriate checks and record actual results. After a correction, rerun
   affected checks; do not repeat unrelated expensive checks without a reason.
4. Check whitespace and consistency of commands, filenames, versions, defaults,
   and stated limitations. Staged and unstaged diffs require separate inspection;
   ordinary Git diffs omit untracked files.
5. Summarize what changed, what was preserved, how it was validated, and remaining
   limits. Report saves, commits, uploads, and tests only when evidence confirms
   them. Never claim a user's checkout or remote repository was updated merely
   because a replacement file was generated.

Do not create additional reports, status files, or maintenance records unless
needed for the requested work. Reuse these files and keep their roles distinct.
