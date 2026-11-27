# Stalwart — mail

`mail.bulbashenko.com`: SMTP (25, submission 587 and 465), IMAP (993), JMAP, the account page (`/account`), and
`autoconfig.`, `autodiscover.`, `mta-sts.` of the domain. The admin UI is at `mail.int.bulbashenko.com/admin`, from
the mesh only; `/admin` on the public name redirects there, and `/` and `/account` on `mail.int` redirect to
`/admin/` and to the public account page (the SSO client lists only these two web UI addresses).

- **Runs:** namespace `stalwart`, one replica, tier-1 (`infra/clusters/prod/apps/stalwart/`). Moves to another node
  in about a minute; senders retry meanwhile.
- **Data:** settings and mail metadata in `pg` (database `stalwart`), message bodies on the Storage Box
  (sub-account `stalwart`).
- **Configuration is code:** `plan.ndjson` (stalwart-cli plan; idempotent upserts), applied by the Job `config`
  after every change. The plan ends with the action `UpdateApps`: Stalwart renders the web UI with its
  `oauthClientId` only at startup or on that action. To start from what the UI shows: `stalwart-cli snapshot <Types> --output x.ndjson`.
- **TLS and DNS:** Stalwart gets its certificate itself (ACME DNS-01 at Cloudflare) and keeps its own records
  current: DKIM (Ed25519 and RSA, rotated), MTA-STS, TLS-RPT, SRV, autoconfig. MX, SPF, DMARC, CAA are in
  `tofu/dns.tf`; `mail.` resolves through the wildcard `*.bulbashenko.com` there. Each node's address has reverse
  DNS `cglc-N.bulbashenko.com` (outgoing mail leaves from the node Stalwart runs on).
- **Ports:** Traefik passes them through with PROXY protocol v2; Stalwart listens on 2525/2587/2465/2993.
  The pod network (`10.42.0.0/16`) is an `AllowedIp` in `plan.ndjson`, so Stalwart never auto-bans kubelet's probes
  or Traefik.
- **People** sign in through the SSO (group `mail-users`; `infra-admins` are its administrators). Phones without
  custom OAuth use an app password from the account page.
- **The web UI** signs in as the public client `stalwart-webui` (the Application's `oauthClientId` in `plan.ndjson`;
  Hydra does not support Client ID Metadata Documents). The same id exists as a Stalwart `OAuthClient` for the
  recovery administrator. `oauthScopes` stays empty: the web UI sends those scopes to Hydra, which would reject them.
  Its sign-out carries no `id_token_hint`, which Hydra rejects; the auth route `stalwart-logout` (cglc-main/auth
  `deploy/routes.yaml`) drops the parameters, so the session ends and the browser lands on the SSO's sign-in page.
- **noreply@bulbashenko.com** sends the mail of Ory and Nextcloud. It signs in with an app password: the domain's
  directory is the SSO, which checks no passwords. The app password is in the Secrets of its users (auth
  `SMTP_CONNECTION_URI`, nextcloud `smtp-password`); rotation in [operations/secrets.md](../operations/secrets.md).
- **Recovery administrator** `recovery` (Secret `stalwart`) is what the Job signs in as; people never use it.
