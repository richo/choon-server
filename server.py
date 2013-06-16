#!/usr/bin/env python

import os
import sys
import socket
import logging

def main(argv):
    if len(argv) > 1:
        port = int(argv[1])
    else:
        port = 4949

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    sock.bind(("127.0.0.1", port))
    logging.info("Bound socket on port: %i" % (port))
    sock.listen(16)
    conn, peer = sock.accept()
    logging.info("Accepted connection from: %s:%i" % peer)
    logging.warn("Dropping into debugger")
    import pdb; pdb.set_trace()


if __name__ == "__main__":
    main(sys.argv)
