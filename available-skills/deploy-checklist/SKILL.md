---
name: deploy-checklist
description: Pre-deployment verification checklist. Use before deploying to production, staging, or any environment. Use when the user says "deploy", "ship", "release", "go live", or "push to production".
argument-hint: "[environment: production|staging|preview]"
disable-model-invocation: true
---

# Deployment Checklist

Systematic pre-deployment verification. Run this before every deployment.

## Checklist

### 1. Code Quality
- [ ] All tests passing (`$TEST_COMMAND` or project's test runner)
- [ ] Linter clean (no warnings or errors)
- [ ] No `TODO` or `FIXME` comments in changed code
- [ ] No `console.log` / `print()` debug statements in changed code
- [ ] No hardcoded secrets, API keys, or credentials
- [ ] No `.env` files staged for commit

### 2. Functionality
- [ ] Feature works as specified in acceptance criteria
- [ ] Edge cases handled (empty inputs, errors, timeouts)
- [ ] Error messages are user-friendly (no raw stack traces)
- [ ] Loading states exist for async operations
- [ ] Rollback path exists if deployment fails

### 3. Security
- [ ] Input validation on all user inputs
- [ ] SQL queries parameterized (no string concatenation)
- [ ] Authentication/authorization checked on new endpoints
- [ ] CORS configured correctly (not `*` in production)
- [ ] Rate limiting on public endpoints
- [ ] No sensitive data in logs

### 4. Performance
- [ ] No N+1 queries introduced
- [ ] Large lists paginated
- [ ] Images optimized and lazy-loaded
- [ ] No blocking operations on critical path

### 5. Database (if applicable)
- [ ] Migrations tested on clean database
- [ ] Migrations are reversible
- [ ] No data loss in migration
- [ ] Indexes added for new query patterns

### 6. Documentation
- [ ] API changes documented (if public API)
- [ ] README updated if setup steps changed
- [ ] Changelog updated for user-facing changes

## Process
1. Run through each section above
2. For any unchecked item, investigate and fix or explicitly document why it's acceptable
3. Report: ready to deploy or blocked with specific issues
