# This is taken from the name.db and
# needs updating once we observe new
# boards!
import machine

MAPPING = {
    b'0\xae\xa4{\xcc\xe4': 'LANA',
    b'0\xae\xa4{\xcd\x00': 'ANNE',
    b'0\xae\xa4\x84z\xd0': 'BERT',
    b'0\xae\xa4\x8b\x8d\xf4': 'YVES',
    b'0\xae\xa4\x8b\xd9\xe0': 'IRIS',
    b'\xb4\xe6-\x94[]': 'PAUL',
    b'\xb4\xe6-\x96"-': 'NILS',
    b'\xb4\xe6-\x963\xc1': 'JANA',
    b'\xb4\xe6-\x966\x15': 'DANA',
    b'\xb4\xe6-\xb22\xb5': 'GINA',
    b'\xb4\xe6-\xbfB\xa1': 'WOUT',
    b'\xb4\xe6-\xbf\xda\xb5': 'OTTO'
}


def get_name():
    return MAPPING[machine.unique_id()]


def get_pipe_id(name=None):
    if name is None:
        id_ = machine.unique_id()
    else:
        for key, value in MAPPING.items():
            if value == name:
                id_ = key
                break
        else:
            raise Exception("No id for name {} found".format(name))

    return id_[:5]
