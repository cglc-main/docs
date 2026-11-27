# Headscale — the mesh

`hs.bulbashenko.com`: the control server of the tailnet (WireGuard, Tailscale clients). The cluster's admin UIs on
`*.int.bulbashenko.com` answer only to tailnet addresses.

- **Runs:** namespace `headscale`, one replica, tier-1 (`infra/clusters/prod/apps/headscale/`). The mesh keeps
  working while it is down; only joining and changes wait.
- **Data:** SQLite in an emptyDir; Litestream streams it to B2 and restores it on start, on any node. The server's
  Noise key is in the Secret `headscale`, so clients keep trusting it after a move.
- **B2 transaction cap:** Litestream's L0 check and compaction intervals are raised (`litestream.yml`) to keep its
  LIST calls under B2's daily Class C cap. If the cap is hit anyway, the `restore` init container fails with
  `403 Transaction cap exceeded` and the pod waits in Init until B2 resets caps at 00:00 UTC (Flux alerts on `apps`).
  Fix: raise the cap in B2 → Caps & Alerts.
- **Sign-in** through the SSO (group `vpn-users`). Relays: Tailscale's public DERP servers (used only when two
  devices cannot connect directly; traffic stays end-to-end encrypted).
- **Addresses** are handed out in order: the three nodes are 100.64.0.1–3 (`tofu/dns.tf` points `*.int` there).
- **Join a device:** `tailscale up --login-server https://hs.bulbashenko.com`.
- **Admin:** `kubectl -n headscale exec deploy/headscale -- headscale nodes list` (users, preauthkeys, ...).
