# Delivery

How a change reaches production. People decide by merging pull requests; the GitHub App **cglc-auto-bot** and Flux do
everything else.

## An app (auth, the site)

```
PR (title: feat: / fix: / ...) ─► test (required) ─► merge (squash)
  └► release.yml: semantic-release ─► tag vX.Y.Z + GitHub Release with the changelog
       └► images :X.Y.Z, each scanned by Trivy before it is pushed (a critical vulnerability with a fix stops here)
            └► Renovate (dispatched at once) ─► PR in infra: one line in clusters/prod/pins.env
                 └► validate (required) ─► merges itself
                      └► Flux: GitRepository at vX.Y.Z, the base with the images of X.Y.Z, rollout
                           └► smoke Job against production
                                ├► passes: commit status on the app's commit, message in Telegram
                                └► fails (or the rollout never becomes ready):
                                     revert-pin.yml reverts the pins.env commit (PR, merges itself),
                                     the previous version comes back, alert in Telegram
```

- **Versions.** `feat:` → minor, `fix:` / `perf:` → patch, `feat!:` or `BREAKING CHANGE:` → major. Other types
  (`chore:`, `docs:`, `test:`, `ci:`) make no release. The PR title is the commit (squash merges), and `pr-title`
  checks it.
- **Big changes as a stack.** Split a feature into small PRs with `gh stack`: each layer is reviewed on its own,
  and `gh stack merge` on the top one lands the whole stack in one push, hence one release.
- **Hotfixes** are their own small `fix:` PR straight to `main`: a patch release minutes later.
- **One version, one line.** `AUTH_VERSION=1.4.2` in `pins.env` sets the GitRepository tag `v1.4.2` and every image
  tag (`postBuild.substituteFrom`). Renovate watches the e2e image, the last one a release pushes, so it never
  proposes a version whose images are not all there.
- **Reverts.** Flux reports a failed health check or smoke Job to infra (`repository_dispatch`); `revert-pin.yml`
  acts only if the failing version is the one pins.env runs. Renovate does not offer a reverted version again; the
  next release does.
- **What a deploy must survive.** The app's Deployments use `maxUnavailable: 0` and a `minReadySeconds` longer
  than the liveness window, and a `progressDeadlineSeconds`: a version that dies never replaces the running one, and
  the deadline turns it into a failed health check.
- **By hand**, should it be needed: revert the version's commit in infra, or edit pins.env to an older version.

## The platform (infra)

- Every PR runs `validate`: every Kustomization builds and validates (kubeconform with CRD schemas), every secret is
  encrypted, OpenTofu formats and validates, workflows lint.
- Renovate keeps charts, images (by digest), Actions, OpenTofu providers and k3s current: minor and patch updates
  merge themselves after `validate`; majors wait for a person ([security.md](security.md)). A chart update waits
  2 hours after its release: Flux reads chart repository indexes every hour, and a version missing from the index
  stalls the HelmRelease until the next read.
- **When Renovate runs.** Every 30 minutes, for every repository: the CronJob `flux-system/renovate-dispatch` in infra
  dispatches `renovate.yml` in `.github`, because GitHub drops most scheduled runs (the workflow's own schedule,
  every 3 hours, is only a fallback). An app release dispatches it at once. Runs and logs: the Actions tab of `.github`.
- Flux applies `main` (layers in `clusters/prod/layers.yaml`: CRDs → controllers → configs → monitoring and apps →
  releases). Failures reach Telegram.
- **OpenTofu** (`tofu/`, `hosts/`): a PR gets the plan as a comment; after the merge, the apply waits for a person's
  approval in the GitHub Environment `production`.

## What only a person does

- Merge major updates (vulnerability fixes excepted).
- Approve `tofu apply`.
- Change secrets (`sops`, [operations/secrets.md](operations/secrets.md)).
- Restore from backups, delete data.
- Manage people and groups (`users.int.bulbashenko.com`).
- The steps of [operations/initial-release.md](operations/initial-release.md) that cannot be automated.
