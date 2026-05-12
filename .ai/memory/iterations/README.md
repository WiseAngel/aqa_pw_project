# Iterations Log

This directory tracks development iterations and sprint progress for the QA framework.

## Purpose

Iteration logs provide:
- Chronological record of changes
- Sprint goals and outcomes
- Technical debt tracking
- Lessons learned
- Decision history with context

## File Naming Convention

Use ISO date format for iteration documents:
```
YYYY-MM-DD_iteration-N_description.md
```

Example: `2026-05-12_iteration-1_framework-setup.md`

## Template Structure

```markdown
# Iteration N - [Date]

## Goals
- [ ] Goal 1
- [ ] Goal 2

## Completed
- ✅ Task 1
- ✅ Task 2

## Blocked/Pending
- ⏸️ Task awaiting review
- ❓ Unclear requirement

## Decisions Made
| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| [Choice] | [Why] | [Other options] |

## Metrics
| Metric | Before | After | Target |
|--------|--------|-------|--------|
| Test count | 0 | 15 | 50 |
| Execution time | - | 3 min | <10 min |

## Retrospective
**What went well:**
- 

**What could improve:**
- 

**Action items:**
- [ ] 
```

---

> 💡 **Tip**: Review previous iterations before starting new work to maintain continuity and avoid repeating mistakes.
