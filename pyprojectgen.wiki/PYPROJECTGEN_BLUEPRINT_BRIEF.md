# pyprojectgen — Future Project Blueprints

**Status: FUTURE — backlog enhancement.** This living brief proposes future capabilities for pyprojectgen. It is not an implementation specification or authorization to implement. No blueprint described here is claimed to be implemented in pyprojectgen.

## 1. Objective and Scope

Extend pyprojectgen to generate reusable engineering and technical foundations for Python projects. Support projects without databases, projects connecting to PostgreSQL, and projects managing their own PostgreSQL infrastructure through Docker Compose.

Generated foundations should be independently installable, configurable, testable and reproducible. Avoid introducing infrastructure or dependencies that the selected project does not need. Review the existing generator architecture and backlog before specifying implementation changes.

## 2. Proposed Blueprint Options

| Blueprint | Capabilities |
|---|---|
| Python Foundation | Package structure, pinned dependencies, virtual environment, bootstrap, engineering governance, documentation and unit testing. |
| Python + PostgreSQL | Python Foundation plus PostgreSQL driver, connection configuration and database integration test infrastructure. |
| Python + Managed PostgreSQL | Python + PostgreSQL plus shared Compose definition, environment management, external persistence, independent development and staging instances, and database test safety. |

These are proposed capability groupings, not a prescribed command interface or template implementation architecture.

### 2.1 Blueprint strategy

Use a shared foundation with optional, additive capabilities. The Python Foundation supplies the common project structure and engineering practices; the PostgreSQL capability adds database connectivity; the managed infrastructure capability adds Docker provisioning and test isolation. Avoid three independently maintained copies of the same foundation. Integrate with the existing generator and its configuration mechanisms rather than creating a parallel generator. The internal template mechanism, selection interface and upgrade strategy are decisions for future implementation planning.

`<project>` denotes the generated project's name, not pyprojectgen itself. `<workspace>` denotes the operator's workspace root. Angle-bracket expressions in this brief are placeholders, not literal directory names or executable shell expressions. Resolve project names into valid Python package, PostgreSQL identifier and infrastructure names according to documented naming rules; for example, `<package>` represents the valid Python import name derived from `<project>`. Do not require the receiving developer or LLM to know another project or conversation.

Separate generation-time inputs (project name, selected capabilities, supported platforms, version pins and applicable documentation) from runtime configuration (host, port, database, credentials and storage). The generator produces version-controlled definitions and templates; operators supply local values. Generating source files must not itself provision a database or start containers unless separately specified and authorized. Existing user files must not be overwritten silently.

### 2.2 Proposed delivery sequence

1. Assess the current pyprojectgen repository, supported generation workflows and backlog. Identify existing capabilities to retain rather than replace.
2. Establish the shared foundation and documentation templates; validate generation, clean installation and unit tests.
3. Add PostgreSQL connectivity as an optional capability; validate driver compatibility and authentication.
4. Add managed PostgreSQL infrastructure, environment management, identity and staging safety as a dependent capability; validate the complete setup and container replacement workflows.
5. Add later capabilities only after their requirements are specified and approved. Validate each supported combination and regress the simpler blueprints when adding a capability.

This sequence is a proposed strategy, not implementation authorization or a commitment to a specific command syntax.

## 3. Engineering Governance and Documentation

Generate project-appropriate documentation and governance templates. Do not overwrite existing project documents or introduce task-specific LLM instructions as universal rules.

### 3.1 Document architecture and authority

Generate the following documents as applicable. Paths are relative to the generated repository root. The wiki directory is `<project>.wiki/`; references must resolve to the selected generated project name. Governance templates contain reusable rules; project requirements and execution records must not contain invented business behavior or historical results.

| File | Audience and purpose | Authority and maintenance trigger |
|---|---|---|
| `README.md` | Users and consuming application developers: purpose, installation, configuration, usage and operational guidance. | Describes validated available behavior; update when user-facing functionality becomes available or changes. |
| `AGENTS.md` | Coding agents and LLMs: a navigation guide to the repository documentation. | Registry and task-dependent reading guidance only; update when document locations, existence, purposes, authority or dependencies change. |
| `<project>.wiki/DEVELOPMENT.md` | Contributors and maintainers: bootstrap, dependencies, development configuration, environment provisioning and test execution. | Operational development instructions; update when actual development workflows or commands change. |
| `<project>.wiki/FUNCTIONAL_REQ.md` | Stakeholders and implementers: what the product must do, business rules, lifecycle policies and user/role capabilities. | Authoritative functional requirements; update only through authorized requirements decisions. |
| `<project>.wiki/TECHNICAL_REQ.md` | Architects, developers and testers: how requirements are realized, technology, architecture, data, interfaces, security, deployment, stages and acceptance criteria. | Authoritative technical requirements; update through authorized technical decisions. |
| `<project>.wiki/CODING_CONVENTIONS.md` | Developers and coding agents: consistent engineering practices and interface boundaries. | Approved coding standards; update when conventions change. |
| `<project>.wiki/TESTING.md` | Developers, testers and reviewers: how tests are designed, executed, isolated, evidenced and accepted. | Testing governance, not a substitute for acceptance criteria; update when testing rules change. |
| `<project>.wiki/TEST_SPECIFICATION.md` | Test developers and reviewers: what is tested and why, unique test identifiers, requirement/acceptance references and executable test mapping. | Coverage and traceability; update when tests or applicable requirements change. |
| `<project>.wiki/TEST_EXECUTION_PHASE<phase>_STAGE<stage>.md` | Reviewers and maintainers: actual validation evidence for one stage. | Evidence, not a requirements source; create after actual validation and checkpoint verification, never fabricate results or prepopulate historical evidence. Adapt naming to the project's approved delivery process. |
| `<project>.wiki/DOCUMENT_GOVERNANCE.md` | Anyone creating, reviewing or updating documentation, including LLMs. | Mandatory authorized change control and audit procedure; update only when governance changes. |
| `<project>.wiki/BACKLOG.md` | Developers and decision makers: deferred improvements, intended outcomes, evidence and disposition. | Future work only; update when items are identified, approved, deferred or validated. Does not supersede requirements or authorize implementation. |

Generate requirement and test-specification skeletons where project-specific content is not supplied. Include only actual generated foundation tests and their traceability; do not invent application tests. A test execution report template may be provided, but it must not be registered as an executed report until populated with actual evidence. Externally supplied architectural principles, clarification processes and task prompts are not automatically repository files; reference them as applicable without falsely registering them or treating task-specific instructions as universal rules.

### 3.2 User-facing README architecture

Use the following section sequence: Overview, Features, System Requirements, Installation, Configuration, Initialization, Getting Started, CLI Reference, Python API Reference, Examples, Security and Access Management, Backup and Recovery, Troubleshooting.

Tailor applicability to the selected project. Leave unimplemented applicable sections blank until validated; do not advertise planned functionality as available. Getting Started introduces the first basic workflow, while Examples demonstrates specific practical tasks. Keep development setup and internal testing instructions in DEVELOPMENT.md, with a correct relative link if needed.

### 3.3 Agent document navigation

AGENTS.md contains three sections: Document Registry, Document Reading Guidance, and Maintenance Rules. Do not duplicate the project overview, task objective, authorization rules or context initialization instructions. The registry records each actual document's relative path, purpose and authority. Reading guidance depends on the assigned task; examples include:

| Task | Relevant documents |
|---|---|
| Understand or use the product | README; applicable technical interface or operational sections if needed. |
| Requirements or architecture | README, functional and technical requirements; applicable architecture principles, conventions and testing rules. |
| Software implementation | Functional and technical requirements, coding conventions, testing governance, development guide, test specification and applicable execution reports. |
| Test design or execution | Requirements, testing governance, coding conventions, test specification, development guide and applicable execution reports. |
| Evaluate deferred improvements or prepare future work | Backlog and applicable requirements and governing documents. |
| Document creation, modification or review | Document governance, target document and applicable authoritative sources. |

Do not infer implementation authorization from this guide. Update the registry when a document is added, removed, renamed, relocated or changes purpose or authority; update reading guidance when applicability changes. Ordinary content edits do not require a registry update unless they affect those properties.

### 3.4 Document governance template

Apply the following process to every authorized document creation or modification, including changes to the governance document itself. Correctness and compliance take precedence over speed.

- Establish purpose, audience, scope and authoritative sources. Read the complete existing document, inspect available baseline/repository state and preserve unrelated content, approved decisions and uncommitted user changes. Review-only tasks do not authorize edits; do not regenerate files merely in response to review comments.
- Draft self-contained content, preserving section purpose and separating functional requirements from technical specifications. Avoid duplicated requirements and unnecessary historical commentary; distinguish planned from implemented functionality. Verify commands, filenames and references against available evidence. Modify only affected authorized documents.
- **Pass 1, accuracy and compliance:** reopen the actual written file and compare with requirements, decisions, scope, evidence and the original baseline. Check coverage, factual accuracy, preservation, authorization and cross-document consistency. Identify findings with the affected section and supporting source; correct automatically within scope, requesting input only for material decisions or additional authorization. Reopen and verify corrections.
- **Pass 2, document quality:** independently read the corrected file afresh, checking audience suitability, clarity, terminology, internal consistency, flow, section cohesion, conciseness and accurate references. Correct and verify; repeat affected Pass 1 checks when corrections change previously verified content.
- **Delivery gate:** reopen the final file and compare against the baseline. Resolve material findings before final delivery; disclose missing sources, blocked checks and unresolved limitations. Report concrete checks, findings and corrections for each pass, not merely an assertion that an audit passed. Do not claim separate reviewers, evidence or test executions that did not occur. Packaging unchanged files does not require another audit.

### 3.5 Coding conventions template

Use PEP 8, four-space indentation, descriptive snake_case Python and PostgreSQL identifiers and UPPER_CASE Python constants. Annotate function parameters and returns (including None), prefer native types, and do not introduce a runtime type-checking framework solely for annotations. Keep responsibilities focused, use explicit parameters, avoid mutable defaults and use classes only when justified. Document public functions with concise purpose, parameters, return values and error behavior; comments explain non-obvious rationale rather than restating code.

Use specific exception handling, actionable errors without secrets or raw SQL diagnostics, and the project's approved interface contracts. Only executable entry points may terminate the process. Use standard Python logging, configurable severity and stderr for diagnostics; keep stdout available for command results. Do not log credentials or sensitive application content.

Expose only approved public Python functions, explicitly declare exports with `__all__`, prefix internal functions with `_`, and use internal modules where useful. Python naming is not a security boundary. For PostgreSQL, use uppercase SQL keywords, qualified object names, explicit columns, parameterized queries, safe search paths and ordered numbered SQL migration files when migrations are introduced. If the selected application uses a database-enforced API, isolate public SQL functions from helpers and restrict execution permissions; preserve the approved policy enforcement boundary rather than duplicating business logic in wrappers or the CLI. Do not impose a specific business API or JSON envelope on all projects.

Prefer the standard library, justify third-party dependencies, pin direct and transitive versions and separate runtime from development/testing dependencies. Obtain approval for additions or upgrades under the project's change control rules. Preserve public contracts during internal refactoring.

### 3.6 Automated testing governance template

Use pytest with independently executable unit, integration and end-to-end suites. Maintain a single test specification with unique identifiers mapped to applicable requirements, acceptance criteria and actual executable tests. Include relevant positive, negative, boundary, security and failure scenarios. Introduce tests progressively within authorized scope.

Run relevant tests during development, rerun affected tests after audit corrections, and execute current and previous applicable stage tests before acceptance. Database validation uses a specific committed revision in staging. Isolate test data and credentials, use temporary filesystem locations, and establish reproducible test state automatically. Apply the additional managed PostgreSQL safety rules in Section 5 when that capability is selected.

Investigate failures using evidence; distinguish software, test and environmental defects. Correct confirmed defects and rerun relevant regression tests. After two consecutive unsuccessful fixes of the same defect, stop speculative modifications and reassess root causes before further changes. Obtain user decisions for changes outside approved scope. Never suppress or weaken tests to obtain a pass.

Retain one final execution report per validated stage (not every intermediate run). Record date, environment, actual commands, case identifiers and results, including failures, skips, blockers and tests not run with reasons. Required tests must actually pass; code inspection is not a test pass. Complete requirements/correctness and engineering quality audits, verify the tested Git checkpoint and record its identifier in the report. If tested code or configuration changes, rerun applicable tests. User acceptance and authorization to advance remain separate from technical validation.

## 4. Technical Foundation

### 4.1 Generated asset map

The following paths describe the proposed output contract, not an assertion that the generator already creates them. Include only assets relevant to the selected capability and integrate with existing generator conventions.

| Asset | Purpose | Capability |
|---|---|---|
| `.python-version`, `pyproject.toml`, `src/<package>/__init__.py` | Pinned Python version, installable package metadata and package entry boundary. | Foundation |
| `scripts/bootstrap.sh`, `requirements-bootstrap.txt`, `requirements.txt` | Repeatable setup, installation-tool pins and test/development dependency pins. | Foundation |
| `requirements-runtime.txt` | Runtime dependency pins, separate from test tools. | As needed |
| `.gitignore`, `.env.example` | Exclusions and secret-free configuration contract. | Foundation / as applicable |
| `src/<package>/_config.py` | Runtime configuration validation and connection settings where applicable. | PostgreSQL |
| `compose.yaml`, `src/<package>/_environment.py` | Shared infrastructure definition and provisioning configuration validation. | Managed PostgreSQL |
| `scripts/manage_environment.py`, `src/<package>/_provisioning.py` | Operator-facing setup/check utility and internal provisioning logic. | Managed PostgreSQL |
| `src/<package>/_test_safety.py`, `tests/conftest.py` | Shared mandatory staging verification and test harness integration. | Managed PostgreSQL |
| `tests/unit/`, `tests/integration/`, `tests/e2e/` | Independent test suites; empty directories may use placeholders if required by Git. | Foundation |
| `tests/unit/test_config.py`, `tests/unit/test_import.py` | Foundation import and applicable configuration tests. | As applicable |
| `tests/unit/test_environment.py`, `tests/unit/test_provisioning.py`, `tests/integration/test_environment_management.py` | Configuration, provisioning and real infrastructure verification. | Managed PostgreSQL |


### 4.2 Python project and dependencies

- Generate an installable package with a `src/` layout, an independent `.venv`, and a pinned Python version.
- Provide a bootstrap script that safely reruns, installs pinned dependencies and the package in editable development mode, verifies dependency integrity and runs unit tests without requiring database infrastructure.
- Separate bootstrap, runtime and development/testing dependency manifests. Pin applicable direct and transitive dependencies; prefer the standard library when suitable and justify new dependencies.
- Select compatible versions for the target platforms. Exact dependency pins alone do not guarantee byte-identical or offline reproducibility.

### 4.3 Configuration and PostgreSQL connectivity

- Provide a version-controlled, secret-free `.env.example` defining the configuration contract. Actual `.env`, credentials, virtual environments and persistent data remain outside version control.
- Validate required values, paths and conflicts before acting. Read local provisioning configuration as literal key/value data, not executable shell code.
- Use standard libpq connection settings and Psycopg 3 with its binary distribution for PostgreSQL-enabled projects. Validate installation, import, real connectivity and password-file authentication on supported platforms. Do not assume ordinary application processes automatically load `.env`.
- Keep public APIs separate from internal implementation; avoid hardcoded project names, environment paths and connection values. Require `PGDATABASE` and `PGUSER` for database operations; ordinary client host and port defaults follow libpq, while managed provisioning requires explicit target settings. Do not add an ORM merely to provide database connectivity.

### 4.4 Automated test infrastructure

Provide pytest organization under `tests/unit/`, `tests/integration/` and `tests/e2e/`. Use temporary files and test doubles for unit tests; integration tests must exercise real isolated infrastructure. Keep tests executable independently by the project operator. Provide test collection, execution and regression instructions.

## 5. Managed PostgreSQL Architecture

### 5.1 Environment isolation and persistence

Use one source repository with independent development and staging checkouts, virtual environments, local configuration and PostgreSQL instances. Staging validates a selected committed revision; source changes are made in development. Use the same application code and parameterized Compose definition in both environments, rather than adding application mode logic.

A suggested workspace layout is:

```text
<workspace>/
  develop/<project>/
  stage/<project>/
  data/<project>/
    develop/postgres/
    develop/secrets/
    stage/postgres/
    stage/secrets/
```

The workspace root and storage paths are configurable. Keep development and staging data outside disposable checkouts. Production storage is operator-defined and must remain independent of disposable components. Use pinned PostgreSQL images and bind-mounted external storage. Container replacement must preserve data, roles and environment identity. Never automatically delete persistent storage or unrelated infrastructure.

Example environment settings (illustrative, not globally reserved values):

| Setting | Development | Staging |
|---|---|---|
| Compose project | `<project>_develop` | `<project>_stage` |
| Container | `<project>-db-dev` | `<project>-db-test` |
| Host | `localhost` | `localhost` |
| Port | Operator-selected available port | Different operator-selected available port |
| Database | `<project>_dev` | `<project>_test` |
| Environment identity | `development` | `staging` |

Use separate PostgreSQL instances because database roles are cluster-wide. Staging infrastructure remains stable, while tests establish reproducible application schemas and test data.

### 5.2 Configuration and credentials

Use a common configuration contract for Compose and provisioning. Configuration must identify the environment (`development`, `staging` or `production`), Compose project, container, external storage, provisioning password file and database connection. Standard settings include `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER` and optional `PGPASSFILE`. Container names, ports and storage paths are environment-specific and configurable. Proposed managed configuration keys are `<PROJECT>_ENVIRONMENT` (a project-derived uppercase identifier), `COMPOSE_PROJECT_NAME`, `POSTGRES_CONTAINER_NAME`, `POSTGRES_DATA_DIR` and `POSTGRES_PASSWORD_FILE`, in addition to the libpq settings. Resolve paths safely; validate configuration before acting, reject storage overlap or storage inside disposable checkouts, and keep credentials outside both checkout and database storage. Bind database ports to the local interface for the local workflow. Do not hardcode an operator's workspace, superuser name or port. Use the pinned image's supported persistent storage mount (PostgreSQL 18 uses `/var/lib/postgresql` in the official image).

The operator supplies and protects two credential files:

| File | Purpose |
|---|---|
| Provisioning password file | Single-line initial PostgreSQL superuser password, supplied to the official container through `POSTGRES_PASSWORD_FILE`. |
| Client password file | libpq connection-specific credentials, supplied through `PGPASSFILE` or the default `~/.pgpass` on macOS/Linux. |

The provisioning file contains only the password (no assignment or quotes). The client password file contains `host:port:database:user:password` entries; preserve unrelated entries and escape literal colons and backslashes according to libpq rules. The operator must understand that initial server password creation and client authentication are different operations. Require permissions `0600` on macOS/Linux. Never expose password values or automatically create, change or synchronize credentials. Validate matching initial credentials before initializing new storage. For existing storage, authenticate using the current client credential; container replacement does not rotate the database password. Password rotation remains the operator's responsibility. Credential simplification, if pursued, requires a separate security design review.

### 5.3 Environment management utility

Provide a utility with two initial operations:

- `setup`: validate configuration, paths and infrastructure conflicts; prepare missing directories; report missing credentials and stop before starting containers or initializing databases; provision or start the designated PostgreSQL instance once prerequisites pass; verify readiness, authentication and identity.
- `check`: verify configuration, infrastructure, connectivity and identity without changing anything.

Both operations must be safe to rerun. Reuse valid existing resources without modification; reject conflicting resources with actionable diagnostics. Detect both active host listeners and configured Docker port mappings, including stopped containers. Never delete containers, volumes or database files automatically or alter unrelated infrastructure. Application schema initialization remains a separate privileged operation.

Expose the utility through `scripts/manage_environment.py`, using the generated virtual environment. For the proposed local macOS/Linux workflow, from the configured checkout the operator runs `.venv/bin/python scripts/manage_environment.py setup` and then `.venv/bin/python scripts/manage_environment.py check`. The utility parses the local `.env` without executing shell code; direct application clients use their process environment. Verify driver availability, credential permissions and matching initial credentials before starting a fresh database. Reject unsafe remote Docker contexts for the local provisioning workflow. Validate readiness against the actual TCP listener, not only a transient initialization server. Verify password-file authentication using SCRAM-SHA-256 and verify identity before reporting success. If provisioning is interrupted and storage exists without identity, abort rather than silently recreate or relabel it; recovery is outside initial scope.

Provide one canonical setup procedure: bootstrap; supply local configuration; run setup to prepare directories; supply any missing credential files identified by the utility; rerun setup; run read-only check. Distinguish operator responsibilities from automated activities.

### 5.4 Environment identity and test safety

Provide an independently provisioned metadata schema, e.g. `<project>_env.environment_identity` (using a valid SQL identifier derived from the project name), containing a protected singleton environment identity record. Enforce exactly one record and the allowed values `development`, `staging` and `production` in PostgreSQL. Make the record immutable after provisioning. Prevent ordinary roles from inserting, deleting or modifying the identity. PostgreSQL superusers can bypass database protections, so administrative access must also be controlled.

Create identity during first provisioning and verify it on subsequent runs. Reject existing clusters with missing, invalid, unreadable or mismatched identity; never silently relabel them. Keep identity independent of application schema resets.

Before automated database tests, setup or cleanup, a shared fail-closed guard must verify the designated Docker target, staging host, port and database, and the stored `staging` identity. Missing or unsafe configuration must fail the required database tests, not skip them. Provide no bypass or force option. Preserve the identity during resets. Controlled container recreation tests must operate only on verified staging infrastructure, preserve external storage and verify database contents, roles, identity, configuration and connectivity after replacement. Test cleanup may remove only its own authorized fixtures, never persistent storage.

### 5.5 Data architecture and responsibility boundaries

| Data | Location / source | Consumer and lifecycle |
|---|---|---|
| Versioned code, manifests, configuration template, Compose definition | Git repository | Reproducible generation, installation and provisioning; changes through controlled revisions. |
| Environment values | Local `.env` | Provisioning utility and Compose; application connection settings explicitly loaded into process environment. Operator-owned. |
| Provisioning password | Protected external file | Official PostgreSQL image on first initialization; not a password rotation mechanism. |
| Client credentials | Protected libpq password file | Management utility, application and tests; match actual role and target connection. Separate privileged setup credentials from runtime credentials. |
| Database contents and roles | External `POSTGRES_DATA_DIR` | PostgreSQL; persist across container replacement. |
| Environment identity | Independent metadata schema | Setup/check and test guard; created once, never reset with application schema. |
| Test fixtures | Versioned tests and temporary staging state | Test harness; establish known state, clean only authorized test artifacts. |
| Test execution evidence | Project engineering documentation | Reviewers; retained per validated stage, references tested revision. |

The generated environment definition is shared; the local configuration, secrets and persistent state are independent for each deployment. Do not confuse container replacement with data backup or recovery. A documented manual backup-and-restore procedure is a future local-development deliverable; production recovery objectives, retention, replication, failover and recovery automation remain to be specified and validated; do not claim persistence testing proves recovery.

## 6. Design Improvements to Include

These are proposed requirements or future extensions, not claims of implemented generator functionality:

- Provide actionable conflict messages identifying the resource and setting involved, without disclosing secrets.
- Provide meaningful progress messages during lengthy provisioning operations.
- Distinguish expected missing-credential prerequisites from genuine provisioning failures with an `[ACTION REQUIRED]` message, including required file paths and permissions. Return a nonzero exit code while provisioning is incomplete; do not weaken credential protections.
- Provide a concise verification summary showing the actual checks performed and their outcomes; keep `check` read-only.
- Keep the operator workflow ordered and minimize manual infrastructure preparation.
- Explain the difference between initial server credentials and client authentication credentials.
- Consider future environment health checks, structured health reports, recovery diagnostics and controlled recovery routines. These require separate specification and authorization; do not implement destructive recovery as part of initial provisioning.

## 7. Proposed Acceptance Criteria

Before blueprint release, demonstrate that a generated project:

- Uses the chosen project name and configuration without unrelated project names, paths, schemas, business rules or historical test results.
- Installs in a clean supported environment and runs unit tests independently of database infrastructure.
- Includes coherent user and development documentation, applicable governance, executable tests, test traceability and an accurate document registry.
- For PostgreSQL-enabled blueprints, uses external connection settings and protected credentials; validates real connectivity and driver compatibility on supported platforms.
- For managed PostgreSQL blueprints, provisions isolated environments, safely reuses valid resources, prepares directories before requesting credentials, rejects conflicts and missing credentials with actionable messages, and leaves `check` read-only.
- Demonstrates that container recreation preserves external data, roles and environment identity, and that unsafe database tests fail closed without affecting non-staging infrastructure.
- Records actual test evidence and tested revision, runs applicable regression tests, and completes both mandatory audit-and-correction passes before acceptance.

Refine these proposed criteria against the existing pyprojectgen requirements and approved blueprint scope before implementation.

## 8. Additional Capabilities to Specify Later

The following sections are intentionally blank pending further design and validation. Their presence does not authorize development.

### 8.1 Database Initialization and Migration Framework

### 8.2 PostgreSQL API and Security Patterns

### 8.3 Python API and CLI Patterns

### 8.4 End-to-End Validation and Release Practices

### 8.5 Application Containerization and Deployment

### 8.6 Audit Logging, Backup, Recovery and Production Readiness

## 9. Maintenance and Handover

Maintain this brief as a future enhancement in the pyprojectgen repository. Add reusable capabilities and acceptance criteria as they are designed and validated; preserve previously captured requirements, explicitly supersede changed decisions, and keep the later-capability sections blank until there is sufficient evidence. Do not insert names, paths, commits, business rules or test results from unrelated projects into the blueprint templates. No external project or conversation is required to understand this document.

Before implementation, inspect the current pyprojectgen repository and backlog, reconcile existing capabilities, determine supported platforms and version pins, and obtain approval for scope and acceptance criteria. Apply document governance when revising the brief. Do not assume that a proposed capability is implemented merely because it appears here.

### 9.1 Maturity of the proposed foundations

The following records the level of evidence available when defining these reusable patterns, based on reported execution results rather than an independently inspected final repository. It is not pyprojectgen test evidence or a report to copy into generated projects.

| Capability | Current evidence and remaining work |
|---|---|
| Project foundation and governance | A comparable foundation was validated on macOS/Python 3.12.10, including clean installation and 11 passing tests; foundation accepted. |
| PostgreSQL connectivity foundation | Native Psycopg binary installation/import and 60 passing unit tests demonstrated on macOS. |
| Managed environment foundation | 156 passing unit tests reported independently in development and staging on macOS/Python 3.12.10; initial provisioning and read-only checks succeeded in both environments, and development setup rerun succeeded. |
| Staging safety and persistence | Seven infrastructure integration cases reported passed in staging, including safe setup rerun, four identity mutation rejection cases, ordinary-role access protection, and controlled container recreation preserving database contents, roles, identity and unrelated infrastructure. Based on reported results; full per-case execution output is unavailable. |
| Linux application deployment, database application initialization and later capabilities | Not yet validated; do not infer Linux deployment success from macOS results. |

Versions used in the demonstrated foundation: Python 3.12.10, PostgreSQL image `postgres:18.7-bookworm`, and `psycopg[binary]==3.3.9`. These are historical compatibility evidence, not mandatory permanent generator pins. Select and validate versions against the future supported-platform matrix. No pyprojectgen blueprint generation or acceptance tests have been executed for this brief.
