# Business Memory

This directory stores business-related decisions and context for the QA framework.

## Purpose

Business memory documents contain:
- Target application domain and niche
- User personas and their workflows
- Key business metrics and KPIs
- Pricing models and economics
- Regulatory requirements
- Business rules and constraints

## Files to Add

When starting a new project, create documents here describing:
1. **Application Overview** - What business problem does the app solve?
2. **User Journeys** - Critical paths users take through the application
3. **Business Rules** - Validation rules, workflows, approval chains
4. **Success Metrics** - What defines a successful test coverage?

## Example Structure

```markdown
# [Project Name] Business Context

## Domain
[Brief description of the business domain]

## Key Users
- **Admin**: Manages system configuration
- **Manager**: Reviews reports and approves requests
- **End User**: Primary application consumer

## Critical Workflows
1. User registration and onboarding
2. [Core business process]
3. Reporting and analytics

## Business Rules
- [Rule 1]
- [Rule 2]
```

---

> 💡 **Tip**: Keep business memory updated as requirements evolve. All AI assistants should read this before generating tests.
