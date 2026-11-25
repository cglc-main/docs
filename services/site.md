# bulbashenko.com — the site

Public at `bulbashenko.com` (`www.` redirects). Code and the app's documentation:
[cglc-main/bulbashenko.com README](https://github.com/cglc-main/bulbashenko.com#readme). What the cluster provides
and how it deploys: [contracts/site.md](../contracts/site.md).

- **Runs:** namespace `bulbashenko-com`, two replicas, tier-1. Database `site` in `pg`.
- **Media** comes from Nextcloud's Team folder `Site` (read as the local user `site`); when Nextcloud is down, pages
  render without media.
