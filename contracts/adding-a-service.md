# Adding a service

Checklist for a new service in the cluster. Sign-in first (it lives in cglc-main/auth), then the cluster side.

## Sign-in
**App that supports OpenID Connect.**
1. In cglc-main/auth, add `ory/hydra/clients/<id>.json` (copy one), and list it in `kustomization.yaml` under `hydra-clients`. Set:
   - `metadata.required_group`;
   - the redirect URIs;
   - `skip_consent: true`;
   - `post_logout_redirect_uris`;
   - `backchannel_logout_uri`, if the app supports it.

   A confidential client takes `"client_secret": "${OIDC_<NAME>_CLIENT_SECRET}"`. Add that key to the Secret
   `auth` and to the `hydra-clients` Job in `deploy/ui.yaml`.
2. Configure the app with:
   - issuer `https://auth.bulbashenko.com`;
   - the client id and secret;
   - scopes `openid profile email groups`.

   Do not put forward-auth in front of it.

For an app that reads the person from the access token (like Stalwart), give the client an `audience` and
`"metadata": { "access_token_identity": true }`. Access tokens are JWTs. They carry `scope` as a string and `scp`
as a list, plus `preferred_username`, `email` and `name` at the top level. If the app maps groups to roles, list
the groups it may see in `"access_token_groups"`: the token then carries `groups` with those of them the person is
in (an empty list when none). Stalwart gets `infra-admins`, its administrators.

**App without any login.** Serve it on `<name>.int.bulbashenko.com`, and give its route three middlewares:
- `mesh-only`;
- `forward-auth` (Oathkeeper's decision API, `http://oathkeeper.auth.svc.cluster.local:4456/decisions`);
- `headers`.

In cglc-main/infra all three come from one Kustomize component, `components/int-route`: include it in the app's
namespace and attach the middlewares in that order (example: `clusters/prod/monitoring/namespace/routes.yaml`).
`*.int.bulbashenko.com` already resolves to the nodes' tailnet addresses (`tofu/dns.tf`), so no DNS change is
needed.

The rule in `ory/oathkeeper/rules.yml` lets in `infra-admins`. Browsers without a session are sent to sign in;
with the wrong group, they get 403.

**People and groups.** Manage them on the admin page at `https://users.int.bulbashenko.com`. It needs
`infra-admins`, the mesh, and a recent sign-in. On it you can:
- create a person;
- change their groups (this revokes their tokens, so new claims apply);
- end their sessions;
- issue a recovery link;
- disable or delete them.

**The local admin of a service** (break-glass) is named `_admin`. An SSO username always
starts with a letter (Kratos identity schema), so an app that maps people by `preferred_username` can never sign a
person into a local account.

## The cluster side (cglc-main/infra)

1. **A directory** `clusters/prod/apps/<name>/` with its namespace and the component `components/defaults` (VPA sets
   its requests from real usage; LimitRange). List it in `clusters/prod/apps/kustomization.yaml`.
2. **Priority:** `tier-1` if visitors or mail depend on it, nothing (tier-2) otherwise, `tier-3` for monitoring.
3. **State never on a node.** A database: a role and a database in `infrastructure/configs/postgres/` (one line each)
   and the component `components/internal-ca`. Files: a Storage Box sub-account over SMB (see
   `apps/nextcloud/namespace/storage.yaml`). A SQLite database: Litestream to B2 (see `apps/headscale/`).
4. **Secrets** in `*.sops.yaml` next to the manifests (`sops <file>`).
5. **Routes** on the Gateway `traefik/main`: listener `subdomains` for `<name>.bulbashenko.com`, `int` for admin UIs.
6. **Our own app** (a repo of cglc-main that releases images): a line in `clusters/prod/pins.env` with its
   `# renovate:` comment, and `clusters/prod/releases/<name>.yaml` like the others. Its repo calls the org's
   `release.yml` and `pr-title.yml` (copy them from cglc-main/auth). Add its Kustomizations to the Alerts in
   `clusters/prod/flux-system/notifications.yaml`.
7. **Docs:** a page in `services/`, and a contract in `contracts/` if it is our own app.
