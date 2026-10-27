# D-Bus policy (placeholder)

ARCHITECTURE.md §5.1 specifies a D-Bus system-bus control plane (`org.pocketmate.*`).
v0.4.0 ships an equivalent **Unix-socket RPC** (`pocketmate/ipc/rpc.py`, sockets in `/run/pm/*.sock`,
mode 0660 group `pm`) so services can be developed and tested without a bus. See STATUS.md.

`org.pocketmate.conf` below is the policy to install if/when the control plane moves to D-Bus. It is not
used by the current code.
