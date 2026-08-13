# Conventions

These will be enforced by tooling starting at milestone M0.4 (linting/formatting).
Documented here now so they're consistent from the first real commit onward.

## Commits

- One logical change per commit.
- Message format: short imperative summary, e.g. `Add user registration endpoint`.

## Branches

- `main` is always in a working state.
- Feature work happens on short-lived branches, merged back into `main`.

## Code style

- **Backend (Python):** formatted with Black, linted with Ruff.
- **Frontend (TypeScript):** formatted with Prettier, linted with oxlint.
