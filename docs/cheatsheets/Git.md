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

# Update Feature Branch

```bash
git checkout main
git pull

git checkout feature/<feature-name>

git merge main
```

---

# Delete Local Branch

```bash
git branch -d feature/<feature-name>
```

---

# Delete Remote Branch

```bash
git push origin --delete feature/<feature-name>
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
main
 │
 ▼
git pull
 │
 ▼
Create feature branch
 │
 ▼
Code
 │
 ▼
git add .
 │
 ▼
git commit
 │
 ▼
git push
 │
 ▼
Create Pull Request
 │
 ▼
Review
 │
 ▼
Merge
 │
 ▼
Delete Branch
```