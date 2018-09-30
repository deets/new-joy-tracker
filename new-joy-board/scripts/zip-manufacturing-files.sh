#!/usr/bin/env python3
# -*- mode: python -*-
import os
import sys
import zipfile
import glob

BASE = os.path.join(os.path.dirname(__file__), "..")
GLOBS = "*.gbr", "*.drl"

def main():
    os.chdir(BASE)
    with zipfile.ZipFile("new-joy-board.zip", "w") as outf:
        for g in GLOBS:
            for name in glob.glob(g):
                outf.write(name)
                print(name)


if __name__ == '__main__':
    main()
