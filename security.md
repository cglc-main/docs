# Security updates

| What | How | Merges |
|---|---|---|
| Dependencies of every repo (npm, images by digest, Helm charts, Actions by digest, OpenTofu providers) | Renovate (`cglc-main/.github` renovate/default.json); the Dependency Dashboard issue in each repo lists everything pending | minor and patch on their own after the checks; majors wait for a person |
| Known vulnerabilities in dependencies | Renovate's vulnerability alerts (GitHub advisories and OSV): PRs at any time, labelled `security` | on their own after the checks, majors included: a broken release is smoke-tested and reverted |
| Debian packages | `unattended-upgrades` on every node | on their own; **kured** reboots a node that needs it, one at a time, drained first, 02:00–05:00 |
| k3s | system-upgrade-controller, node by node; Renovate proposes the version (`configs/k3s-upgrade.yaml`, `tofu/nodes.tf`) | patch releases on their own; minors and majors wait for a person |
| Flux | Flux Operator follows the latest 2.x (`flux-system/flux-instance.yaml`) | on its own |
| Our images | Trivy in each app's release: a critical vulnerability with a fix available stops the release | — |
| GitHub | Dependabot alerts, secret scanning with push protection, branch protection with required checks | — |

Watch-list (no automation can do this): Ory publishes open-source releases rarely and without backports; follow the
security advisories of ory/kratos, ory/hydra, ory/keto and ory/oathkeeper.
