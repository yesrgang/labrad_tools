from conductor_device.conductor_parameter import ConductorParameter

class ImagePath(ConductorParameter):
    priority = 3

    def update(self):
        experiment_name = self.conductor.experiment_name
        experiment_number = self.conductor.experiment_number
        point_number = self.conductor.point_number
        if ((experiment_name is not None) and (experiment_number is not None) 
                and (point_number is not None)):
            record_name = '{}-images#{}-{}'.format(experiment_name, 
                    experiment_number, point_number)
        else:
            record_name = ''

        self.value = record_name
