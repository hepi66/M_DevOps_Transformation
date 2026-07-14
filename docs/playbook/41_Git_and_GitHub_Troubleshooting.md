# Git and GitHub Troubleshooting Guide

## Purpose

This guide documents common Git and GitHub issues that may occur during development and operation of the M-DevOps platform.

The objective is to provide symptom-driven troubleshooting procedures that reduce investigation time and preserve project knowledge.

This guide focuses on source control, repository management, branching, synchronization, and GitHub-related issues.

---

# Troubleshooting Philosophy

Git issues often appear simple but can have significant downstream impact.

Examples:

```text id="w4u8mk"
Failed Commit
        ↓
No Push
        ↓
No CI/CD
        ↓
No Deployment
```

Always investigate source control issues early.

---

# Symptom Classification

Typical Git and GitHub issues fall into:

```text id="z8r2pv"
Local Repository Issues

Branch Issues

Push Failures

Merge Conflicts

Repository Synchronization Issues

GitHub Access Issues
```

Correct classification accelerates resolution.

---

# Investigation Workflow

Recommended order:

```text id="x2m9qc"
git status
        ↓
git branch
        ↓
git log
        ↓
git remote -v
        ↓
GitHub Repository
```

Start locally before assuming a GitHub problem.

---

# Issue: Working Tree Not Clean

## Symptom

```powershell id="q7v4pt"
git status
```

Output:

```text id="g3m8rd"
Changes not staged for commit
```

or

```text id="m5w1zk"
Untracked files
```

---

## Meaning

Local changes exist that have not been committed.

---

## Investigation

Review modified files:

```powershell id="y6q3vn"
git status
```

Review detailed changes:

```powershell id="t1p8mk"
git diff
```

---

## Resolution

Commit intended changes:

```powershell id="u9v4qx"
git add .

git commit -m "description"
```

or discard unintended changes.

---

# Issue: Commit Created But Not Pushed

## Symptom

Local changes appear committed but are not visible in GitHub.

---

## Investigation

Review recent commits:

```powershell id="d4m8tx"
git log --oneline -5
```

Verify remote synchronization:

```powershell id="f7q2pw"
git status
```

Example:

```text id="s2v8ry"
Your branch is ahead of origin
```

---

## Resolution

Push changes:

```powershell id="m9x3kt"
git push
```

---

# Issue: Push Rejected

## Symptom

```powershell id="v8m4rq"
git push
```

returns an error.

---

## Common Causes

```text id="a7p9wd"
Remote repository changed

Branch divergence

Permission issue
```

---

## Investigation

Execute:

```powershell id="g4t2mx"
git status
```

and:

```powershell id="n5w8pv"
git fetch
```

Review differences before proceeding.

---

## Resolution

Often:

```powershell id="k2q7vn"
git pull
```

followed by:

```powershell id="j8m1pr"
git push
```

If merge conflicts occur, resolve them before pushing.

---

# Issue: Merge Conflict

## Symptom

Git reports:

```text id="r6t4qy"
CONFLICT
```

during pull or merge operations.

---

## Meaning

Two changes affect the same content.

Git cannot automatically determine the correct result.

---

## Investigation

Open affected files.

Conflict markers typically appear:

```text id="x4p9mb"
<<<<<<<

=======

>>>>>>>
```

---

## Resolution

Review both versions.

Create the correct final result.

Remove conflict markers.

Then:

```powershell id="z8v3tk"
git add .

git commit
```

Validate application functionality after conflict resolution.

---

# Issue: Wrong Branch

## Symptom

Changes appear missing or commits appear in an unexpected location.

---

## Investigation

Check current branch:

```powershell id="m4r7xp"
git branch
```

Current branch is marked with:

```text id="t2w6pk"
*
```

---

## Resolution

Switch to the correct branch:

```powershell id="k7m9rd"
git checkout <branch-name>
```

Verify branch before continuing development.

---

# Issue: Remote Repository Misconfigured

## Symptom

Pushes fail or target an unexpected repository.

---

## Investigation

Review remotes:

```powershell id="c5v8tm"
git remote -v
```

Verify:

```text id="r9x2pk"
origin
```

points to the expected GitHub repository.

---

## Resolution

Correct remote configuration if required.

Verify before pushing again.

---

# Issue: Repository Appears Out Of Date

## Symptom

GitHub contains commits that are not visible locally.

---

## Investigation

Execute:

```powershell id="y4m1qw"
git fetch
```

Review:

```powershell id="n7v3pk"
git log --oneline --all
```

---

## Resolution

Synchronize repository:

```powershell id="h5q8mx"
git pull
```

Verify expected commits are present.

---

# Issue: Accidental File Commit

## Symptom

Unexpected files appear in a commit.

Examples:

```text id="d2p7rk"
Temporary files

Generated files

Local artifacts
```

---

## Investigation

Review commit contents:

```powershell id="w9m4tp"
git show
```

---

## Prevention

Maintain:

```text id="q3v8my"
.gitignore
```

Review:

```powershell id="t7q2nv"
git status
```

before committing.

---

# Issue: Large Repository Changes

## Symptom

Unexpectedly large commit.

---

## Investigation

Review:

```powershell id="s8m5pk"
git diff
```

and:

```powershell id="a6q9rv"
git status
```

---

## Lesson Learned

Large structural changes should be reviewed carefully before committing.

Repository reorganizations may affect:

```text id="p4x7wd"
Documentation

GitOps

Automation

Validation Scripts
```

---

# Issue: GitHub Actions Not Triggered

## Symptom

Push succeeds but no workflow starts.

---

## Investigation

Verify:

```text id="u8m2px"
.github/workflows
```

exists and workflow files are present.

Confirm push reached GitHub successfully.

---

## Resolution

Review workflow configuration and GitHub Actions status.

---

# Project Lesson Learned: Documentation Structure Matters

## Observation

During the project lifecycle, documentation evolved significantly.

Multiple reorganizations occurred before a stable structure emerged.

---

## Impact

Symptoms included:

```text id="h7q4tz"
Difficult navigation

Knowledge duplication

Missing references
```

---

## Final Practice

Maintain documentation within:

```text id="j2v8rk"
docs/
```

using the defined architecture and standards.

---

# Project Lesson Learned: Repository Structure Influences GitOps

## Observation

Repository restructuring affected understanding of the deployment architecture.

---

## Impact

Several deployment-related artifacts required reconstruction and verification.

---

## Final Practice

Document:

```text id="r5m1pk"
Repository Structure

GitOps Structure

Deployment Architecture
```

explicitly.

Never rely solely on folder names for architectural understanding.

---

# Git Troubleshooting Checklist

```text id="x9v3wd"
□ Working tree clean

□ Correct branch selected

□ Commit created

□ Push successful

□ Remote repository correct

□ GitHub synchronized

□ Workflows triggered
```

This checklist resolves the majority of Git-related incidents.

---

# Success Criteria

This guide is complete when the engineer understands:

* Git investigation workflow
* Common repository issues
* Push and synchronization failures
* Merge conflict handling
* GitHub workflow triggers
* Project-specific lessons learned

The engineer should be capable of resolving routine Git and GitHub issues independently.

---

# Next Step

Continue with:

**CI/CD and GHCR Troubleshooting Guide**

This guide covers pipeline failures, container build issues, image publication problems, and artifact-related incidents.
