"""IPC (§5.1). Data plane: length-prefixed msgpack frames on Unix sockets under /run/pm/.
Control plane: D-Bus in the spec; this prototype uses the same framed socket for request/response
(`rpc.py`) so services run without a system bus. Interface names mirror org.pocketmate.* [impl]."""
