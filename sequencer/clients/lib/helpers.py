from itertools import chain

class ConfigWrapper(object):
    def __init__(self, **config_entries):
        self.__dict__.update(config_entries)

def merge_dicts(*dictionaries):
    merged_dictionary = {}
    for d in dictionaries:
        merged_dictionary.update(d)
    return merged_dictionary

def get_sequence_parameters(x):
    """ determine which parameters we need to get from conductor or db """
    if type(x).__name__ in ['str', 'unicode'] and x[0] == '*':
        return [x]
    elif type(x).__name__ == 'list':
        return list(chain.from_iterable([get_sequence_parameters(xx) for xx in x]))
    elif type(x).__name__ == 'dict':
        return list(chain.from_iterable([get_sequence_parameters(v) for v in x.values()]))
    else:
        return []

def substitute_sequence_parameters(x, parameter_values):
    if type(x).__name__ in ['str', 'unicode']:
        if x[0] == '*':
            return parameter_values[x]
        else:
            return x
    elif type(x).__name__ == 'list':
        return [substitute_sequence_parameters(xx, parameter_values) for xx in x]
    elif type(x).__name__ == 'dict':
        return {k: substitute_sequence_parameters(v, parameter_values) for k, v in x.items()}
    else:
        return x
