---
title: "snowball-sprint-demo-app: Decisions"
type: decision-log
date: 2026-07-13
updated: 2026-10-27
source: Written at the pauses in the milestone sequence (the proposal pick, the plan's out-of-scope list, a change of direction mid-session, the close of a merged branch)
description: Why each decision was made and what was passed over, one entry per decision, plus the outcome, lesson, and client words at the close of every milestone. Read by the timelapse record and by the case study.
related: [PRD.md, DESIGN.md]
tags: [decisions, snowball-sprint-demo-app]
---

# snowball-sprint-demo-app: Decisions

## Decisions

One decision per entry, numbered in the order they were made. `Instead` names the road not taken and is never blank when a proposal was rejected. A later decision that replaces an earlier one says so in `Supersedes` and leaves the old entry in place. The entry shape is in the `stack-markdown` skill's `template/decision-log.md`.

### D001: Claude Desktop sessions run inside the dev container, reached over SSH
- Date: 2026-11-02
- Branch: desktop-ssh-sessions
- Area: stack
- Because: The setup rolled out from curiouscarbons-site (its DECISIONS.md, D001 to D008): sshd in the image started per connection by `docker exec`, a fixed `snowball-sprint-demo-app-dev` container name, the whole transcript folder mounted from `~/.claude/container-projects/snowball-sprint-demo-app`, and unsigned commits from Desktop sessions. Applied to every container repo at once at Doug's request instead of waiting for the November 10 review.
- Instead: waiting for the November 10, 2026 review to pick repos one by one.
- Supersedes: none

### D002: osv-scanner in the image replaces the post-push Dependabot read
- Date: 2026-11-03
- Branch: add-osv-scanner
- Area: stack
- Because: The push-time step read Dependabot's alerts after a push, which needed a GitHub sign-in every time and only ever saw `main` (Dependabot scans the default branch). osv-scanner reads every lock file on the branch before the push, platform-only entries included, with no sign-in. From the stack-devcontainer template, version and checksums pinned.
- Instead: keeping the Dependabot read with a sign-in per push, or a lasting GitHub token in the container.
- Supersedes: none

## Milestone close

One entry per merged branch, written before the merge from Doug's answers. "none" is a valid answer for every line; an invented answer is not.

### desktop-ssh-sessions
- Merged: 2026-11-02
- Outcome: Measured on 2026-11-02: the image built and `sshd -t` passed on the new configuration (the rollout's build test).
- Lesson: none
- Client said: none

### add-osv-scanner
- Merged: 2026-11-03
- Outcome: Measured on 2026-11-03: the image built with the checksum check passing and `osv-scanner --version` printed 2.7.0.
- Lesson: none
- Client said: none

### fix-dependency-scan
- Merged: 2026-11-03
- Outcome: Measured on 2026-11-03: osv-scanner went from one critical finding in certifi and four high in pyasn1 to one medium finding (minimatch, a development package); the app loaded and /health answered 200.
- Lesson: none
- Client said: none
