# Git Branching Workflow - M-DevOps-Transformation

This document defines the standardized branching and merging process for the M-DevOps-Transformation project to ensure code quality and traceability.

## 1. Workflow Overview
We follow a strict Feature-Branch workflow to maintain a clean `main` branch:
- **Feature Branch:** Every task (Sub-Issue) is implemented in a dedicated branch: `feature/epic-<ID>-<short-name>`.
- **Commit:** Atomic commits with descriptive messages (e.g., `feat(epic-1): ...`).
- **Pull Request (PR):** Changes are merged into `main` via PRs on GitHub.
- **Merge:** PRs act as the gatekeeper for code quality.

## 2. Local Workflow (Terminal)
To implement a new feature:

## 1. Create and switch to new branch
git checkout -b feature/epic-X-task-name

## 2. Add, Commit, and Push
git add .
git commit -m "feat(epic-X): descriptive message"
git push -u origin feature/epic-X-task-name

## 3. GitHub Workflow (Web Interface)
Once you have pushed your branch:
- **Open Repository: Go to the project page on GitHub.
- **Create PR: Click the "Compare & pull request" button that appears automatically.
- **Review: Add a short description of the changes. Click "Create pull request".
- **Merge: Once verified, click "Merge pull request" and confirm.
- **Cleanup: Delete the feature branch after merging to keep the repository tidy.