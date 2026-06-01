# Codex Git rules

These rules apply to this Obsidian repository and any clone of it.

## Required behavior

1. Do not run `git pull`, merge a remote branch, or rebase onto a remote branch unless the user explicitly asks for that exact action.
2. Keep remote legacy site or workflow content out of the repository. Do not restore or push `.github/` or `docs/`.
3. Push only local vault content and `.obsidian/` additions or changes, unless the user explicitly names another file or folder.
4. Do not commit or push `BaiduSyncdisk/` or `Baidusyncdisk/`.
5. Do not force-add ignored folders with `git add -f` unless the user explicitly asks for the exact ignored path.

## Ignore rules that must stay

The repository `.gitignore` must keep these entries:

```gitignore
.github/
docs/
BaiduSyncdisk/
Baidusyncdisk/
```

## Checks before commit or push

Run these checks before staging, committing, or pushing:

```powershell
git status --short --branch
git diff --cached --name-status
git ls-files
```

Check that staged files do not include `.github/`, `docs/`, `BaiduSyncdisk/`, or `Baidusyncdisk/`.

## Prior cleanup record

The repository was cleaned so that tracked remote legacy content outside `.obsidian/` was removed. The cleanup removed `.github/workflows/pages.yml` and `docs/`, then pushed local vault Markdown files and `.obsidian` changes to `Hilde/master`.
