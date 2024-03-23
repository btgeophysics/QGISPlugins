#!/usr/bin/env python3

import sys
import socket
import selectors
import traceback

try:
    import libclient
except:
    from BTClient import libclient




def create_request(action, value):
    # import pdb; pdb.Pdb().set_trace()
    if action == "search":
        return dict(
            type="text/json",
            encoding="utf-8",
            content=dict(action=action, value=value),
        )
    elif action == "command":
        return dict(
            type="text/json",
            encoding="utf-8",
            content=dict(action=action, value=value),
        )
    else:
        return dict(
            type="binary/custom-client-binary-type",
            encoding="binary",
            content=bytes(action + value, encoding="utf-8"),
        )


def start_connection(host, port, request, sel):
    addr = (host, port)
    print(f"Starting connection to {addr}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    message = libclient.Message(sel, sock, addr, request)
    sel.register(sock, events, data=message)

def start_request(host = '127.0.0.1', port = 12345, action='command', value='{"atest":"test"}'):
    # if len(sys.argv) != 5:
    #     print(f"Usage: {sys.argv[0]} <host> <port> <action> <value>")
    #     sys.exit(1)

    # host, port = sys.argv[1], int(sys.argv[2])
    # host = '127.0.0.1'

    # action, value = sys.argv[3], sys.argv[4]
    request = create_request(action, value)
    sel = selectors.DefaultSelector()
    start_connection(host, port, request, sel)

    


    try:
        while True:
            events = sel.select(timeout=1)
            for key, mask in events:
                message = key.data
                try:
                    message.process_events(mask)
                except Exception:
                    print(
                        f"Main: Error: Exception for {message.addr}:\n"
                        f"{traceback.format_exc()}"
                    )
                    message.close()
            # Check for a socket being monitored to continue.
            if not sel.get_map():
                break
    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")
    finally:
        sel.close()

if __name__ == "__main__":
    start_request(value='{"type":"setExtent","xmin":531650.35,"ymin":5056753.49,"xmax":531680.35,"ymax":5056793.49}')