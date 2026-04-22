# Backend Guidelines

## Purpose

This file standardizes how new backend modules should be added in `backend/`.

Goal:
- keep same structure for every feature
- keep business logic out of route handlers
- keep DB access isolated in repositories
- keep models, DTOs, and response schemas predictable

Use this file whenever adding new feature like `policy_management`, `approval`, `retrieval`, `evaluation`, or future multi-tenant support.

---

## Standard Folder Layout

For each feature `<feature_name>` create matching folders:

```text
backend/
  api/
    <feature_name>/
      __init__.py
      routes.py
      schemas.py
  models/
    <feature_name>/
      __init__.py
      <entity_1>.py
      <entity_2>.py
  repositories/
    <feature_name>/
      __init__.py
      <entity_1>_repository.py
      <entity_2>_repository.py
  services/
    <feature_name>/
      __init__.py
      commands.py
      <feature_name>_service.py
```

Keep root package exports:
- `backend/models/__init__.py`
- `backend/repositories/__init__.py`
- `backend/services/<feature_name>/__init__.py`

Reason:
- internal structure stays feature-grouped
- imports stay short

---

## Responsibility Split

### Model

Put only persistence shape here.

Allowed:
- table name
- columns
- relationships
- constraints
- enum definitions
- default timestamps

Do not put:
- HTTP errors
- request validation
- orchestration logic
- cross-entity workflows

### Repository

Repository owns DB reads and writes for entity or aggregate support.

Allowed:
- `create`
- `get_by_id`
- list/query methods
- aggregate helpers like `next_version_number`
- SQLAlchemy query logic

Do not put:
- FastAPI `HTTPException`
- route/request parsing
- business workflow across multiple repositories unless query-only helper

### Service

Service owns use-case orchestration.

Allowed:
- call multiple repositories
- apply business rules
- enforce state transitions
- commit transaction
- raise domain/API errors when rule violated

Do not put:
- raw SQLAlchemy query building if repository can own it
- request/response schema definitions

### API Route

Route layer must stay thin.

Route should:
- parse request schema
- build command DTO
- call service
- map service result into response schema

Route should not:
- talk directly to ORM model
- contain business logic
- duplicate validation already in command/schema

---

## Naming Rules

### Feature names

Use snake_case feature folders:
- `policy_management`
- `policy_retrieval`
- `approval_workflow`

### Model classes

Use singular PascalCase:
- `Policy`
- `PolicyVersion`
- `ApprovalRequest`

### Repository classes

Pattern:
- `<Entity>NameRepository`

Examples:
- `PolicyRepository`
- `PolicyVersionRepository`

### Service classes

Pattern:
- `<FeatureName>Service`

Examples:
- `PolicyManagementService`
- `ApprovalWorkflowService`

### Command DTOs

Pattern:
- `<Action><EntityOrFeature>Command`

Examples:
- `CreatePolicyCommand`
- `PublishPolicyCommand`
- `ApproveVersionCommand`

### API schemas

Pattern:
- `<Action>Request`
- `<Action>Response`
- `<Entity>Data`

Examples:
- `CreatePolicyRequest`
- `PublishPolicyResponse`
- `PolicyVersionData`

---

## Import Rules

Prefer importing through package exports when possible:

```python
from backend.models import Policy, PolicyVersion
from backend.repositories import PolicyRepository, PolicyVersionRepository
```

Feature-local imports are fine when needed, but keep import style consistent in same module.

Avoid deep mixed imports everywhere. Root exports exist to keep service code clean.

---

## DB Model Rules

### General

- one file per main entity
- explicit `__tablename__`
- explicit constraints for uniqueness
- use `timezone=True` for timestamps
- use typed `Mapped[...]`
- use `nullable=False` unless field truly optional

### IDs

- use integer primary key for now
- keep naming as `id`
- foreign keys must use `<entity>_id`

### Timestamps

- use UTC only
- define helper like `utc_now()`
- avoid naive `datetime.now()`

### Status fields

- use enum when state machine matters
- enum values should be stable string values used by API

### Constraints

If business rule depends on uniqueness, encode in DB too.

Example:
- `UniqueConstraint("policy_id", "version", name="uq_policy_version")`

---

## Repository Rules

Every repository should:
- take `Session` in constructor
- never create its own DB session
- call `flush()` after create when caller needs generated IDs
- return model objects, not response schemas

Commit rule:
- repository should not call `commit()`
- service owns `commit()`
- if needed later, service also owns `rollback()`

Good pattern:

```python
class PolicyRepository:
    def __init__(self, session: Session) -> None:
        self.session = session
```

---

## Service Rules

Service is source of truth for use-case behavior.

Each public service method should:
- accept command DTO
- validate entity existence
- enforce state/business rules
- coordinate repository calls
- commit once per successful use case
- return plain Python dict or typed result object

Error rules:
- `404` for missing entity
- `409` for invalid state transition
- `422` for invalid payload shape should stay in request schema validation

Versioning rule:
- if immutable versions exist, service must allocate next version using all rows that matter
- never assume "latest published" equals "latest version"

---

## API Rules

### Route file

Each feature route file should contain:
- router
- dependency builder for service
- endpoints only

### HTTP method choice

Use:
- `POST` for create or action
- `PUT` for full draft/content update
- `GET` for reads

### Response shape

- always return explicit response schema
- never return raw SQLAlchemy model directly
- nested response objects are fine when aggregate data returned

### Endpoint naming

Prefer noun-based endpoints:
- `POST /policies`
- `PUT /policies/{id}/draft`
- `POST /policies/{id}/publish`
- `GET /policies/active`

---

## Command DTO Rules

Put command DTOs in `services/<feature>/commands.py`.

Use Pydantic for:
- input validation
- trimmed strings
- min/max length checks

Commands represent use-case input, not HTTP transport details.

Good:
- `CreatePolicyCommand(title, content)`

Avoid:
- passing raw request object into service

---

## Transaction Rules

Current standard:
- one request = one service call = one commit

If exception happens before commit:
- request should fail
- session should not partially persist business flow

If later logic becomes more complex:
- add explicit `rollback()` in error paths
- move common transaction handling into shared helper if repeated

---

## Testing Rules

For every new feature, test at 3 levels when possible.

### 1. Repository tests

Test:
- entity creation
- query filters
- ordering
- unique constraints

### 2. Service tests

Test:
- happy path
- missing entity
- invalid state transition
- version increments

### 3. API tests

Test:
- request validation
- endpoint status codes
- response payload shape
- main business flow end-to-end

Minimum manual smoke flow for new feature:
1. create entity
2. update or transition state
3. fetch read model
4. verify DB rows if stateful feature

---

## New Feature Checklist

When adding new backend requirement, do this:

1. Create feature folders under `api`, `models`, `repositories`, `services`
2. Add entity models with constraints
3. Export new models in `backend/models/__init__.py`
4. Add repositories and export in `backend/repositories/__init__.py`
5. Add command DTOs
6. Add service with all use-case methods
7. Add request/response schemas
8. Add routes and register router in `backend/main.py`
9. Run syntax check
10. Run manual smoke test against local API

---

## Current Project Conventions

Based on current backend:

- framework: FastAPI
- ORM: SQLAlchemy 2
- driver: `psycopg`
- DB session source: `backend/dependencies.py`
- app startup table creation: `backend/main.py`
- DB config: `backend/db.py`

Until migration tool added:
- schema changes require table recreation or manual migration
- for serious evolution, add Alembic before more features land

---

## Anti-Patterns

Do not do these:

- query DB directly inside route
- commit inside repository
- return ORM model directly from API
- place business workflow in model class
- mix request schema and command DTO into one object when service should stay transport-agnostic
- use copy-paste folder names that do not match feature name
- add unrelated feature logic into existing service because it is "close enough"

---

## Future Extensions

These guidelines assume current Iter 1 single-tenant setup.

When multi-tenant support arrives:
- add `company_id` at model boundary
- make repository queries tenant-scoped by default
- include tenant context in command DTO or service dependency
- add DB indexes including tenant key

Do not bolt tenant filtering only at route layer.

