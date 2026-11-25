# Rebuilding a node

A node is replaced by a fresh Debian 13 with the same name and addresses; it rejoins the cluster on its own.

1. Drain it: `kubectl drain cglc-N --ignore-daemonsets --delete-emptydir-data`.
2. Remove it from etcd and the cluster: `kubectl delete node cglc-N` (the other servers keep quorum).
3. Rebuild (commands in [initial-release.md](initial-release.md), step 3). Only the first node is special
   (`cluster-init`): rebuilding cglc-1 later joins it like the others (set `first_node` in `tofu/nodes.tf` to
   another node first).
4. In the mesh: `tailscale up --login-server https://hs.bulbashenko.com --authkey <key>` (a new key, as in
   initial-release.md step 5); delete the old machine in Headscale (`headscale nodes delete`).
