# A node is down

Nothing to do in the first minutes ([architecture.md](../architecture.md), "High availability"):
- the Floating IP moves to a node with a healthy Traefik within seconds;
- after ~1 minute the node's pods start elsewhere; Postgres's replica becomes primary;
- monitoring (tier-3) may be evicted for lack of memory: Telegram still gets the dead man's switch.

Then:
1. Hetzner console: is the server running? A reboot often fixes a hung one.
2. If it is gone for good: [rebuild-node.md](rebuild-node.md). Postgres recreates its second instance on its own
   once the node is back (or `kubectl cnpg destroy pg <instance> -n data` to make it rebuild elsewhere).
3. Two nodes down: etcd has no quorum, the API is read-only. Bring one back; if impossible, restore etcd from its
   snapshot in B2 on a single node ([restore.md](restore.md)).
