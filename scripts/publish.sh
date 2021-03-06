#!/usr/bin/env python3.6
# -*- mode: python -*-
import os
import sys
import argparse
import subprocess
import hashlib
from common import DEFAULT_SERIAL_PORT

SRC_DIR = os.path.join(os.path.dirname(__file__), "../src")
TAG_DIR = "/tmp"


def hash_file(path):
    if os.path.isdir(path):
        return "".join(
            (hash_file(os.path.join(path, name))
             for name in os.listdir(path)),
        )

    content_sum = hashlib.md5()
    with open(path, "rb") as inf:
        content_sum.update(inf.read())
    return content_sum.hexdigest()


def get_tag_path(path):
    path = os.path.normpath(path)
    tag_sum = hashlib.md5()
    tag_sum.update(path.encode("utf-8"))
    return os.path.join(
        TAG_DIR,
        "{}-{}".format(tag_sum.hexdigest(), os.path.basename(path))
    )


def changed(path):
    tag_path = get_tag_path(path)
    if not os.path.exists(tag_path):
        return True

    with open(tag_path, "r") as inf:
        old_checksum = inf.read()

    return old_checksum != hash_file(path)


def tag(path):
    tag_path = get_tag_path(path)
    with open(tag_path, "w") as outf:
        content_sum = hash_file(path)
        outf.write(content_sum)


def collect_files(src_dir, force=False, files=[]):
    def take_file(name):
        full_path = os.path.join(src_dir, name)
        return (os.path.splitext(name)[1] in (".py", ".txt")
                or os.path.basename(name) == "uosc") \
                and (force or changed(full_path)) \
                and (not files or name in files)

    return [os.path.normpath(os.path.join(src_dir, name))
            for name in os.listdir(src_dir)
            if take_file(name)
            ]


def publish(path, port):
    cmd = [
        "ampy",
        "--port", port,
        "put",
        path,
    ]
    print("publishing {}".format(path))
    subprocess.check_call(cmd)
    tag(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--force",
        default=False,
        action="store_true",
        help="Push *all* source files.",
    )
    parser.add_argument(
        "--port",
        default=DEFAULT_SERIAL_PORT,
        help="USB serial port to use.",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="List of filenames to limit publishing to",
    )
    opts = parser.parse_args()
    files = collect_files(SRC_DIR, opts.force, opts.files)
    for file in files:
        publish(file, opts.port)

if __name__ == '__main__':
    main()
