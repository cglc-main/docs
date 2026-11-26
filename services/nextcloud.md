# Nextcloud — files

`cloud.bulbashenko.com`. Official chart and image (`infra/clusters/prod/apps/nextcloud/`), tier-2.

- **Nothing on a node.** On every start the init container `prepare` lays out the image's code in an emptyDir and
  puts back `config.php` from the Storage Box; the start hook (`nextcloud.hooks.before-starting` in
  `release/nextcloud.yaml`) migrates after a new image, installs the apps (user_oidc, groupfolders), sets sign-in and
  the site's Team folder, then saves `config.php`.
  Files are on the Storage Box (`data/`). A start takes about a minute longer for it.
- **Sign-in** through the SSO (`cloud-users`); the local admin at `/login?direct=1` (Secret `nextcloud`).
- **The site's media:** Team folder `Site` (`Gallery/`, `Files/`): `site-admins` write, the local user `site` reads.
- **Cache and locks:** Valkey, no volume.
- **Upgrades:** one major at a time (Renovate groups chart and image; majors wait for a person). No rollback: fix
  forward.
- **occ:** `kubectl -n nextcloud exec deploy/nextcloud -c nextcloud -- su -s /bin/sh www-data -c 'php occ <cmd>'`.
