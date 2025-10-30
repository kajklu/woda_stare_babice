import config
from math import ceil

class Household:
    def __init__(self,town,street,table_consumption,town_hall_average,population,number=None):
        self.number = number
        self.town = town
        self.street = street
        try:
            self.population = int(population)
        except ValueError:
            self.population = 0

        self.table_consumption = table_consumption
        self.town_hall_average = town_hall_average


        self.consumption = 0.0
        self.yearly_consumption = 0.0
        self.mean = 0.0


        self.consider_flag = True
        self.apply_globals()
        self.category = self.population
        self.apply_grouping()

    def apply_globals(self):
        if config.use_town_hall_averages:
            self.yearly_consumption = self.town_hall_average * self.population * 12
        else:
            self.yearly_consumption = self.table_consumption

        if config.reject_non_yearly_consumption_values:
            try:
                if round(self.table_consumption/self.town_hall_average/self.population) != 12:
                    self.consider_flag = False
            except ZeroDivisionError:
                pass

        if self.consider_flag:
            if self.yearly_consumption < 0 and config.reject_negative_consumption_values:
                self.consider_flag = False
            elif self.yearly_consumption == 0 and config.reject_zero_consumption_values:
                self.consider_flag = False

        self.consumption = self.yearly_consumption / config.get_divider()
        try:
            self.mean = self.consumption / self.population if self.population != 0 else 0
        except TypeError:
            self.mean = 0
        except ZeroDivisionError:
            self.mean = 0

    def is_overusage(self,threshold):
        if self.mean > threshold:
            return True
        return False

    def count_missing_people(self,threshold):
        missing_in_household = 0
        if self.is_overusage(threshold):
            missing_in_household = ceil(self.consumption / threshold - self.population)
        return missing_in_household

    def apply_grouping(self):
        if config.group_household_types:
            if self.population in ('Gmina', 1, 2, 3, 4, 5):
                self.category = self.population
            elif self.population in range(6, 11):
                self.category = '6-10'
            elif self.population in range(11, 26):
                self.category = '11-25'
            elif self.population in range(26, 51):
                self.category = '26-50'
            elif self.population in range(51, 101):
                self.category = '51-100'
            else:
                self.category = '100 +'
