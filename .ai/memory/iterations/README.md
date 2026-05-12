# Iterations Log

Эта директория отслеживает итерации разработки и прогресс спринтов для QA фреймворка.

## Назначение

Логи итераций предоставляют:
- Хронологическую запись изменений
- Sprint goals и outcomes
- Technical debt tracking
- Lessons learned
- Decision history с контекстом

## Соглашение по именованию файлов

Используй ISO date format для документов итераций:
```
YYYY-MM-DD_iteration-N_description.md
```

Пример: `2026-05-12_iteration-1_framework-setup.md`

## Шаблон структуры

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

> 💡 **Совет**: Просматривай предыдущие итерации перед началом новой работы для сохранения непрерывности и избежания повторения ошибок.
