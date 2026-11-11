# Project-specific guidance

## ADS integration checks

- Keep live ADS integration checks separate from unit tests. Run them manually
  when needed; routine tests must not require network access or an ADS or OPENAI token.

## Dependencies

- Prefer the Python standard library when it provides a clear, maintainable
  solution. Add third-party packages only when they offer a meaningful benefit, e.g. considerably simplify code.

## Working protocol

- Do not create, edit, or delete files, or execute commands, unless I have
  explicitly instructed or authorized you to do so. If the task is ambiguous,
  ask before acting.
- Inspect relevant files and the repository state before changing anything.
  Preserve existing work; never discard or overwrite it without my permission.

## Tests and Git checkpoints

- Run appropriate tests and report the results before recommending a checkpoint.
- After meaningful changes, summarize the diff and explain key decisions.
- Ask before committing. Never commit without my explicit permission.
