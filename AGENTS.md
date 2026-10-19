# Coding guidance

Prefer the simplest, smallest implementation that fully satisfies the stated requirements.

- Avoid unnecessary abstractions, helper functions, classes, dependencies, configuration, and indirection.
- Don't add features, defensive checks, or generality that the requirements don't justify.
- Reuse existing functionality and follow the project's established conventions rather than introducing new patterns.
- Preserve correctness, readability, and required error handling; do not sacrifice these merely to reduce line count.
- Before implementing, consider whether a simpler solution would work.
- If a more complex solution seems necessary, explain why.
- Keep live ADS integration checks separate from unit tests; run them manually when needed, without making routine tests depend on network access or an ADS token.

## Working protocol

Do not create, edit, or delete files, or execute commands, unless explicitly instructed or given permission by me. When a task is ambiguous, ask before taking action. You may inspect files and discuss ideas, analyse code, and propose plans without modifying the project or executing commands.

## Communication style

Be concise and direct. Prefer short explanations and focused answers over lengthy descriptions. Include only the detail needed to explain the reasoning, clarify important trade-offs, or support a decision. Avoid repetition, unnecessary summaries, and unsolicited suggestions. Expand when I ask for more detail or when complexity genuinely requires it.

## Dependencies

Prefer Python's standard library over external dependencies when it provides a clear, maintainable solution. Introduce third-party packages only when they offer a meaningful benefit in functionality, simplicity, reliability, or performance. Avoid dependencies for trivial tasks that can be handled cleanly with built-in modules.

## Change review and Git checkpoints

- After completing a meaningful milestone, summarise the changes and explain the key design decisions.
- Help me review the diff, highlighting the most important changes and anything I should understand before accepting them.
- Run appropriate tests and report their results before recommending a checkpoint.
- Ask whether I want to commit the changes. Do not commit without my explicit permission.
- Never discard or overwrite existing work without my explicit permission.