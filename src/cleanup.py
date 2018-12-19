import os


def full_cleanup(path=""):
    """
    Recursively cleans up all files
    known to the system. Including itself ;)
    """
    for name, type_, _, _ in os.ilistdir(path):
        full_path = path + "/" + name
        print(full_path)
        if type_ == 16384:
            full_cleanup(full_path)
            os.rmdir(full_path)
        else:
            os.remove(full_path)
