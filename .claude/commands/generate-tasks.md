---
name: generate-tasks
description: Convert PLANNING.md strategic plan into actionable tasks in TODO.md
---

You are converting strategic release plans into concrete, actionable tasks. Read `.claude/PLANNING.md` and generate detailed tasks in `.claude/TODO.md`.

## Task Generation Principles

1. **Small Batch Size**: Each task should be completable in one focused session (15-45 minutes)
2. **Clear Success Criteria**: Each task must have obvious "done" conditions
3. **Minimal Dependencies**: Tasks should be as independent as possible
4. **Ordered Intelligently**: Dependencies come before dependents
5. **Specific and Testable**: No vague tasks like "improve code quality"

## Task Breakdown Strategy

### Code Changes
- Break large features into: interface definition → implementation → tests → integration
- Separate file creation from file modification
- Isolate risky changes (migrations, breaking changes) as dedicated tasks

### Documentation
- Separate writing from reviewing
- Break by document type: API docs, user guides, changelog, upgrade guides

### Testing & Validation
- Unit tests separate from integration tests
- Performance testing as distinct tasks
- Manual testing checklists separate from automated tests

### Deployment Preparation
- Configuration changes separate from code changes
- Migration scripts separate from application code
- Rollback procedures documented as separate task

## Task Format for .claude/TODO.md

Each task should follow this structure:

```markdown
## [Category] Task Title

**Priority**: [High/Medium/Low]
**Estimated Effort**: [Small/Medium/Large]
**Dependencies**: [Other task IDs or "None"]
**Risk Level**: [Low/Medium/High]

### Context
[Why this task matters, where it fits in the release]

### Acceptance Criteria
- [ ] [Specific, testable criterion]
- [ ] [Specific, testable criterion]
- [ ] [Specific, testable criterion]

### Implementation Notes
- [Key technical considerations]
- [Potential gotchas]
- [Files likely to change]

### Testing Requirements
- [How to verify this works]
- [Edge cases to consider]

### Definition of Done
- [ ] Code written and tested
- [ ] Tests passing
- [ ] Documentation updated
- [ ] Committed to git
- [ ] [Any other completion criteria]

---
```

## Task Categories

Use these categories to organize tasks:

- **[BLOCKER]** - Must complete before release
- **[FEATURE]** - New functionality
- **[BUGFIX]** - Fixing issues
- **[REFACTOR]** - Code improvement without behavior change
- **[TEST]** - Testing infrastructure or test cases
- **[DOCS]** - Documentation updates
- **[DEPLOY]** - Deployment preparation
- **[DEPS]** - Dependency updates

## Output Structure for .claude/TODO.md

```markdown
# TODO - Release [Version] - [Date]

## Overview
[Brief summary of what these tasks accomplish]
[Link to PLANNING.md for strategic context]

## Current Focus
[The 1-3 tasks that should be worked on next]

---

## High Priority Tasks

[Tasks from PLANNING.md "Must Have" section]

---

## Medium Priority Tasks

[Tasks from PLANNING.md "Should Have" section]

---

## Low Priority Tasks

[Tasks from PLANNING.md "Nice to Have" section]

---

## Deferred Tasks

[Tasks that won't make this release but should be tracked]

---

## Task Statistics
- Total Tasks: X
- High Priority: X
- Medium Priority: X
- Low Priority: X
- Estimated Total Effort: [Based on task sizes]
```

## Execution Guidelines

1. **Read PLANNING.md thoroughly** - understand the full context
2. **Extract all requirements** - don't miss anything from the plan
3. **Break down systematically** - work through each section of PLANNING.md
4. **Order by dependencies** - database migrations before code that uses them
5. **Flag uncertainties** - if planning is incomplete, note what's missing
6. **Be realistic** - don't create tasks for things that aren't actually needed
7. **Include rollback tasks** - if risky changes need rollback preparation
8. **Commit TODO.md to git** when complete

## Quality Checks Before Completing

- [ ] Every "Must Have" from PLANNING.md has corresponding tasks
- [ ] Each task has clear acceptance criteria
- [ ] Dependencies are correctly identified
- [ ] No task is too large (can split further if needed)
- [ ] High-risk items have testing tasks
- [ ] Documentation tasks exist for user-facing changes
- [ ] Deploy preparation tasks are included

After generating TODO.md, provide a summary:
- Total number of tasks created
- Breakdown by priority
- Estimated timeline if working on 2-3 tasks per day
- Any gaps or questions that need clarification
