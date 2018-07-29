#!/usr/bin/env python3.6
# -*- mode: python -*-
import os
import sys
import argparse
import subprocess
import hashlib

SRC_DIR = os.path.join(os.path.dirname(__file__), "../src")
TAG_DIR = "/tmp"

def hash_file(path):
    content_sum = hashlib.md5()
    with open(path, "rb") as inf:
        content_sum.update(inf.read())
    return content_sum.hexdigest()


def get_tag_path(path):
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


def collect_files(src_dir, force=False):
    def take_file(name):
        full_path = os.path.join(src_dir, name)
        return name.endswith(".py") and (force or changed(full_path))

    return [os.path.join(src_dir, name)
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
        default="/dev/ttyUSB0",
        help="USB serial port to use.",
    )
    opts = parser.parse_args()
    files = collect_files(SRC_DIR, opts.force)
    for file in files:
        publish(file, opts.port)

if __name__ == '__main__':
    main()
