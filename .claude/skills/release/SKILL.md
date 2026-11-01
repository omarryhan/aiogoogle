---
name: release
description: Publish a new aiogoogle release to GitHub and PyPI, which covers merging a green PR if one is named, bumping the version, pushing to master, creating the GitHub release, and verifying the PyPI upload. Use whenever the user wants to cut, ship, or publish a release or new version of aiogoogle, or says "merge this PR and release it", even if they don't mention PyPI.
---

# Release aiogoogle

Creating a GitHub release triggers `.github/workflows/publish.yml`, which uploads to PyPI. A PyPI version can't be reused once uploaded, so check everything before step 5. Stop and report if any check fails, and don't work around it.

Any maintainer can run this. It needs `gh` signed in with write access to `omarryhan/aiogoogle` and permission to push to `master`. No PyPI credentials are needed locally, because the upload runs in GitHub Actions. Check with `gh auth status` and `gh repo view omarryhan/aiogoogle --json viewerPermission`.

## 1. Merge the PR (if one was named)

```bash
gh pr view <N> --repo omarryhan/aiogoogle --json state,mergeStateStatus,reviewDecision,statusCheckRollup,headRefOid,title,author,body
gh pr diff <N> --repo omarryhan/aiogoogle
```

Read the diff. Merge only when every check succeeded and `mergeStateStatus` is `CLEAN`. If checks are still running, wait for them. Use a merge commit, matching the repo's history, and pin the reviewed commit so a late push can't slip in:

```bash
gh pr merge <N> --repo omarryhan/aiogoogle --merge --match-head-commit <headRefOid>
```

## 2. Choose the version

Read `__version_info__` in `aiogoogle/__version__.py` and review every change since the last tag:

- **Breaking change:** bump the major version and reset the rest (5.20.0 → 6.0.0). That covers anything that can break existing callers, such as removed or renamed APIs, changed signatures or defaults, different exception types, or dropped Python versions. Tell the user which change makes it breaking, and call it out in the release notes with what users need to update.
- **Anything else:** bump the minor version, even for bug fixes (5.18.0 → 5.19.0 → 5.20.0).

Check that the tag is free with `gh release list --repo omarryhan/aiogoogle --limit 5`.

## 3. Bump and push

Start from the latest master. `master` is often checked out in another worktree, so work on the current branch and push to master by ref rather than switching:

```bash
git fetch origin master
git merge --ff-only origin/master
```

Edit `__version_info__`, then commit only that file with the message `bump version`, and push:

```bash
git push origin HEAD:master
```

If `--ff-only` fails, the current branch has its own work. Commit from a detached `origin/master` instead, so that work doesn't land on master.

## 4. Wait for CI on the bump commit

```bash
gh run list --repo omarryhan/aiogoogle --commit <sha> --workflow CI --json databaseId --jq '.[0].databaseId'
gh run watch <id> --repo omarryhan/aiogoogle --exit-status
```

The run can take a few seconds to appear. CI must pass on the exact commit being released, since a green PR doesn't cover the merge result.

## 5. Publish the release

Write the notes in the format of recent releases, one bullet per merged change since the last tag, with a short paragraph on any behavior change users need to act on. List the changes with `git log <last-tag>..HEAD --merges`.

```markdown
## What's Changed

- Short description (#PR, fixes #issue) — @author

What changed for users, and anything they need to update.

**Full Changelog**: https://github.com/omarryhan/aiogoogle/compare/vOLD...vNEW
```

Tag and title are both `vX.Y.Z`. Pin the target to the commit CI just verified:

```bash
gh release create vX.Y.Z --repo omarryhan/aiogoogle --target <sha> --title vX.Y.Z --notes-file <notes> --latest
```

## 6. Verify PyPI

Watch the `Upload Python Package` run, then confirm the upload itself. A green workflow alone doesn't show the files arrived.

```bash
gh run list --repo omarryhan/aiogoogle --workflow publish.yml --event release --limit 1 --json databaseId,headSha
gh run watch <id> --repo omarryhan/aiogoogle --exit-status
curl -s https://pypi.org/pypi/aiogoogle/json | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["info"]["version"], [f["filename"] for f in d["releases"].get("X.Y.Z", [])])'
```

Expect a wheel and an sdist. PyPI's JSON can lag by a few seconds, so retry briefly before calling it a failure.

If the upload failed, the tag and release already exist, so tell the user rather than deleting or re-creating them, and skip step 7.

## 7. Thank the contributors

Once the version is on PyPI, comment on each merged PR in the release, including ones merged before this run, so contributors know their work has shipped. Skip PRs written by the maintainer running the release and by bots. Comment only after verifying PyPI, so the install command in the message works.

```bash
gh pr comment <N> --repo omarryhan/aiogoogle --body-file <comment>
```

```markdown
Thanks for your contribution, @author! This is now released in [vX.Y.Z](https://github.com/omarryhan/aiogoogle/releases/tag/vX.Y.Z) and available on PyPI:

    pip install -U aiogoogle
```

Finish by reporting the release URL, the PyPI version, and the PRs commented on.
