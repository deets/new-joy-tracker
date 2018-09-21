#!/usr/bin/env python3
import sqlite3
from collections import  defaultdict
import sys

import numpy as np
from scipy.stats import norm
from bokeh.plotting import curdoc, figure, show
from bokeh.palettes import magma

num_bins = 40

db = sqlite3.connect(sys.argv[1], detect_types=sqlite3.PARSE_DECLTYPES)
c = db.cursor()
c.execute('select * from entries')
data = [(ts, packet[20:20+4]) for ts, packet in c]
parts = defaultdict(list)
for ts, name in data:
    parts[name].append(ts)
n
plot = figure()

for name, color in zip(parts, magma(len(parts))):
    nils = parts[name]
    #print(nils)
    diffs = [((b-a).microseconds // 1000) for a, b in zip(nils[:-1], nils[1:])]
    #print(diffs)

    # the histogram of the data
    counts, ranges = np.histogram(diffs, bins=num_bins, density=True)
    x_values = np.cumsum(np.diff(ranges))
    mu, sigma = norm.fit(diffs)
    x = np.linspace(x_values[0], x_values[-1], 500)
    y = norm.pdf(x, mu, sigma)
    plot.vbar(x=x_values, top=counts, width=x_values[0], alpha=.3, color=color)
    plot.line(x=x, y=y, color=color, alpha=.8)

show(plot)
