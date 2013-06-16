#!/usr/bin/env python

import os
import sys
import errno
import socket
import logging
import select

from collections import defaultdict

peers = []
register = defaultdict(list)
reverse_register = defaultdict(list)


def terminate(conn):
    conn.shutdown(socket.SHUT_WR)
    conn.close()
    peers.pop(peers.index(conn))


def handle_disconnect(conn):
    for pebble_id in reverse_register[conn]:
        idx = register[pebble_id]
        idx.pop(idx.index(conn))
    # XXX Pretty sure this leaks
    if conn in peers:
        peers.pop(peers.index(conn))


def handle_register(data, conn):
    pebble_id = data.split(" ")[1]
    register[pebble_id].append(conn)
    reverse_register[conn].append(pebble_id)
    logging.warn("Registered %s" % pebble_id)


def handle_http(data):
    try:
        verb, path, http = data.split(" ", 2)
        _, pebble_id, action = path.split("/")
        byte = action[0]
        for conn in register[pebble_id]:
            try:
                conn.send(byte)
            except socket.error as e:
                if e.errno == errno.EBADF:
                    handle_disconnect(conn)
                else:
                    raise
    except:
        raise


def handle_incoming(data, conn):
    if data.startswith("reg "):
        handle_register(data, conn)
    elif data.startswith("POST /"):
        handle_http(data)
        terminate(conn)
    else:
        terminate(conn)


def main(argv):
    if len(argv) > 1:
        port = int(argv[1])
    elif "PORT" in os.environ:
        port = int(os.getenv("PORT"))
    else:
        port = 4949

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    sock.bind(("0.0.0.0", port))
    logging.info("Bound socket on port: %i" % (port))
    sock.listen(16)

    while True:
        r_socks = peers + [sock]
        r, _, _ = select.select(r_socks, [], [])
        for i in r:
            if i == sock:
                conn, peer = sock.accept()
                logging.info("Accepted connection from: %s:%i" % peer)
                peers.append(conn)
            else:
                data = i.recv(1024).strip()
                print ">>> %s" % data
                handle_incoming(data, i)

if __name__ == "__main__":
    main(sys.argv)
