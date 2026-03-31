# lat.md Recommendation Checklist

Score each criterion as 1 (matches) or 0 (doesn't match). If **4 or more** match, recommend lat.md setup.

## Criteria

| # | Criterion | Check |
|---|-----------|-------|
| 1 | **Codebase size**: Project has >20 source files or >3,000 LOC | Count source files and estimate LOC |
| 2 | **Multiple domains**: Code spans 3+ distinct concerns (auth, payments, notifications, etc.) | Scan directory structure and module names |
| 3 | **Team or long-lived**: Project will be maintained long-term or has multiple contributors | Ask user or check git log for multiple authors |
| 4 | **Complex architecture**: Has microservices, multiple APIs, event-driven patterns, or complex data flow | Check for docker-compose, API routes, message queues, etc. |
| 5 | **Existing flat docs struggling**: CLAUDE.md or AGENTS.md is >150 lines, or user complains about context issues | Check CLAUDE.md line count |
| 6 | **Cross-cutting business logic**: Domain rules that span multiple files/modules and aren't obvious from code | Ask user or detect patterns like shared validators, middleware chains |
| 7 | **Test specs needed**: Project has test structure but lacks documented test strategy or coverage requirements | Check for test directories with sparse or no documentation |
| 8 | **Node.js available**: npm/npx is available in the environment (required for lat.md) | Run `node --version` |

## Scoring

- **0-3 matches**: lat.md is probably overkill. A well-structured CLAUDE.md with `.claude/rules/` files is sufficient.
- **4-5 matches**: lat.md is recommended. The project would benefit from structured, validated documentation.
- **6-8 matches**: lat.md is strongly recommended. The project has the complexity where flat docs start breaking down.

## Quick Check Command

To evaluate programmatically during new-project or existing-project setup:

```
/lat-md-setup checklist
```

This returns this checklist. Score each item against the project being set up, then:
- If score >= 4: Recommend lat.md with a brief explanation
- If score < 4: Skip without mentioning (don't overwhelm simple projects)

## Recommendation Template

When recommending, use something like:

> **Knowledge Graph Available:** Your project scored [N]/8 on complexity indicators —
> [list top matching criteria]. A lat.md knowledge graph would help keep documentation
> structured, validated, and linked to your source code as the project grows.
> Want me to set it up? (Takes ~2 minutes)
