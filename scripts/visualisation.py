from functools import partial
from random import random
from threading import Thread
from datetime import datetime, timedelta
import time

from bokeh.models import ColumnDataSource
from bokeh.plotting import curdoc, figure

from tornado import gen

# this must only be modified from a Bokeh session callback
source = ColumnDataSource(data=dict(x=[datetime.now()], pressure=[0]))

# This is important! Save curdoc() to make sure all threads
# see the same document.
doc = curdoc()

@gen.coroutine
def update(x, pressure):
    source.stream(dict(x=[x], pressure=[pressure]), rollover=100)

def blocking_task():
    while True:
        # do some blocking computation
        time.sleep(0.1)
        y = random()
        x = datetime.now()
        # but update the document from callback
        doc.add_next_tick_callback(partial(update, x=x, pressure=y))

p = figure(x_axis_type='datetime')
l = p.line(x='x', y='pressure', source=source)

doc.add_root(p)

thread = Thread(target=blocking_task)
thread.start()
