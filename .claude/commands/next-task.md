---
name: next-task
description: Execute 1-2 tasks from TODO.md, move completed work to COMPLETED.md
---

You are executing tasks from the release plan. Work on the next 1-2 tasks from `.claude/TODO.md` in small, focused batches.

## Task Selection Strategy

1. **Read TODO.md completely** to understand context
2. **Identify next actionable tasks**:
   - Check "Current Focus" section first
   - Select tasks with no unmet dependencies
   - Prefer high-priority tasks
   - Consider effort estimation (mix small and medium)
3. **Limit to 1-2 tasks maximum** to maintain focus and quality
4. **Verify you have context** for the selected tasks

## Execution Workflow

### Before Starting
1. **Confirm task selection** with user if ambiguous
2. **Check dependencies** are actually complete
3. **Review acceptance criteria** to understand success
4. **Note the current state** of relevant files

### During Execution
1. **Follow acceptance criteria exactly** - they define success
2. **Implement incrementally**:
   - Write interface/types first
   - Implement core logic
   - Add error handling
   - Write tests
   - Update documentation
3. **Test as you go** - verify each criterion as completed
4. **Stay focused** - if you discover new work, note it for TODO.md, don't expand scope
5. **Commit frequently** - atomic commits for each logical change

### After Completion
1. **Verify all acceptance criteria met** - be honest
2. **Run relevant tests** - ensure nothing broke
3. **Update documentation** if required by task
4. **Move task to COMPLETED.md** with completion notes
5. **Update TODO.md** - remove completed task, update "Current Focus"

## Completion Notes Format

When moving tasks to COMPLETED.md, include:

```markdown
## [Category] Task Title - COMPLETED [Date]

**Time Spent**: [Actual time]
**Original Estimate**: [From TODO]

### What Was Done
- [Specific changes made]
- [Files modified/created]
- [Tests added]

### Acceptance Criteria Status
- [x] [Criterion 1] - [How verified]
- [x] [Criterion 2] - [How verified]
- [x] [Criterion 3] - [How verified]

### Learnings & Notes
- [Unexpected challenges encountered]
- [Decisions made during implementation]
- [Technical debt created/resolved]
- [Performance considerations]

### Follow-up Items
- [New tasks discovered, add to TODO.md]
- [Technical debt to address later]
- [Questions for review]

### Git Commits
- [commit hash]: [commit message]
- [commit hash]: [commit message]

---
```

## Quality Standards

### Code Quality
- Follow existing project conventions
- Add comments for non-obvious logic
- Handle errors appropriately
- Consider edge cases
- Maintain or improve test coverage

### Testing Requirements
- Unit tests for new functions/methods
- Integration tests for feature completion
- Manual testing for UI changes
- Verify existing tests still pass

### Documentation Requirements
- Update inline code comments
- Update README if behavior changes
- Update API docs if interfaces change
- Add changelog entry if user-facing

## Handling Problems

### If Dependencies Are Missing
- Stop and note the blocker
- Update TODO.md with the missing dependency
- Suggest working on the dependency first
- Don't proceed with incomplete context

### If Task Is Too Large
- Stop after discovering scope
- Break into smaller tasks in TODO.md
- Complete only the first subtask
- Leave clear notes about what remains

### If Requirements Are Unclear
- Stop and document the ambiguity
- Add clarifying questions to TODO.md
- Suggest consulting PLANNING.md
- Don't guess at requirements

### If Tests Fail
- Don't move to COMPLETED.md
- Document the failure
- Either fix or mark task as blocked
- Update TODO.md with blocker status

## .claude/TODO.md Update Pattern

After completing tasks, update TODO.md:

1. **Remove completed tasks** from their priority section
2. **Update "Current Focus"** with next 1-3 tasks
3. **Add any discovered tasks** in appropriate priority section
4. **Update task statistics**
5. **Note any blockers** discovered

## .claude/COMPLETED.md Append Pattern

Append completed tasks to COMPLETED.md in chronological order (newest first):

```markdown
# COMPLETED - Release [Version]

## [Latest completion date]

[Task completion entry using format above]

[Task completion entry using format above]

## [Earlier completion date]

[Older task entries]
```

## Execution Guidelines

1. **Work in small batches** - better to complete 1 task well than 2 partially
2. **Commit to git frequently** - after each logical change
3. **Be thorough** - follow acceptance criteria exactly
4. **Be honest** - if something doesn't work, document it
5. **Learn and document** - capture insights for future work
6. **Maintain quality** - don't cut corners to move faster
7. **Update both files** - TODO.md and COMPLETED.md stay in sync

## Success Metrics

A successful execution means:
- All acceptance criteria met and verified
- Tests passing
- Code committed to git
- Documentation updated
- COMPLETED.md has thorough notes
- TODO.md accurately reflects remaining work
- No broken functionality introduced

After completing tasks, provide a summary:
- What was completed
- Time spent vs estimated
- Any blockers or issues discovered
- Recommended next tasks
- Overall progress percentage toward release
