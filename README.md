# docs

The single source of truth for the cglc-main cluster: how it is built, how a change reaches production, and what to
do when something breaks. For the owner, for anyone invited to help, and for AI agents (every repo's `AGENTS.md`
points here).

| Start here | |
|---|---|
| [architecture.md](architecture.md) | What runs where: nodes, network, storage, memory, high availability |
| [decisions.md](decisions.md) | Why it is built this way |
| [delivery.md](delivery.md) | From a commit to production: releases, Renovate, deploys, automatic revert |
| [security.md](security.md) | What updates itself, what waits for a person |
| [onboarding.md](onboarding.md) | Inviting someone: accounts, the mesh, keys |

| Contracts (what an app needs from the cluster) | |
|---|---|
| [contracts/auth.md](contracts/auth.md) | The SSO (cglc-main/auth) |
| [contracts/site.md](contracts/site.md) | bulbashenko.com (cglc-main/bulbashenko.com) |
| [contracts/adding-a-service.md](contracts/adding-a-service.md) | Checklist for a new service |

| Services | Runbooks |
|---|---|
| [services/auth.md](services/auth.md) | [operations/initial-release.md](operations/initial-release.md) — building everything from nothing |
| [services/site.md](services/site.md) | [operations/rebuild-node.md](operations/rebuild-node.md) |
| [services/headscale.md](services/headscale.md) | [operations/lost-node.md](operations/lost-node.md) |
| [services/stalwart.md](services/stalwart.md) | [operations/restore.md](operations/restore.md) — Postgres, Headscale, files, mail, etcd |
| [services/nextcloud.md](services/nextcloud.md) | [operations/secrets.md](operations/secrets.md) — editing and rotating secrets |
| [services/monitoring.md](services/monitoring.md) | [operations/storage-box.md](operations/storage-box.md) |

## Repositories

| Repository | What it holds |
|---|---|
| [infra](https://github.com/cglc-main/infra) | OpenTofu (`tofu/`, `hosts/`) and Flux (`clusters/prod/`, `components/`) |
| [.github](https://github.com/cglc-main/.github) | Renovate policy, reusable workflows (release, PR titles), the Renovate runner |
| [auth](https://github.com/cglc-main/auth) | Single sign-on (Ory) |
| [bulbashenko.com](https://github.com/cglc-main/bulbashenko.com) | The site |
| docs | This |

A change to any of them that changes how things work changes the page here in the same pull request.
