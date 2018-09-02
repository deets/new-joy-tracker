#!/usr/bin/env python3.6
# -*- mode: python -*-
import os
import subprocess

vis_app = os.path.join(os.path.dirname(__file__), "visualisation")
assert os.path.exists(vis_app), vis_app

subprocess.run(["bokeh", "serve", "--show", vis_app])
