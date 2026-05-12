# Design Memory

This directory stores UI/UX decisions and design system documentation for the QA framework.

## Purpose

Design memory documents contain:
- Component library specifications
- Design tokens (colors, typography, spacing)
- Responsive breakpoints
- Accessibility requirements (WCAG level)
- Interaction patterns and animations
- Visual regression testing baselines

## Files to Add

When starting a new project, create documents here describing:
1. **Design System** - Link to Figma/Sketch libraries
2. **Component Catalog** - Reusable UI components with states
3. **Responsive Rules** - Breakpoints and layout behavior
4. **Accessibility Standards** - Required WCAG compliance level

## Example Structure

```markdown
# [Project Name] Design Context

## Design System
- **Figma Library**: [Link]
- **Version**: 1.0.0

## Design Tokens
| Token | Value | Usage |
|-------|-------|-------|
| `--color-primary` | #0066CC | Primary actions |
| `--spacing-md` | 16px | Standard padding |

## Components
- Button (default, hover, active, disabled, loading)
- Input (default, focus, error, success)
- Modal (header, body, footer, overlay)

## Responsive Breakpoints
- Mobile: 320px - 767px
- Tablet: 768px - 1023px
- Desktop: 1024px+

## Accessibility
- **Target**: WCAG 2.1 AA
- **Focus indicators**: Visible on all interactive elements
- **Color contrast**: Minimum 4.5:1 for text
```

---

> 💡 **Tip**: Use this documentation to build accurate Page Object models and visual regression tests.
