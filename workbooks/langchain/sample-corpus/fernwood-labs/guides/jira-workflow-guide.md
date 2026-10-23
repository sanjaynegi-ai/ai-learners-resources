# Jira Workflow Guide

## Ticket States

Tickets move through the following states, in order:

1. **Backlog** — not yet prioritized
2. **Ready** — prioritized and scoped, ready to be picked up
3. **In Progress** — actively being worked on
4. **In Review** — in code review or QA
5. **Done** — merged, deployed, and verified

Tickets should never skip from Backlog directly to In Progress — they must pass through Ready so the team can confirm scope first.

## Story Points

We estimate using a Fibonacci-like scale: **1, 2, 3, 5, 8, 13**. Anything that would be estimated above 13 should be split into smaller tickets before the sprint starts.

## Sprint Cadence

Sprints are **2 weeks** long, starting on Mondays. Sprint planning happens on the first Monday; the sprint review and retro happen on the second Friday.

## Labels

- `bug` — defect in existing functionality
- `tech-debt` — refactor or cleanup work with no user-facing change
- `customer-reported` — originated from a support ticket; must link the originating ticket
