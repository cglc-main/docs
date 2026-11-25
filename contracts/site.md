# Contract: bulbashenko.com

Production runs in the k3s cluster managed by Flux from [cglc-main/infra](https://github.com/cglc-main/infra). The site's
repo ([cglc-main/bulbashenko.com](https://github.com/cglc-main/bulbashenko.com)) releases versions and owns the
Kubernetes base in `deploy/`; infra decides which version runs (`BULBASHENKO_COM_VERSION` in
`clusters/prod/pins.env`). This page covers what concerns the site.

## Overview

| Piece | Where |
| --- | --- |
| App | Deployment `site` in the namespace `bulbashenko-com` (`deploy/site.yaml`). Next.js standalone on port 3000, 2 replicas on different nodes (PriorityClass `tier-1`), read-only root filesystem |
| Public traffic | Gateway `traefik/main` (TLS) → HTTPRoute `site` (`deploy/routes.yaml`). `www.` redirects to the apex |
| Images | `ghcr.io/cglc-main/bulbashenko.com`, `-migrate`, `-e2e`, all tagged with the release version `X.Y.Z`, built by `.github/workflows/release.yml` after `test` passes on `main`. The packages are public, so the cluster pulls them without credentials |
| Database | CloudNativePG cluster `pg` in the namespace `data`: one database and role for the site. Backups are infra's |
| Media | Nextcloud Team folder `Site` (`Gallery/`, `Files/`), read by the app as the read-only user `site` over WebDAV. Served to visitors by the app itself at `/m/…`. See [Media](#media) |
| Admin sign-in | Ory Hydra at `https://auth.bulbashenko.com`, client `bulbashenko-site` (defined in [cglc-main/auth](https://github.com/cglc-main/auth), group `site-admins`) |

## What infra provides

- **A Flux `GitRepository`** on the release tag, with a `Kustomization` for `deploy/`. The images in
  `deploy/kustomization.yaml` are set to the same version (`clusters/prod/releases/bulbashenko-com.yaml`).
- **A second `Kustomization` for `deploy/smoke`**. It depends on the first and waits for the Job.
- **The Gateway `traefik/main`**, which terminates TLS for `bulbashenko.com` and `www.bulbashenko.com`.
- **The PriorityClass `tier-1`.**
- **The ConfigMap `internal-ca`** (key `ca.crt`): the CA of the Postgres server certificate.
- **The Secret `site`:**

| Key | Notes |
| --- | --- |
| `DATABASE_URL` | `postgresql://…@pg-rw.data.svc.cluster.local:5432/…?sslmode=verify-full&sslrootcert=/etc/internal-ca/ca.crt` |
| `JWT_SECRET` | Signs the admin session cookie and the short-lived sign-in flow cookie |
| `OIDC_CLIENT_SECRET` | Same value as `OIDC_SITE_CLIENT_SECRET` in the auth Secret |
| `NEXTCLOUD_PASSWORD` | App password of the Nextcloud user `site` |

The plain values (`SITE_URL`, `OIDC_ISSUER`, `OIDC_CLIENT_ID`, `NEXTCLOUD_*`) are in `deploy/site.yaml`.
`NEXT_PUBLIC_SITE_URL` and `NEXT_PUBLIC_GOOGLE_SITE_VERIFICATION` are inlined at build time from GitHub repository
variables (Docker build args).

Env from a Secret is read only at pod start. After changing the Secret in infra (`clusters/prod/apps/bulbashenko-com/secret.sops.yaml`), restart the Deployment:
`kubectl -n bulbashenko-com rollout restart deploy/site`.

## Deploying

The whole path is in [delivery.md](../delivery.md). For the site:

- A merged pull request becomes a release `vX.Y.Z` with three images, and Renovate proposes it to infra at once.
- **Rollout.** A new pod replaces an old one only after staying ready for `minReadySeconds` (150 s, longer than the
  liveness window), and no old pod goes before that (`maxUnavailable: 0`). A version that starts and then dies
  never takes the site down: the rollout misses `progressDeadlineSeconds`, Flux's health check fails and the bot
  reverts the version. A deploy therefore takes about six minutes.
- **Migrations.** The init container `migrate` (image `-migrate`, `scripts/migrate.mjs`) applies new migrations
  before the new version starts. The old pods keep serving until the new ones are ready. A failed migration leaves
  production on the old version and alerts.
- **Smoke suite.** The `e2e/` suite runs against production after every deploy and changes nothing. It checks
  that `/api/health` reports the deployed commit, that the pages render and languages switch, and that media is
  served. Locally: `cd e2e && npm ci && E2E_SITE=http://localhost:3000 npx playwright test`.
- **Rollback** by hand: revert the version's commit in infra; Flux deploys the previous release. A rollback does
  not undo a migration (see below).

## Schema changes

Prisma Migrate: every schema change comes with a migration file in `prisma/migrations`.

```sh
# edit prisma/schema.prisma, then (local Postgres from docker-compose.yml):
npx prisma migrate dev --name <what-changed>
```

- CI (`check`) fails if `prisma/schema.prisma` and the migrations differ.
- After migrating, `migrate.mjs` checks that the database matches the schema exactly, and fails otherwise (drift
  from a hand-made change). The log shows the difference.
- Keep migrations backward compatible with the running version: add, then use, then drop in a later release.
  During a rollout the old pods still serve on the new schema, and a rollback does not undo a migration.

## Sign-in and sign-out

- **Sign-in:** `/api/auth/oidc/login` → Hydra (two factors, group `site-admins`) → `/api/auth/oidc/callback`. The
  callback creates a `Session` row with the ID token's `sub`, `sid` and the ID token itself, and sets a cookie that
  names the row. Every admin request checks that the row still exists (`src/proxy.ts`).
- **Sign-out in the panel:** the row is deleted, then the browser goes to Hydra's end-session endpoint with the ID
  token (`id_token_hint`). The SSO session ends, so every app's single sign-on ends with it, and Hydra returns to
  the home page.
- **Sign-out anywhere else:** Hydra POSTs a logout token to `/api/auth/oidc/backchannel-logout`. The app verifies
  it against Hydra's keys and deletes the rows of that SSO session.

## Media

The owner uploads in Nextcloud, never through the site: `Site/Gallery` (pictures and videos) and `Site/Files`
(anything, any size; subfolders become groups on the page).

- **Sync** (`src/lib/media-sync.ts`). At most once a minute (on a page render or `/api/media`), the app checks the
  Team folder with a depth-0 PROPFIND. Nextcloud changes the folder's etag whenever anything below it changes, so
  the full walk runs only then.
  - Rows in `MediaItem` follow the files by Nextcloud's file id, so renames and moves keep the caption and order.
  - The admin panel's SYNC runs it at once.
- **Serving** (`src/app/m/[id]/[name]/route.ts`). The app streams from Nextcloud and passes through Range, ETag and
  304, so video seeks and downloads resume, and memory does not grow with file size.
  - `Files/` is always a download.
  - `?w=400|1600` is a preview from Nextcloud's preview API (images only).
  - Hidden items answer 404, except the one used as the profile photo.
  - Every response carries a sandbox CSP, so an uploaded file cannot run script on the site's origin.
- **Availability.** The site depends on Nextcloud for media only. When Nextcloud is down, pages still render from
  the last known list, but files and previews don't load.
- **Locally.** Run `docker compose up -d`, then `sh scripts/nextcloud-dev-setup.sh --fixtures` (the user `site`,
  the Team folder, sample files), and start the app with the env it prints. CI runs the same setup and
  `scripts/media-smoke.sh` (job `media` in `test.yml`).
