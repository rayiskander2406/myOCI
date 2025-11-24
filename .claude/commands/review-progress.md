---
name: review-progress
description: Analyze COMPLETED.md and TODO.md to assess release progress and update plans
---

You are conducting a comprehensive progress review for the release. Analyze `.claude/COMPLETED.md`, `.claude/TODO.md`, and `.claude/PLANNING.md` to provide insights and recommendations.

## Review Objectives

1. **Measure Progress** - quantify what's done vs what remains
2. **Identify Patterns** - learnings from completed work
3. **Spot Risks** - blockers, delays, or quality concerns
4. **Adjust Plans** - update estimates and priorities based on reality
5. **Maintain Momentum** - clear next actions and decision points

## Analysis Framework

### Velocity Analysis
- **Tasks completed** in last review period
- **Average time per task** vs original estimates
- **Estimation accuracy** - where were we wrong?
- **Trend analysis** - speeding up or slowing down?

### Quality Metrics
- **Test coverage** changes
- **Technical debt** created vs resolved
- **Bugs introduced** during development
- **Rework required** - tasks that needed redoing

### Risk Assessment
- **Blocked tasks** and why
- **Dependency delays** affecting timeline
- **Scope creep** - new tasks added vs completed
- **Critical path items** still pending

### Learning Extraction
- **Effective patterns** that worked well
- **Pain points** encountered repeatedly
- **Estimation blind spots** - what we underestimated
- **Process improvements** needed

## Review Output Format

Create a comprehensive review in `.claude/REVIEW-[DATE].md`:

```markdown
# Release Progress Review - [Date]

## Executive Summary
**Release Version**: [X.Y.Z]
**Review Period**: [Date range]
**Overall Status**: [On Track / At Risk / Behind Schedule]
**Recommended Action**: [Proceed / Adjust Scope / Delay Release]

### Key Metrics
- **Tasks Completed**: X/Y (Z%)
- **High Priority Remaining**: X tasks
- **Blockers**: X active blockers
- **Velocity**: X tasks/day (vs estimated Y tasks/day)
- **Estimated Completion**: [Date based on current velocity]

---

## Progress Summary

### Completed This Period
- [Major accomplishments]
- [Features finished]
- [Bugs fixed]
- [Infrastructure improvements]

### Tasks Remaining
- **High Priority**: X tasks ([estimated days] remaining)
- **Medium Priority**: X tasks ([estimated days] remaining)
- **Low Priority**: X tasks ([estimated days] remaining)

### Deferred/Descoped
- [Tasks removed from this release with justification]

---

## Velocity & Estimation Analysis

### Task Completion Rate
```
Week 1: X tasks completed
Week 2: Y tasks completed
Week 3: Z tasks completed
Average: A tasks/week
```

### Estimation Accuracy
- **Underestimated**: [Categories of work we underestimated]
  - [Type]: [Factor we were off by]
- **Overestimated**: [Categories we overestimated]
  - [Type]: [Factor we were off by]
- **Accurate**: [What we estimated well]

### Velocity Trend
[Increasing / Stable / Decreasing]
**Analysis**: [Why velocity is changing]

---

## Risk & Blocker Analysis

### Active Blockers
1. **[Blocker Title]**
   - **Impact**: [High/Medium/Low]
   - **Affects**: [Which tasks/features]
   - **Root Cause**: [Why blocked]
   - **Mitigation**: [Plan to unblock]
   - **Owner**: [Who's resolving]

### Risk Register
| Risk | Probability | Impact | Mitigation Status |
|------|-------------|--------|-------------------|
| [Risk] | [H/M/L] | [H/M/L] | [Status] |

### Critical Path Analysis
**Current critical path**: [Sequence of tasks that determine release date]
**Bottleneck**: [Where things are slowest]
**Risk to timeline**: [Days of potential delay]

---

## Quality Assessment

### Test Coverage
- **Current**: X%
- **Target**: Y%
- **Gap**: [Analysis of uncovered areas]

### Technical Debt
- **Created This Period**: [New debt with justification]
- **Resolved This Period**: [Debt paid down]
- **Net Change**: [Better/Worse/Neutral]

### Code Quality Trends
- **Rework Required**: X tasks needed changes after "completion"
- **Bug Introduction Rate**: Y bugs per feature
- **Review Comments**: [Patterns in code review feedback]

### Integration Issues
- [Any problems discovered during integration]
- [Compatibility issues found]
- [Performance regressions identified]

---

## Learning & Insights

### What Worked Well
1. [Practice/Pattern that proved effective]
   - **Example**: [Specific instance]
   - **Recommendation**: [How to repeat]

### What Didn't Work
1. [Practice/Pattern that caused problems]
   - **Example**: [Specific instance]
   - **Recommendation**: [How to improve]

### Surprises & Discoveries
- [Unexpected challenges encountered]
- [Technologies/approaches that exceeded expectations]
- [Assumptions that proved wrong]

### Process Improvements Identified
1. [Improvement opportunity]
   - **Current Problem**: [What's not working]
   - **Proposed Solution**: [How to fix]
   - **Expected Benefit**: [What improves]

---

## Scope & Priority Adjustments

### Recommended Scope Changes
**Add to Release**:
- [Task]: [Why it became critical]

**Remove from Release**:
- [Task]: [Why it can wait]

**Priority Adjustments**:
- [Task]: [Old Priority] → [New Priority] because [reason]

### Rationale
[Explanation of why scope/priority changes are needed]

---

## Updated Timeline Projection

### Based on Current Velocity
- **Optimistic**: [Date if everything goes well]
- **Realistic**: [Date based on average velocity]
- **Pessimistic**: [Date if we hit more blockers]

### Confidence Level
[High / Medium / Low] confidence in timeline
**Reasoning**: [What factors affect confidence]

### Release Date Recommendation
**Target Date**: [Date]
**Buffer**: [Days of contingency]
**Final Recommended Date**: [Date]

---

## Next Steps & Decisions Needed

### Immediate Actions (Next 1-3 Days)
1. [Action item with owner]
2. [Action item with owner]
3. [Action item with owner]

### Decisions Required
1. **[Decision Topic]**
   - **Options**: [A, B, C]
   - **Recommendation**: [Which option and why]
   - **Deadline**: [When decision is needed]
   - **Decision Maker**: [Who decides]

### Focus Areas for Next Period
1. [Priority focus area with reasoning]
2. [Priority focus area with reasoning]
3. [Priority focus area with reasoning]

---

## Health Indicators

### Team Health
- **Morale**: [Assessment based on progress, blockers, quality]
- **Pace**: [Sustainable / Unsustainable]
- **Clarity**: [Team clear on goals and priorities]

### Technical Health
- **Architecture**: [Following plan / Drifting]
- **Quality**: [Improving / Stable / Degrading]
- **Maintainability**: [Trend assessment]

### Process Health
- **Planning Accuracy**: [How well plans match reality]
- **Workflow Efficiency**: [Smooth / Some friction / Major issues]
- **Communication**: [Clear / Adequate / Problematic]

---

## Appendix: Detailed Task Breakdown

### High Priority Tasks Detail
[Detailed breakdown of remaining high priority work]

### Dependencies Map
[Visual or text representation of task dependencies]

### Resource Allocation
[Where effort is being spent - useful for identifying imbalances]
```

## Execution Guidelines

1. **Read all three files thoroughly**:
   - PLANNING.md for original intent
   - TODO.md for current state
   - COMPLETED.md for actual progress

2. **Be data-driven**:
   - Count tasks, measure time, track trends
   - Don't rely on feelings, use actual metrics
   - Look for patterns in the data

3. **Be honest about problems**:
   - Call out blockers clearly
   - Admit when estimates were wrong
   - Identify process issues

4. **Be constructive**:
   - Don't just identify problems, propose solutions
   - Focus on what can be controlled
   - Provide clear next actions

5. **Think strategically**:
   - Connect tactical progress to strategic goals
   - Consider trade-offs (scope vs time vs quality)
   - Make recommendations, don't just report

6. **Update plans based on learnings**:
   - Adjust TODO.md if priorities changed
   - Update PLANNING.md if scope changed
   - Document decisions for future reference

## Post-Review Actions

After generating the review:

1. **Update TODO.md** with any priority changes
2. **Update PLANNING.md** if scope changed significantly
3. **Archive review** in `.claude/reviews/` directory
4. **Commit all changes** to git
5. **Share summary** with stakeholders if needed

## Review Triggers

Run this review when:
- **Time-based**: Weekly or bi-weekly for active releases
- **Milestone-based**: After completing major features
- **Concern-based**: When velocity drops or blockers accumulate
- **Decision-based**: Before making scope or timeline changes

## Quality Checks

A good review should:
- [ ] Provide clear progress metrics
- [ ] Identify concrete next actions
- [ ] Surface risks with mitigation plans
- [ ] Extract learnings from completed work
- [ ] Give honest timeline projections
- [ ] Recommend specific decisions
- [ ] Be actionable, not just informational

After completing the review, provide a verbal summary highlighting:
- Overall release health (on track / at risk / behind)
- Top 3 risks or blockers
- Recommended timeline adjustment if any
- Most critical next actions
- Any urgent decisions needed
