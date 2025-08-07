import math

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
        self.mean = float
        self.mode = float
        self.median = float
        self.stdev = float
        self.averages = []
    def __str__(self):
        if type(self.category) == int:
            return f"{self.category} os. w gospodarstwie"
        elif type(self.category) == str:
            return f"{self,type}"
        return None

    def process(self):
        self.mean = mean(self.averages)
        self.stdev = stdev(self.averages)
        self.mode = mode(self.averages)
        self.median = median(self.averages)

    def add_household(self, household):
        self.count += 1
        self.population += household.population
        self.consumption += household.consumption
        for _ in range(household.population):
            self.averages.append(household.mean)