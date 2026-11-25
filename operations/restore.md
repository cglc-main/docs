# Restoring

| What | From | How |
|---|---|---|
| Postgres (all apps' databases) | B2, `pg/` (WAL + nightly base backups, 14 days) | A new Cluster with `bootstrap.recovery` from the ObjectStore `b2` (point in time optional). Test into a scratch cluster first: copy `configs/postgres/cluster.yaml` as `pg-restore` with `bootstrap: { recovery: { source: pg } }`, `externalClusters: [{ name: pg, plugin: { name: barman-cloud.cloudnative-pg.io, parameters: { barmanObjectName: b2, serverName: pg } } }]`. |
| Headscale | B2, `headscale/` (Litestream) | Automatic on every start. A point in time: `litestream restore -timestamp <RFC3339>` in a pod with the same Secret. |
| Nextcloud files, `config.php` | Storage Box snapshots | Hetzner console → Storage Box → Snapshots, or the read-only `.zfs/snapshot/` in the share. |
| Mail bodies | Storage Box snapshots (sub-account `stalwart`); metadata with Postgres | Restore both to the same moment. |
| Cluster state (etcd) | B2, `etcd/` (every 6 h, 2 days) | On a fresh first node: `k3s server --cluster-reset --cluster-reset-restore-path=<snapshot> --etcd-s3 ...` (k3s docs, "Backup and restore"), then join the others. |
| Everything else | Git | Flux reapplies it. |
