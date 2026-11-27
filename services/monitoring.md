# Monitoring

One chart, victoria-metrics-k8s-stack (`infra/clusters/prod/monitoring/`), tier-3 except the per-node agents
(node-exporter, vlagent: `system-node-critical`) and the two stores pinned to a node by their volumes (vmsingle,
vlsingle: `tier-2`).

| | Where |
|---|---|
| Grafana | `grafana.int.bulbashenko.com` (SSO; `infra-admins` are admins). Break-glass: user `_admin` at `/login?disableAutoLogin`, Secret `grafana-admin`. |
| Our dashboards | **Health** (is anything broken; every tile green at 0) and **Resources** (memory, CPU, disk) in Grafana; JSON in `infra/clusters/prod/monitoring/dashboards/` |
| Logs (VictoriaLogs, 14 days) | `logs.int.bulbashenko.com` (UI at `/select/vmui`) |
| Requests and VPA recommendations | `goldilocks.int.bulbashenko.com` |
| Flux | `flux.int.bulbashenko.com` |
| Alerts | Telegram (Alertmanager; Flux failures directly) |

- **Alert rules** are the standard kube-prometheus ones. `Watchdog` pings healthchecks.io every minute; when the
  pings stop, healthchecks.io tells Telegram (the dead man's switch).
- **Logs for an agent or a terminal:** VictoriaLogs' CLI `vlogscli -datasource.url=https://logs.int.bulbashenko.com/select/logsql/query`
  from a device in the mesh (forward-auth needs a browser session; on a node use the Service
  `vlsingle-vm.monitoring:9428` directly). LogsQL, e.g. `_time:1h kubernetes.pod_namespace:auth error`.

## Reading memory

Resources shows memory two ways, both out of the node's physical RAM (3.74 GiB on a CX23):

- **Physical:** pods (working set) + k3s (the cgroup `k3s.service`: k3s and containerd, the number kubeReserved is
  sized by) + system (OS, kernel) + available.
- **Scheduler:** k3s reserve (`capacity − allocatable`: kubeReserved 1750Mi + eviction 100Mi) + pods' requests (set by
  VPA, native sidecars included, completed pods left out) + free for new pods.

The chart's dashboards show memory over 100 % because they divide the whole node's usage, k3s included, by
allocatable, which already excludes k3s. "Fits after losing a node?" over 100 % is what the alert
`KubeMemoryOvercommit` reports: when a node dies, the lowest tiers stay Pending.
