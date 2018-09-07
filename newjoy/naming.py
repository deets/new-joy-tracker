# -*- coding: utf-8 -*-
# Copyright: 2018, Diez B. Roggisch, Berlin . All rights reserved.
import pickle
import pathlib

# 26 names to chose from
POOL = {
    "ANNA",
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
    if not id_ in MAPPING:
        if not POOL:
            raise Exception("name pool exhausted!")
        candidate = next(iter(POOL))
        POOL.remove(candidate)
        MAPPING[id_] = candidate
        save()
    return MAPPING[id_]
