#!/usr/bin/env python3

import sys
import socket
import selectors
import traceback
import json

from BTServer import libserver
from PyQt5.QtCore import QObject, QThread, pyqtSignal

sel = selectors.DefaultSelector()


def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    message = libserver.Message(sel, conn, addr)
    sel.register(conn, selectors.EVENT_READ, data=message)

class ServerWorker(QObject):
    finished = pyqtSignal()
    cmdevt = pyqtSignal(object)
    # progress = pyqtSignal(int)

    def run(self):
        """Server process"""
        self.start()

    def start(self, host = '127.0.0.1', port = 12345):

        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Avoid bind() exception: OSError: [Errno 48] Address already in use
        lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        lsock.bind((host, port))
        lsock.listen()
        print(f"Listening on {(host, port)}")
        lsock.setblocking(False)
        sel.register(lsock, selectors.EVENT_READ, data=None)

        try:
            while True:
                events = sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        accept_wrapper(key.fileobj)
                    else:
                        message = key.data
                        try:
                            message.process_events(mask)
                            if message.payload:
                                try:
                                    # jdat = json.loads(message.payload)
                                    # self.cmdevt.emit(jdat.update({"success":True}))
                                    self.cmdevt.emit(message.payload)
                                except:
                                    self.cmdevt.emit({"success":False})
                                    pass
                            # import pdb; pdb.Pdb().set_trace()

                        except Exception:
                            print(
                                f"Main: Error: Exception for {message.addr}:\n"
                                f"{traceback.format_exc()}"
                            )
                            message.close()
        except KeyboardInterrupt:
            print("Caught keyboard interrupt, exiting")
        finally:
            sel.close()

if __name__ == "__main__":
    ServerWorker().start()
