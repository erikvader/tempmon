import socket
import pickle
# pylint: disable=relative-beyond-top-level
from . import ADR

def _query(opcode, args):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM | socket.SOCK_CLOEXEC) as sock:
        sock.connect(ADR)

        with sock.makefile("wb") as f:
            pickle.dump((opcode, args), f)

        sock.shutdown(socket.SHUT_WR)

        with sock.makefile("rb") as f:
            msg = pickle.load(f)

        sock.shutdown(socket.SHUT_RD)

    return msg

def put(degrees):
    return _query("put", degrees)[1]

def get(year, month, day):
    return _query("get", (year, month, day))[1]
