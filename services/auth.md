# auth — single sign-on

`auth.bulbashenko.com` (public), `users.int.bulbashenko.com` (admin page, mesh only). Ory Kratos, Hydra, Keto,
Oathkeeper and a Next.js UI; code and the app's own documentation (sign-in rules, groups, logout, Thunderbird):
[cglc-main/auth README](https://github.com/cglc-main/auth#readme). What the cluster provides:
[contracts/auth.md](../contracts/auth.md).

- **Runs:** namespace `auth`, two replicas of each service, tier-1. Databases `kratos`, `hydra`, `keto` in `pg`.
- **Groups** decide access to every app: `infra-admins`, `site-admins`, `mail-users`, `cloud-users`, `vpn-users`,
  `matrix-users`.
- **Mail** (recovery codes) goes out as `noreply@bulbashenko.com` through Stalwart.
- **Logs:** `logs.int.bulbashenko.com`, `{kubernetes.pod_namespace="auth"}`.
