---
title: Git Daily Workflow
type: Cheat Sheet
status: Living Document
version: 2.2
owner: Engineering
last_updated: 2026-07-15
---

# Git Daily Workflow

> **Purpose**
>
> This cheat sheet provides the standard day-to-day Git and GitHub workflow used throughout the project. It serves as a quick reference for common development activities and complements the Engineering Playbook.

---

## Navigation

- 🏠 [Documentation Home](../README.md)
- 📋 [Engineering Cheat Sheets](README.md)
- 📘 [Engineering Playbook](../playbook/README.md)

---

# Fast Feature Workflow

> **Advanced users only — Commit, Push, Pull Request, and Cleanup**
>
> This condensed workflow covers the standard feature cycle used in most daily cases.
> Replace all placeholders and the commit message before executing the commands.

## Step 1: Update Main and Create Feature Branch

```bash
git checkout main; git pull --ff-only origin main; git checkout -b feature/<feature-name>
```

## Step 2: Commit and Push

```bash
git add .; git commit -m "Short, meaningful commit message"; git push -u origin feature/<feature-name>
```

## Step 3: Create and Merge the Pull Request

On GitHub:

```text
base: main
compare: feature/<feature-name>
```

Then:

- Review the changes.
- Wait for all CI checks to pass.
- Merge the Pull Request.
- Delete the remote feature branch on GitHub.

## Step 4: Synchronize and Clean Up Locally

```bash
git checkout main; git pull --ff-only origin main; git branch -d feature/<feature-name>
```

> **Important**
>
> Do not paste a command block unchanged.
> Replace `<feature-name>` and the commit message before execution.

---

# 1. Local Development

Update the local `main` branch before starting new work.

```bash
git checkout main
git pull --ff-only origin main
```

Create and switch to a new feature branch.

```bash
git checkout -b feature/<feature-name>
```

Work on the implementation.

Check the repository status.

```bash
git status
```

Stage all changes.

```bash
git add .
```

Create a meaningful commit.

```bash
git commit -m "Short, meaningful commit message"
```

---

# 2. Push Feature Branch

Push the feature branch to GitHub.

```bash
git push -u origin feature/<feature-name>
```

For subsequent pushes on the same branch:

```bash
git push
```

The `-u` option connects the local branch with its remote branch.

After this initial connection, the shorter `git push` command is sufficient.

---

# 3. GitHub Pull Request

After pushing the feature branch:

1. Follow the Pull Request link displayed in the terminal  
   **or**
2. Click **Compare & pull request** on GitHub  
   **or**
3. Open **Pull requests → New pull request** manually.

Select:

```text
base: main
compare: feature/<feature-name>
```

Then:

- Review the changes.
- Verify that all CI checks succeed.
- Merge the Pull Request into `main`.
- Click **Delete branch** on GitHub.

The automatic **Compare & pull request** prompt is only a convenience feature.

A Pull Request can always be created manually.

---

# 4. Add More Changes to an Open Pull Request

If the Pull Request has not yet been merged, continue working on the same feature branch.

Verify the active branch.

```bash
git branch --show-current
```

Make the additional changes.

Then:

```bash
git status
git add .
git commit -m "Add remaining feature updates"
git push
```

GitHub automatically adds the new commit to the existing Pull Request.

Do not create a new feature branch for changes that belong to the same unfinished task.

Typical history:

```text
feature/<feature-name>
│
├── Commit 1: initial implementation
├── Commit 2: fix validation issue
├── Commit 3: add remaining updates
└── Pull Request → main
```

Merge the Pull Request only when the complete feature is ready.

---

# 5. Pull Request Checks Failed

If the Pull Request checks fail, do not create a new branch.

Continue working on the existing feature branch.

## Option A: Re-run Failed Checks

If the failure was caused by a temporary GitHub Actions issue:

1. Open the failed workflow run in GitHub.
2. Click **Re-run jobs** or **Re-run failed jobs**.
3. Wait for the pipeline to complete.
4. Continue with the Pull Request once all checks pass.

## Option B: Fix the Code

Update the implementation on the same feature branch.

Check the repository status.

```bash
git status
```

Stage the changes.

```bash
git add .
```

Create a new commit.

```bash
git commit -m "Fix CI validation issue"
```

Push the update.

```bash
git push
```

GitHub automatically updates the existing Pull Request.

Wait for the CI pipeline to run again.

Merge the Pull Request only after all checks have passed.

---

# 6. Local Cleanup After Merge

Synchronize the local repository after the Pull Request has been merged.

```bash
git checkout main
git pull --ff-only origin main
```

Delete the local feature branch.

```bash
git branch -d feature/<feature-name>
```

If the remote branch was not deleted through GitHub:

```bash
git push origin --delete feature/<feature-name>
```

The feature branch is now complete.

Create a new branch for the next independent change.

---

# 7. Additional Changes After a Pull Request Was Already Merged

A merged Pull Request is closed and cannot receive additional commits.

If more work is required after the merge, treat it as a new change.

First synchronize `main`.

```bash
git checkout main
git pull --ff-only origin main
```

Create a new feature branch.

```bash
git checkout -b feature/<next-feature-name>
```

Make the changes.

Then:

```bash
git add .
git commit -m "Add follow-up changes"
git push -u origin feature/<next-feature-name>
```

Create a new Pull Request.

Do not continue using an already merged feature branch for unrelated or follow-up work.

If commits were accidentally added to the old branch after its Pull Request was merged, create a new manual Pull Request:

```text
base: main
compare: old-feature-branch
```

After the second Pull Request is merged, synchronize `main` and delete the old branch.

---

# 8. Revert an Already Merged Pull Request

Use this procedure when a merged Pull Request must be completely undone.

This also works if the original feature branch has already been deleted.

The merge commit remains part of the Git history.

## Step 1: Update Local Main

```bash
git checkout main
git pull --ff-only origin main
```

## Step 2: Find the Merge Commit

Display recent commits.

```bash
git log --oneline -10
```

Example:

```text
c936a89 Merge pull request #70 from owner/feature/example
ce5a8fc Original feature commit
bc5d050 Merge pull request #69 from owner/feature/previous
```

Use the merge commit ID, not the original feature commit ID.

In this example:

```text
c936a89
```

## Step 3: Create a Revert Branch

Preferred project workflow:

```bash
git checkout -b revert/pr-70
```

## Step 4: Revert the Merge Commit

```bash
git revert -m 1 <merge-commit-id>
```

Example:

```bash
git revert -m 1 c936a89
```

Meaning of `-m 1`:

- Keep the `main` side of the merge.
- Remove the changes introduced by the merged feature branch.

If Git opens an editor, accept or adjust the generated revert commit message, then save and close the editor.

## Step 5: Push the Revert Branch

```bash
git push -u origin revert/pr-70
```

## Step 6: Create a Pull Request

On GitHub create a Pull Request with:

```text
base: main
compare: revert/pr-70
```

Review the reverted files and allow the CI pipeline to run.

Merge the revert Pull Request only after the result has been verified.

## Step 7: Synchronize and Clean Up

```bash
git checkout main
git pull --ff-only origin main
git branch -d revert/pr-70
```

If necessary, delete the remote revert branch:

```bash
git push origin --delete revert/pr-70
```

## Verification

Confirm that the revert commit is now part of `main`.

```bash
git log --oneline -10
git status
```

Confirm that the unwanted change is no longer present.

## Important

Deleting a feature branch does not delete commits that were merged into `main`.

The merge can still be reverted by using its merge commit ID.

Avoid using `git reset` on a shared and already-pushed `main` branch.

Use `git revert` because it preserves the shared Git history.

---

# 9. Verify Whether All Branch Changes Are Already in Main

Fetch the latest remote state.

```bash
git fetch origin
```

Compare the remote feature branch with remote `main`.

```bash
git log origin/main..origin/feature/<feature-name> --oneline
```

Interpretation:

- No output: all branch commits are already included in `main`.
- Commits displayed: those commits are not yet included in `main`.

Review file differences:

```bash
git diff --stat origin/main..origin/feature/<feature-name>
```

This check is useful before deleting a branch.

---

# Daily Workflow Overview

```text
main
 │
 ├── git checkout main
 ├── git pull --ff-only origin main
 ├── git checkout -b feature/<feature-name>
 │
 ▼
feature/<feature-name>
 │
 ├── Work
 ├── git status
 ├── git add .
 ├── git commit
 ├── git push -u origin feature/<feature-name>
 │
 ▼
GitHub Pull Request
 │
 ├── Review
 ├── CI Pipeline
 │
 ├── PASS
 │     │
 │     └── Merge
 │
 └── FAIL
       │
       ├── Re-run checks
       │
       └── Fix code on the same branch
             ├── git add .
             ├── git commit
             └── git push
                  │
                  ▼
             Pull Request updated
                  │
                  ▼
             CI Pipeline
 │
 ▼
main
 │
 ├── git checkout main
 ├── git pull --ff-only origin main
 ├── git branch -d feature/<feature-name>
 │
 ▼
Ready for the next feature
```

---

# Revert Workflow Overview

```text
Merged Pull Request
        │
        ▼
Problem Identified
        │
        ▼
git checkout main
        │
git pull --ff-only origin main
        │
git log --oneline
        │
        ▼
Identify Merge Commit
        │
        ▼
Create Revert Branch
        │
git revert -m 1 <merge-commit-id>
        │
git push
        │
        ▼
Revert Pull Request
        │
        ▼
CI Validation
        │
        ▼
Merge Revert
        │
        ▼
main Restored
```

---

# Best Practices

- Create one feature branch per task.
- Start every new branch from an updated `main`.
- Keep commits small and meaningful.
- Open the Pull Request early.
- Continue pushing to the same branch while its Pull Request remains open.
- Let the CI pipeline validate every change.
- Merge only after all checks have passed.
- Never create a new branch only to fix a failed open Pull Request.
- Treat a merged feature branch as completed.
- Create a new branch for follow-up work after a merge.
- Delete merged feature branches promptly.
- Keep the local `main` branch synchronized with GitHub.
- Use `git revert` instead of rewriting shared history.
- Revert merged Pull Requests through a dedicated branch and Pull Request.
- Verify that all commits are present in `main` before deleting uncertain branches.

---

## Related Documents

- 📘 [Engineering Playbook](../playbook/README.md)
- 📋 [ArgoCD Local Operations](ArgoCD_Local_Operations.md)
- 📚 [Documentation Architecture](../handbook/01_Documentation_Architecture.md)

---

## Return to

- 📋 [Engineering Cheat Sheets](README.md)
- 🏠 [Documentation Home](../README.md)