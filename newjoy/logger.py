# -*- coding: utf-8 -*-
# Copyright: 2018, Diez B. Roggisch, Berlin . All rights reserved.
import threading
import queue
import sqlite3
import datetime
from itertools import count

COMMIT_COUNT = 10

class Logger:

    def __init__(self, log_db_name):
        self._q = queue.Queue()
        t = threading.Thread(target=self._run, args=(log_db_name,))
        t.daemon = True
        t.start()


    def _run(self, log_db_name):
        conn = sqlite3.connect(
            log_db_name,
        )
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS entries ( ts TIMESTAMP NOT NULL, data BLOB NOT NULL)")
        for packet_num in count():
            ts, packet = self._q.get()
            c.execute("INSERT INTO entries (ts, data) VALUES (?, ?)", (ts, packet.dgram))
            if packet_num % COMMIT_COUNT == 0:
                conn.commit()

    def logging_callback(self, package):
        self._q.put((datetime.datetime.now(), package))
