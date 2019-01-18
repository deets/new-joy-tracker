from functools import partial
from random import random
import threading
from datetime import datetime, timedelta
import time

from bokeh.models import ColumnDataSource
from bokeh.plotting import curdoc, figure
from bokeh.layouts import column

from tornado import gen
from pythonosc import osc_server
from pythonosc import dispatcher

from surface3d import Surface3d

ROLLOVER = 100


class BoardInfo:
    # the names of the columns
    # per OSC packet. The name is special,
    # it's of course not displayed in every update.
    COLUMNS = ["name", "packet_diff"]

    HEIGHT = 250

    def __init__(self, name, layout):
        self._layout = layout
        self._name = name
        self._setup = False

    @gen.coroutine
    def update(self, when, *args):
        self._setup_figures(args)
        data = { k: [v] for k, v in zip(self.COLUMNS[1:], args)}
        data["x"] = [when]
        self._source.stream(data, rollover=ROLLOVER)


    def _setup_figures(self, args):
        if self._setup:
            return
        self._setup = True

        data = dict(
            x=[datetime.now()],
        )

        for column, value in zip(self.COLUMNS[1:], args): # skip name
            data[column] = [value]

        self._source = ColumnDataSource(
            data=data,
        )


        p = figure(x_axis_type='datetime', y_axis_label="{} packet_diff".format(self._name), height=self.HEIGHT)
        p.circle(x='x', y="packet_diff", source=self._source)
        self._layout.children.append(p)


def schedule_update(
        doc, clients, layout,
        # All following arguments are from the OSC package
        path,
        *args
        ):
    if path not in clients:
        clients[path] = BoardInfo(path, layout)

    # update the document from callback
    doc.add_next_tick_callback(
        partial(clients[path].update, *args)
    )


def main():
    # this must only be modified from a Bokeh session callback

    # This is important! Save curdoc() to make sure all threads
    # see the same document.
    doc = curdoc()
    layout = column(children=[], sizing_mode='stretch_both')
    doc.add_root(layout)
    clients = {}
    disp = dispatcher.Dispatcher()
    disp.map("/*", partial(schedule_update, doc, clients, layout))
    server = osc_server.BlockingOSCUDPServer(("localhost", 11111), disp)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()


main()
