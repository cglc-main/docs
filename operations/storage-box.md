# Storage Box

1 TB, Hetzner. One sub-account per volume, SMB 3 with encryption (`seal`), mounted by csi-driver-smb on any node:

| Sub-account | Holds | Volume |
|---|---|---|
| `nextcloud` | `data/` (the files), `state/config.php` | `apps/nextcloud/namespace/storage.yaml` |
| `stalwart` | mail bodies | `apps/stalwart/storage.yaml` |

- Create a sub-account: Hetzner console → Storage Box → Sub-accounts, SMB on, a generated password; its name
  (`uNNNNNN-subN`) and password go into the app's `storage-box` Secret and the PV's `source`.
- Snapshots: automatic, nightly, kept 14 days (console → Snapshots). They are the files' and mail's backup.
- The volumes are never pruned by Flux and use `Retain`: deleting a PV or PVC never deletes data.
