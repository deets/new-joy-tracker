from functools import partial
from random import random
import threading
from datetime import datetime, timedelta
import time

from bokeh.models import ColumnDataSource
from bokeh.plotting import curdoc, figure
from bokeh.layouts import layout


from tornado import gen
from pythonosc import osc_server
from pythonosc import dispatcher

ROLLOVER = 1000

@gen.coroutine
def update(source, **kw):
    item = dict((k, [v]) for k, v in kw.items())
    source.stream(item, rollover=ROLLOVER)


def schedule_update(
        doc, source, path,
        pressure,
        gyro_x,
        gyro_y,
        gyro_z,
        acc_x,
        acc_y,
        acc_z,
        packet_diff,
        ):
    x = datetime.now()
    # but update the document from callback
    doc.add_next_tick_callback(
        partial(
            update,
            source=source,
            x=x,
            pressure=pressure,
            gyro_x=gyro_x,
            gyro_y=gyro_y,
            gyro_z=gyro_z,
            acc_x=acc_x,
            acc_y=acc_y,
            acc_z=acc_z,
            packet_diff=packet_diff,
        )
    )


COLUMNS = ["pressure", "gyro_x", "gyro_y", "gyro_z", "acc_x", "acc_y", "acc_z", "packet_diff"]

GLYPH_TYPES = {
    "packet_diff": "circle",
}

def main():
    # this must only be modified from a Bokeh session callback
    data = dict(
            x=[datetime.now()],
    )
    for column in COLUMNS:
        data[column] = [0]

    source = ColumnDataSource(
        data=data,
    )

    # This is important! Save curdoc() to make sure all threads
    # see the same document.
    doc = curdoc()

    plots = {}
    for column in COLUMNS:
        p = figure(x_axis_type='datetime', y_axis_label=column)
        getattr(p, GLYPH_TYPES.get(column, "line"))(x='x', y=column, source=source)
        plots[column] = p

    l = layout([
        [plots["pressure"], plots["packet_diff"]],
        [plots["gyro_x"], plots["gyro_y"], plots["gyro_z"]],
        [plots["acc_x"], plots["acc_y"], plots["acc_z"]],
        ],
        sizing_mode='stretch_both'
    )
    doc.add_root(l)

    disp = dispatcher.Dispatcher()
    disp.map("/filter", partial(schedule_update, doc, source))
    server = osc_server.BlockingOSCUDPServer(("localhost", 10000), disp)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()

main()
