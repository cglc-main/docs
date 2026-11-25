# Monitoring

One chart, victoria-metrics-k8s-stack (`infra/clusters/prod/monitoring/`), all tier-3.

| | Where |
|---|---|
| Grafana | `grafana.int.bulbashenko.com` (SSO; `infra-admins` are admins). Break-glass: `/login?disableAutoLogin`, Secret `grafana-admin`. |
| Logs (VictoriaLogs, 14 days) | `logs.int.bulbashenko.com` (UI at `/select/vmui`) |
| Requests and VPA recommendations | `goldilocks.int.bulbashenko.com` |
| Flux | `flux.int.bulbashenko.com` |
| Alerts | Telegram (Alertmanager; Flux failures directly) |

- **Alert rules** are the standard kube-prometheus ones. `Watchdog` pings healthchecks.io every minute; when the
  pings stop, healthchecks.io tells Telegram (the dead man's switch).
- **Logs for an agent or a terminal:** VictoriaLogs' CLI `vlogscli -datasource.url=https://logs.int.bulbashenko.com/select/logsql/query`
  from a device in the mesh (forward-auth needs a browser session; on a node use the Service
  `vlsingle-vm.monitoring:9428` directly). LogsQL, e.g. `_time:1h kubernetes.pod_namespace:auth error`.
