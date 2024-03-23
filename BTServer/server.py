#!/usr/bin/env python3

import sys
import socket
import selectors
import traceback
import json

from BTServer import libserver
from PyQt5.QtCore import QObject, QThread, pyqtSignal

class ServerWorker(QObject):
    finished = pyqtSignal()
    cmdevt = pyqtSignal(object)
    running = False  # Flag to control the server loop

    def __init__(self):
        super().__init__()
        self.lsock = None  # Listening socket
        self.sel = selectors.DefaultSelector()  # Initialize the selector here

    def accept_wrapper(self, sock):
        conn, addr = sock.accept()  # Should be ready to read
        print(f"Accepted connection from {addr}")
        conn.setblocking(False)
        message = libserver.Message(self.sel, conn, addr)  # Use the instance's selector
        self.sel.register(conn, selectors.EVENT_READ, data=message)

    def run(self):
        """Server process"""
        self.start()

    def start(self, host='127.0.0.1', port=12345):
        self.running = True
        self.sel = selectors.DefaultSelector()  # Reinitialize the selector on start
        self.lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.lsock.bind((host, port))
        self.lsock.listen()
        print(f"Listening on {(host, port)}")
        self.lsock.setblocking(False)
        self.sel.register(self.lsock, selectors.EVENT_READ, data=None)

        try:
            while self.running:
                events = self.sel.select(timeout=1)  # Allow loop to check the running flag
                for key, mask in events:
                    if key.data is None:
                        self.accept_wrapper(key.fileobj)
                    else:
                        message = key.data
                        try:
                            message.process_events(mask)
                            self.cmdevt.emit(message.payload)  # Assume this emits correctly formatted data
                        except Exception as e:
                            print(f"Error: Exception for {message.addr}:\n{traceback.format_exc()}")
                            message.close()
        except KeyboardInterrupt:
            print("Caught keyboard interrupt, exiting")
        finally:
            self.sel.close()  # Close the selector
            if self.lsock:
                self.lsock.close()  # Close the listening socket
            self.sel = selectors.DefaultSelector()  # Reset the selector for future starts

    def stop(self):
        self.running = False  # Signal the server to stop

if __name__ == "__main__":
    worker = ServerWorker()
    # You may need additional logic to start and stop the worker properly when running as a script
    worker.run()
