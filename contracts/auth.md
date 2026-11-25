# Contract: auth

What the SSO ([cglc-main/auth](https://github.com/cglc-main/auth)) needs from the cluster, and where the cluster
provides it.

`kustomization.yaml` in [cglc-main/auth](https://github.com/cglc-main/auth) is a Kustomize base, and
[cglc-main/infra](https://github.com/cglc-main/infra) deploys it into the namespace `auth`
(`clusters/prod/releases/auth.yaml`). One version, `AUTH_VERSION` in `clusters/prod/pins.env`, sets both:
- the Flux `GitRepository` on the release tag `vX.Y.Z`;
- the image tags of `ghcr.io/cglc-main/auth-ui` and `auth-e2e` (`X.Y.Z`).

How a release gets there: [delivery.md](../delivery.md).

**What the cluster must provide:**
- The Gateway `traefik/main`, which terminates TLS for `*.bulbashenko.com` and `*.int.bulbashenko.com`. Routes
  attach Traefik middlewares as `ExtensionRef` filters.
- The PriorityClass `tier-1`. The stack keeps running when a node is lost: two replicas of each service, spread
  over the nodes.
- Enforced NetworkPolicies. k3s enforces them.
- Monitoring in the namespace `monitoring`, if any: it may scrape Keto (port `metrics`, 4468) and Oathkeeper
  (`metrics`, 9000), both at `/metrics/prometheus`. Kratos and Hydra expose metrics only on their admin ports,
  which stay closed to other namespaces.
- The ConfigMap `internal-ca` (key `ca.crt`). This is the CA of the Postgres server certificate, mounted at
  `/etc/internal-ca`, so DSNs use `sslmode=verify-full&sslrootcert=/etc/internal-ca/ca.crt`.
- The Secret `auth`:

| Key | What it is |
|---|---|
| `KRATOS_DSN`, `HYDRA_DSN`, `KETO_DSN` | One database and role per service |
| `KRATOS_SECRETS_COOKIE`, `KRATOS_SECRETS_DEFAULT`, `KRATOS_SECRETS_PAGINATION` | Random, 32+ characters |
| `KRATOS_SECRETS_CIPHER` | Exactly 32 characters (`openssl rand -hex 16`), encrypts credential data at rest |
| `HYDRA_SECRETS_SYSTEM`, `HYDRA_SECRETS_COOKIE`, `HYDRA_SECRETS_PAGINATION` | Random, 32+ characters |
| `SMTP_CONNECTION_URI`, `SMTP_SENDER` | The mail account recovery codes come from, e.g. `smtps://noreply%40bulbashenko.com:<url-encoded password>@mail.bulbashenko.com:465/` |
| `OIDC_{SITE,HEADSCALE,FLUXWEB,GRAFANA,NEXTCLOUD,MAS}_CLIENT_SECRET` | `scripts/new-client-secret.sh`; the app gets the same value |

**What each deploy runs:**
- Kratos, Hydra and Keto run their database migrations as init containers.
- The `hydra-clients` Job makes Hydra's clients exactly the files in `ory/hydra/clients/`: it creates new ones,
  replaces changed ones and deletes the rest.
- Once the stack is ready, infra applies `deploy/smoke`: the `@smoke` tests run against production and change
  nothing. If they fail, the bot reverts the version ([delivery.md](../delivery.md)).

**The first person.** After the first deploy ([operations/initial-release.md](../operations/initial-release.md)):

```sh
kubectl -n auth exec -it deploy/sso-ui -- node scripts/bootstrap-admin.mjs <username> <email> "<Name>"
```

This puts the person in every group and prints a recovery link and code, valid for one hour. Open the link, then
on the settings page:
- set a password;
- add a passkey;
- link an authenticator app;
- save the recovery codes.

## Where infra provides it

| What | Where in cglc-main/infra |
|---|---|
| Namespace, Secret `auth`, ConfigMap `internal-ca`, VPA defaults | `clusters/prod/apps/auth/` |
| Release (GitRepository, deploy and smoke Kustomizations) | `clusters/prod/releases/auth.yaml` |
| Gateway `traefik/main`, certificate | `clusters/prod/infrastructure/configs/gateway.yaml` |
| PriorityClass `tier-1` | `clusters/prod/infrastructure/crds/priority-classes.yaml` |
| Databases and roles `kratos`, `hydra`, `keto` | `clusters/prod/infrastructure/configs/postgres/` |
| The mailbox `noreply@` (SMTP for Kratos) | `clusters/prod/apps/stalwart/plan.ndjson` |
