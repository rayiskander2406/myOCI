---
name: plan-release
description: Analyze codebase and create strategic release plan in .claude/PLANNING.md
---

You are analyzing the project for release planning. Create a comprehensive strategic plan in `.claude/PLANNING.md`.

## Analysis Steps

1. **Review Recent Changes**
   - Examine git log for commits since last release/tag
   - Identify patterns: bug fixes, features, breaking changes, refactors
   - Note any migration or upgrade requirements

2. **Assess Current State**
   - Check for open issues or TODOs in code
   - Review dependency versions and compatibility
   - Identify technical debt that should block/not block release
   - Check test coverage and CI/CD status

3. **Determine Release Scope**
   - Classify changes: MAJOR (breaking), MINOR (features), PATCH (fixes)
   - Identify what MUST be in this release vs what can wait
   - Consider versioning strategy (semantic versioning)
   - Note any deprecation warnings needed

4. **Risk Assessment**
   - Database migrations or schema changes
   - API contract changes
   - Dependency updates that might cause issues
   - Deployment complexity or downtime requirements

5. **Release Strategy**
   - Recommended version number with justification
   - Deployment approach (blue-green, rolling, etc.)
   - Rollback plan if issues arise
   - Communication plan (changelog, docs, notifications)

## Output Format for .claude/PLANNING.md

Structure your plan as follows:

```markdown
# Release Planning - [Date]

## Release Overview
- **Proposed Version**: X.Y.Z
- **Release Type**: [Major/Minor/Patch]
- **Target Date**: [Estimated]
- **Risk Level**: [Low/Medium/High]

## Changes Since Last Release
### Breaking Changes
- [List with impact analysis]

### New Features
- [List with completion status]

### Bug Fixes
- [List with severity]

### Dependencies
- [Updates needed, compatibility concerns]

## Release Requirements
### Must Have (Blockers)
- [ ] [Item with justification]

### Should Have (Important)
- [ ] [Item with justification]

### Nice to Have (Optional)
- [ ] [Item with justification]

## Risk Analysis
### High Risk Items
- [Item]: [Mitigation strategy]

### Medium Risk Items
- [Item]: [Mitigation strategy]

### Dependencies on External Systems
- [System]: [Compatibility/coordination needs]

## Deployment Strategy
### Pre-Deployment
- [ ] [Checklist items]

### Deployment Steps
1. [Ordered steps]

### Post-Deployment
- [ ] [Verification steps]

### Rollback Plan
- [Clear rollback procedure if needed]

## Documentation & Communication
### Changelog Entries
- [Key items for user-facing changelog]

### Documentation Updates Needed
- [Docs that need updating]

### Stakeholder Communication
- [Who needs to know what, when]

## Open Questions
- [Decisions still needed]
- [Clarifications required]

## Next Steps
[What should happen after this planning phase]
```

## Execution Guidelines

- Be thorough but concise
- Flag uncertainties clearly - don't guess
- If you need more information, list what's needed in Open Questions
- Focus on strategic decisions, not implementation details
- Commit PLANNING.md to git when complete
- Include reasoning for version number recommendation
- Consider backwards compatibility seriously

After writing PLANNING.md, provide a brief summary of:
- Recommended version number
- Key risks identified
- Critical blockers if any
- Whether the project is ready for release planning to proceed
