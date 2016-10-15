def normalize_parameters(p):
    parameters = dict(p)

    if parameters['status']: 
        del parameters['status']

    for key, value in parameters.iteritems():
        if (isinstance(value, list) and len(value) == 1):
            parameters[key] = value[0]

    return parameters
