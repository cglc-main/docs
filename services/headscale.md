# Headscale — the mesh

`hs.bulbashenko.com`: the control server of the tailnet (WireGuard, Tailscale clients). The cluster's admin UIs on
`*.int.bulbashenko.com` answer only to tailnet addresses.

- **Runs:** namespace `headscale`, one replica, tier-1 (`infra/clusters/prod/apps/headscale/`). The mesh keeps
  working while it is down; only joining and changes wait.
- **Data:** SQLite in an emptyDir; Litestream streams it to B2 and restores it on start, on any node. The server's
  Noise key is in the Secret `headscale`, so clients keep trusting it after a move.
- **Sign-in** through the SSO (group `vpn-users`). Relays: Tailscale's public DERP servers (used only when two
  devices cannot connect directly; traffic stays end-to-end encrypted).
- **Addresses** are handed out in order: the three nodes are 100.64.0.1–3 (`tofu/dns.tf` points `*.int` there).
- **Join a device:** `tailscale up --login-server https://hs.bulbashenko.com`.
- **Admin:** `kubectl -n headscale exec deploy/headscale -- headscale nodes list` (users, preauthkeys, ...).
