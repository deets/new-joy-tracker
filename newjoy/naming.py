# -*- coding: utf-8 -*-
# Copyright: 2018, Diez B. Roggisch, Berlin . All rights reserved.
import pickle
import pathlib

# 26 names to chose from
POOL = {
    "ANNE",
    "BERT",
    "CARL",
    "DANA",
    "ENNO",
    "FIPS",
    "GINA",
    "HANS",
    "IRIS",
    "JANA",
    "KARL",
    "LANA",
    "MONA",
    "NILS",
    "OTTO",
    "PAUL",
    "QBRT",
    "RALF",
    "SINA",
    "TIMO",
    "ULLI",
    "VERA",
    "WOUT",
    "XENO",
    "YVES",
    "ZVEN",
}


MAPPING = {}

DB = pathlib.Path(__file__).parent / "names.db"

LOADED = False


def load():
    global LOADED, POOL, MAPPING
    if LOADED:
        return
    LOADED = True
    if DB.exists():
        with DB.open("rb") as inf:
            try:
                POOL, MAPPING = pickle.load(inf)
            except:
                pass


def save():
    with DB.open("wb") as outf:
        pickle.dump((POOL, MAPPING), outf)


def resolve(id_):
    load()
    if id_ not in MAPPING:
        if not POOL:
            raise Exception("name pool exhausted!")
        candidate = next(iter(POOL))
        POOL.remove(candidate)
        MAPPING[id_] = candidate
        save()
    return MAPPING[id_]


if __name__ == '__main__':
    import pprint
    load()
    pprint.pprint(MAPPING)
    #print(resolve(b'0\xae\xa4\x84\xc8\x88')
    msb_ids = set(id_[:5] for id_ in MAPPING.keys())
    if len(msb_ids) == len(MAPPING):
        print("All msb ids are unique")
    #print(msb_ids)
