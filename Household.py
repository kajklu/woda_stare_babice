import config


class Household:
    def __init__(self,town,street,consumption,population):
        self.town = town
        self.street = street
        try:
            self.population = int(population)
        except ValueError:
            self.population = 0
        try:
            self.consumption = float(consumption)
        except ValueError:
            self.consumption = 0

        try:
            self.mean = self.consumption / self.population if self.population != 0 else 0
        except TypeError:
            self.mean = 0

        self.consider_flag = True
        self.apply_globals()
    def apply_globals(self):

        if self.consumption < 0 and config.reject_negative_consumption_values:
            self.consider_flag = False
        elif self.consumption == 0 and config.reject_zero_consumption_values:
            self.consider_flag = False

        self.consumption = self.consumption / config.divider
        self.mean = self.mean / config.divider