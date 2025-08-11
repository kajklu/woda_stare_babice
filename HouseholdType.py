import math
import config

def mode(values):
    if type(values) != list:
        return None
    return max(set(values), key=values.count)

def stdev(values):
    if type(values) != list or len(values) == 0:
        return 0
    variance = sum((x - mean(values)) ** 2 for x in values) / len(values)
    return math.sqrt(variance)

def median(values):
    values.sort()
    index = int(len(values) / 2)
    if type(index) != int:
        value1 = values[int(index)]
        value2 = values[int(index + 1)]
        return value1 + value2 / 2
    return values[int(index)]

def mean(values):
    if type(values) != list or len(values) == 0:
        return 0
    average = sum(values) / len(values)
    return average


class HouseholdType:
    def __init__(self, category):
        self.category = category
        self.count = 0
        self.consumption = 0.0
        self.population = 0

        self.mean = 0.0
        self.mode = 0.0
        self.median = 0.0
        self.stdev = 0.0

        self.averages = []
        self.consumptions = []
        self.households = []

    def __str__(self):
        if type(self.category) == int:
            return f"{self.category} os. w gospodarstwie"
        elif type(self.category) == str:
            return f"{self,type}"
        return None

    def process(self):
        self.cutoff()
        self.consumption = sum(self.consumptions)
        self.population = len(self.averages)

        self.mean = mean(self.averages)
        self.stdev = stdev(self.averages)
        self.mode = mode(self.averages)
        self.median = median(self.averages)

    def add_household(self, household):
        self.count += 1
        for _ in range(household.population):
            self.averages.append(household.mean)
            self.averages = sorted(self.averages)
        self.consumptions.append(household.consumption)
        self.consumptions = sorted(self.consumptions)

        self.households.append(household)
        self.households = sorted(self.households, key=lambda x: x.consumption)
        # Nie podobają mi się te sorty. Z matematyki wynika, że dane z jednego domostwa będą na jednej i drugiej liście
        # w tym samym miejscu, ale no jakoś nie przemawia to do mnie.


    def cutoff(self,lower_threshold=config.lower_cutoff_percentage,upper_threshold=config.upper_cutoff_percentage):
        start_index_averages = round(len(self.averages)*lower_threshold/100)
        end_index_averages = round(len(self.averages)*upper_threshold/100)

        start_index_consumptions = round(len(self.consumptions)*lower_threshold/100)
        end_index_consumptions = round(len(self.consumptions)*upper_threshold/100)

        self.averages = self.averages[start_index_averages:end_index_averages]
        self.consumptions = self.consumptions[start_index_consumptions:end_index_consumptions]
        self.count = len(self.consumptions)

        for i, household in enumerate(self.households):
            if i < start_index_consumptions or i >= end_index_consumptions:
                household.consumption = False
