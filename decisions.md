# Decisions

Short records of why things are the way they are. A new decision gets a line here in the same PR.

| Decision | Why |
|---|---|
| Ready-made tools first; own code only where nothing exists | Own scripts and hand-picked numbers are what broke before. The own code left: `revert-pin.yml`, keepalived's one-line hook, Nextcloud's start hook and `prepare`. |
| k3s, three servers | Survives a lost node with no one acting. One server would save ~1 GB but stop all self-healing when it is lost. |
| Debian 13 | Lightest current base; kernel with WireGuard and SMB 3 encryption; k3s supports it. |
| IPv4 only | One Floating IP for everything; no AAAA that could point at a dead node. |
| keepalived for the Floating IP | Standard VRRP on the hosts, independent of Kubernetes; the old fip-controller is unmaintained. |
| No state on nodes | A lost node loses nothing (see architecture.md, "Where data lives"). |
| Headscale on SQLite + Litestream | Headscale recommends SQLite; Litestream restores it on any node. |
| Stalwart: metadata in Postgres, mail on the Storage Box | The pod moves freely; mail bodies cost nothing extra and stay out of B2. |
| Stalwart manages its own mail DNS records and certificate | DKIM rotation, MTA-STS, TLS-RPT and ACME built in. Records that depend on the network (A, MX, SPF, DMARC, CAA) stay in tofu. |
| Nextcloud's code from the image on every start | No volume on a node and no PHP over the network; `config.php` and files are on the Storage Box. |
| CloudNativePG with the Barman Cloud plugin | The built-in object-store backup is removed from CloudNativePG 1.32. |
| Release tags + Renovate instead of commit pins | Readable versions and changelogs; Renovate pins them like any dependency, no own pin tooling. |
| Big changes as stacked PRs, hotfixes alone | A stack merges at once: one release per feature; a fix ships on its own. |
| Automatic revert of failed deploys | Working alone: a broken release must not wait for a person. |
| One `docs` repository | One place for people and agents; app repos keep only what is about their code. |
| Public repositories | Branch protection and environments are free; secrets are only ever in SOPS. |
| No staging in the cluster | Memory; tests and the smoke suite cover what staging did. |
| Monitoring not highly available | Memory; a dead man's switch reports when it is gone. |
