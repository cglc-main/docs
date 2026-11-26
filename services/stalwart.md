# Stalwart — mail

`mail.bulbashenko.com`: SMTP (25, submission 587 and 465), IMAP (993), JMAP, the account page (`/account`), and
`autoconfig.`, `autodiscover.`, `mta-sts.` of the domain. The admin UI is at `mail.int.bulbashenko.com/admin`, from
the mesh only; `/admin` on the public name redirects there.

- **Runs:** namespace `stalwart`, one replica, tier-1 (`infra/clusters/prod/apps/stalwart/`). Moves to another node
  in about a minute; senders retry meanwhile.
- **Data:** settings and mail metadata in `pg` (database `stalwart`), message bodies on the Storage Box
  (sub-account `stalwart`).
- **Configuration is code:** `plan.ndjson` (stalwart-cli plan; idempotent upserts), applied by the Job `config`
  after every change. To start from what the UI shows: `stalwart-cli snapshot <Types> --output x.ndjson`.
- **TLS and DNS:** Stalwart gets its certificate itself (ACME DNS-01 at Cloudflare) and keeps its own records
  current: DKIM (Ed25519 and RSA, rotated), MTA-STS, TLS-RPT, SRV, autoconfig. MX, SPF, DMARC, CAA are in
  `tofu/dns.tf`; `mail.` resolves through the wildcard `*.bulbashenko.com` there. Each node's address has reverse
  DNS `cglc-N.bulbashenko.com` (outgoing mail leaves from the node Stalwart runs on).
- **Ports:** Traefik passes them through with PROXY protocol v2; Stalwart listens on 2525/2587/2465/2993.
- **People** sign in through the SSO (group `mail-users`; `infra-admins` are its administrators). Phones without
  custom OAuth use an app password from the account page.
- **The web UI** signs in as the public client `stalwart-webui` (the Application's `oauthClientId` in `plan.ndjson`;
  Hydra does not support Client ID Metadata Documents). The same id exists as a Stalwart `OAuthClient` for the
  recovery administrator. `oauthScopes` stays empty: the web UI sends those scopes to Hydra, which would reject them.
- **noreply@bulbashenko.com** is a local account (password in the Secret `stalwart`) for Ory and Nextcloud.
- **Recovery administrator** `recovery` (Secret `stalwart`) is what the Job signs in as; people never use it.
