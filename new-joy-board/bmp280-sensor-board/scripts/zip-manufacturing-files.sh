#!/usr/bin/env python3
# -*- mode: python -*-
import os
import sys
import zipfile
import glob
import pathlib

BASE = (pathlib.Path(__file__).parent / "..").absolute()
NAME = BASE.parent.parent.name

GLOBS = "*.gbr", "*.drl"

def main():
    os.chdir(BASE)
    zip_file_name = "{}.zip".format(NAME)
    print(zip_file_name)
    with zipfile.ZipFile(zip_file_name, "w") as outf:
        for g in GLOBS:
            for name in glob.glob(g):
                outf.write(name)
                print(name)


if __name__ == '__main__':
    main()
