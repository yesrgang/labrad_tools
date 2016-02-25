from generic_signal_generator import GenericSignalGeneratorServer

if __name__ == '__main__':
    configuration_name = 'ag33522b_config'
    __server__ = GenericSignalGeneratorServer(configuration_name)
    from labrad import util
    util.runServer(__server__)
