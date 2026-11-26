# Initial release

Building the whole platform from nothing, once: the repositories exist and validate, then the nodes are rebuilt and
Flux brings everything up in order. Later changes go through [delivery.md](../delivery.md).

## 0. Before (the owner)

- The GitHub organization `cglc-main` and the GitHub App `cglc-auto-bot` (permissions: contents, pull requests, statuses,
  actions, issues, workflows; installed on all repositories). Organization variable `BOT_APP_ID`, secret
  `BOT_PRIVATE_KEY`.
- Tokens: Hetzner Cloud (read/write), a second one for keepalived; Cloudflare (DNS edit and rulesets on the three
  zones); Backblaze B2 (bucket and key); Telegram bot and chat; healthchecks.io check.
- **Data of the cluster that runs now.** Rebuilding the nodes and cleaning the Storage Box erases it. Decide first
  what moves over (mail, Nextcloud files, databases) and copy it out.

## 1. Repositories

1. Fill the secrets: every `@@NAME@@` in infra (`grep -rn '@@' infra`), then `sops -e -i` each `*.sops.*` file
   ([secrets.md](secrets.md)). `tofu/secrets.sops.json` holds OpenTofu's.
2. Push `docs`, `.github`, `infra`, `auth`, `bulbashenko.com`. In each: branch protection on `main` (required checks,
   squash only, auto-merge allowed), Dependabot alerts, secret scanning with push protection. In infra: the
   Environment `production` with a required reviewer, and the secrets `tofu.yml` reads.
3. First releases: merge a `feat:` PR (or re-run `release`) in auth and the site → `v1.0.0` and its images. Set
   `pins.env` to those versions.

## 2. Hetzner and Cloudflare

1. Storage Box: list what is on it, confirm, clean it; sub-accounts `nextcloud` and `stalwart` with SMB, snapshots
   every night ([storage-box.md](storage-box.md)).
2. `sops exec-env tofu/secrets.sops.json 'tofu -chdir=tofu apply'`: network, firewall, rDNS, DNS, redirects.
   Remove leftover records of the old cluster in the zone (old AAAA, DKIM, SRV) — tofu does not touch records it
   does not own.

## 3. Nodes, one at a time

For cglc-1, then cglc-2, then cglc-3 ([rebuild-node.md](rebuild-node.md)):

```sh
hcloud server poweroff cglc-N
hcloud server add-to-placement-group cglc-N --placement-group cluster
sops exec-env tofu/secrets.sops.json 'tofu -chdir=tofu output -json cloud_init' | jq -r '."cglc-N"' > /tmp/cglc-N.yaml
hcloud server rebuild cglc-N --image debian-13 --user-data-from-file /tmp/cglc-N.yaml
shred -u /tmp/cglc-N.yaml
```

Wait until `kubectl get nodes` shows the node Ready before the next one.

## 4. Flux

The API (6443) is closed to the internet and the mesh comes later (step 5), so until then kubectl goes through an SSH
tunnel to cglc-1. k3s's certificate already covers `127.0.0.1`, the address in its kubeconfig.

```sh
ssh root@<cglc-1 public IP> cat /etc/rancher/k3s/k3s.yaml > ~/.kube/cglc.yaml && chmod 600 ~/.kube/cglc.yaml
ssh -fN -L 6443:127.0.0.1:6443 root@<cglc-1 public IP>
export KUBECONFIG=$HOME/.kube/cglc.yaml   # fish: set -gx KUBECONFIG $HOME/.kube/cglc.yaml
```

From the `infra` repository (the same version as in `clusters/prod/flux-system/flux-operator.yaml`, so Flux takes
over the release without changing it):

```sh
kubectl create namespace flux-system
# The cluster's age key only (the AGE-SECRET-KEY line under "# cglc-main" in ~/.config/sops/age/keys.txt).
grep -A3 '^# cglc-main' ~/.config/sops/age/keys.txt | grep '^AGE-SECRET-KEY' \
  | kubectl -n flux-system create secret generic sops-age --from-file=age.agekey=/dev/stdin
helm install flux-operator oci://ghcr.io/controlplaneio-fluxcd/charts/flux-operator -n flux-system --version <version>
kubectl -n flux-system apply -f clusters/prod/flux-system/flux-instance.yaml
```

From then on Flux manages the operator and itself (`clusters/prod/flux-system/`).

Flux then applies everything in order (`clusters/prod/layers.yaml`). Watch with `flux get kustomizations -A`.

## 5. The two steps that need a person

1. **The mesh.** `kubectl -n headscale exec deploy/headscale -- headscale users create nodes`, then
   `... headscale preauthkeys create --user nodes --expiration 1h`, and on each node in order (cglc-1, cglc-2,
   cglc-3, so they get 100.64.0.1–3): `tailscale up --login-server https://hs.bulbashenko.com --authkey <key>`.
   Then your own device (signs in through the SSO once the next step is done). Set the repository variable
   `SSH_FROM_MESH_ONLY=true` and apply tofu: SSH closes to the internet.
2. **The first person**: `kubectl -n auth exec -it deploy/sso-ui -- node scripts/bootstrap-admin.mjs <username>
   <email> "<Name>"`, then on the link: password, passkey, authenticator app, recovery codes
   ([contracts/auth.md](../contracts/auth.md)).

## 6. Checks

- `flux get all -A`: everything Ready; both smoke Jobs passed; `kubectl cnpg status pg -n data`: WAL archived.
- Delivery end to end: a `fix:` PR in auth → release → Renovate PR in infra → deploy → commit status and Telegram.
  Then a release whose smoke test fails → the revert PR merges itself.
- Each node powered off in turn: the Floating IP moves, Stalwart/Headscale/Nextcloud start elsewhere, Postgres fails
  over ([lost-node.md](lost-node.md)).
- Postgres restored from B2 into a scratch cluster ([restore.md](restore.md)).
- Mail: a message to an outside mailbox passes SPF, DKIM, DMARC; `mail-tester.com` scores 10.
- `*.int.bulbashenko.com` opens from the mesh and not from the internet. `bulbashenko.dev` and `cglc.eu` redirect.
