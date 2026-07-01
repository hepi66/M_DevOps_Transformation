Title: Git Daily Workflow
Type: Cheat Sheet
Status: Living Document
Version: 2.0
Owner: Engineering
Last Updated: 2026-07-01

# Git Daily Workflow

> Quick reference for the daily Git and GitHub workflow used in this project.

---

# 1. Local Development

Create and switch to a new feature branch.

```bash
git checkout main
git pull origin main
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

For subsequent pushes:

```bash
git push
```

---

# 3. GitHub Pull Request

After pushing the feature branch:

1. Follow the Pull Request link displayed in the terminal
   **or**
2. Click **Compare & pull request** on GitHub.

Then:

- Review the changes
- Verify that all CI checks succeed
- Merge the Pull Request into `main`
- Click **Delete branch** on GitHub

---

# 4. Local Cleanup

Synchronize the local repository after the merge.

```bash
git checkout main
git pull origin main
git branch -d feature/<feature-name>
```

---

# Daily Workflow Overview

```text
main
 │
 ├── git checkout -b feature/<feature-name>
 │
 ▼
feature/<feature-name>
 │
 ├── Work
 ├── git add .
 ├── git commit
 ├── git push
 │
 ▼
GitHub Pull Request
 │
 ├── Review
 ├── CI Pipeline
 ├── Merge
 ├── Delete remote branch
 │
 ▼
main
 │
 ├── git checkout main
 ├── git pull
 ├── git branch -d feature/<feature-name>
 │
 ▼
Ready for the next feature
```

---

# Best Practices

- Create one feature branch per task.
- Keep commits small and meaningful.
- Open the Pull Request early.
- Let the CI pipeline validate every change.
- Merge only after all checks have passed.
- Delete merged feature branches immediately.
- Keep the local `main` branch synchronized with GitHub.

---

# Related Documents

- `docs/Git_Branching_Workflow.md`
- `docs/reports/E02_Transition_Report.md`
- `README.md`