#!/usr/bin/env python3.6
# -*- mode: python -*-
import os
import subprocess

vis_py = os.path.join(os.path.dirname(__file__), "visualisation.py")
assert os.path.exists(vis_py), vis_py

subprocess.run(["bokeh", "serve", "--show", vis_py])
