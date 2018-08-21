from functools import partial
from random import random
import threading
from datetime import datetime, timedelta
import time

from bokeh.models import ColumnDataSource
from bokeh.plotting import curdoc, figure

from tornado import gen
from pythonosc import osc_server
from pythonosc import dispatcher

ROLLOVER = 1000

@gen.coroutine
def update(source, x, pressure):
    source.stream(dict(x=[x], pressure=[pressure]), rollover=ROLLOVER)


def schedule_update(doc, source, path, pressure, pressure_d, pressure_a):
    x = datetime.now()
    # but update the document from callback
    doc.add_next_tick_callback(
        partial(
            update,
            source=source,
            x=x,
            pressure=pressure,
        )
    )


def main():
    # this must only be modified from a Bokeh session callback
    source = ColumnDataSource(data=dict(x=[datetime.now()], pressure=[0]))

    # This is important! Save curdoc() to make sure all threads
    # see the same document.
    doc = curdoc()

    p = figure(x_axis_type='datetime')
    l = p.line(x='x', y='pressure', source=source)

    doc.add_root(p)

    disp = dispatcher.Dispatcher()
    # This will print all parameters to stdout.
    disp.map("/filter", partial(schedule_update, doc, source))
    server = osc_server.BlockingOSCUDPServer(("localhost", 10000), disp)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()
    #server.shutdown()

    #thread = Thread(target=blocking_task, args=(doc, source))
    #thread.start()


main()
