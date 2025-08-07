import config


class Household:
    def __init__(self,town,street,population,water_consumption):
        self.town = town
        self.street = street
        try:
            self.population = int(population)
        except ValueError:
            self.population = 0
        try:
            self.water_consumption = float(water_consumption)
        except ValueError:
            self.water_consumption = 0
        self.consider_flag = True
        self.apply_globals()
    def apply_globals(self,divider=config.divider, reject_zero_consumption_flag=config.reject_zero_consumption_values, reject_negative_consumption_flag = config.reject_negative_consumption_values):

        if self.water_consumption < 0 and reject_negative_consumption_flag:
            self.consider_flag = False
        elif self.water_consumption == 0 and reject_zero_consumption_flag:
            self.consider_flag = False

        self.water_consumption = self.water_consumption / divider