# Inviting someone

1. **Account in the SSO.** On `users.int.bulbashenko.com`: create the person, give them the groups they need
   (`infra-admins` for the cluster's admin UIs, `vpn-users` for the mesh, `cloud-users`, `mail-users`, ...), issue a
   recovery link and code and hand them over in person. They set a password, a passkey and an authenticator app.
2. **The mesh.** With `vpn-users`, they install Tailscale and run
   `tailscale up --login-server https://hs.bulbashenko.com`; signing in goes through the SSO. Then
   `*.int.bulbashenko.com` (Grafana, Flux, logs, Goldilocks, mail admin, people admin) opens for them.
3. **GitHub.** Add them to the organization cglc-main. Pull requests need the required checks; merging into `infra`
   applies to production.
4. **Secrets** (only if they must edit them): add their age public key to `.sops.yaml` in infra and run
   `sops updatekeys` on every `*.sops.*` file ([operations/secrets.md](operations/secrets.md)).
5. **kubectl** (only if needed): the API (port 6443) is closed to the internet and reachable through the mesh, with
   a kubeconfig from a node (`/etc/rancher/k3s/k3s.yaml`, with `server: https://100.64.0.1:6443`, a node's tailnet
   address).
