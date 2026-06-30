# Git Cheat Sheet

Daily Git workflow for the **M_DevOps_Transformation** project.

---

# Create a Feature Branch

```bash
git checkout main
git pull
git checkout -b feature/<feature-name>
```

---

# Check Status

```bash
git status
```

---

# Stage Changes

```bash
git add .
```

---

# Commit

```bash
git commit -m "type: short description"
```

Examples:

```text
feat: add Docker health check
fix: correct README links
docs: update Git cheat sheet
refactor: simplify application startup
chore: update dependencies
```

---

# Push Branch

```bash
git push -u origin feature/<feature-name>
```

---

# Keep Your Feature Branch Up to Date

```bash
git checkout main
git pull

git checkout feature/<feature-name>

git merge main
```

---

# After Pull Request Merge

The feature branch is deleted in **GitHub** after the Pull Request has been reviewed and merged.

Update your local repository:

```bash
git checkout main
git pull
git branch -d feature/<feature-name>
```

---

# Undo Last Commit (keep changes)

```bash
git reset --soft HEAD~1
```

---

# Undo Last Commit (discard changes)

```bash
git reset --hard HEAD~1
```

---

# View Commit History

```bash
git log --oneline --graph --decorate --all
```

---

# Daily Workflow

```text
Start
 │
 ▼
git checkout main
 │
 ▼
git pull
 │
 ▼
git checkout -b feature/<feature-name>
 │
 ▼
Implement changes
 │
 ▼
git status
 │
 ▼
git add .
 │
 ▼
git commit
 │
 ▼
git push -u origin feature/<feature-name>
 │
 ▼
Create Pull Request
 │
 ▼
Code Review
 │
 ▼
Merge Pull Request
 │
 ▼
Delete branch in GitHub
 │
 ▼
git checkout main
 │
 ▼
git pull
 │
 ▼
git branch -d feature/<feature-name>
 │
 ▼
Next Feature
```