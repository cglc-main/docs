# Rebuilding a node

A node is replaced by a fresh Debian 13 with the same name and addresses; it rejoins the cluster on its own.

1. Drain it: `kubectl drain cglc-N --ignore-daemonsets --delete-emptydir-data`.
2. Remove it from etcd and the cluster: `kubectl delete node cglc-N` (the other servers keep quorum).
3. Rebuild (commands in [initial-release.md](initial-release.md), step 3). Only the first node is special
   (`cluster-init`): rebuilding cglc-1 later joins it like the others (set `first_node` in `tofu/nodes.tf` to
   another node first).
4. Back into the mesh at the same address 100.64.0.N (k3s's `tls-san` and the `*.int` records expect it):
   delete the old machine in Headscale (`headscale nodes delete`), then restart Headscale
   (`kubectl -n headscale rollout restart deploy/headscale`). Headscale hands out addresses after the last one it
   gave, and only a restart makes it start again from the lowest free one. Then on the node
   `tailscale up --login-server https://hs.bulbashenko.com --authkey <key> --accept-dns=false` (a new key, as in
   [initial-release.md](initial-release.md) step 5) and check `tailscale ip -4`.
