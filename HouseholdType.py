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


def covariance(x, y):
    if type(x) != list or type(y) != list or len(x) != len(y):
        return 0
    mean_x = mean(x)
    mean_y = mean(y)
    cov = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(len(x))) / len(x)
    return cov

def pearson_correlation(x, y):
    if type(x) != list or type(y) != list or len(x) != len(y):
        return 0
    cov = covariance(x, y)
    stdev_x = stdev(x)
    stdev_y = stdev(y)
    if stdev_x == 0 or stdev_y == 0:
        return 0
    return cov / (stdev_x * stdev_y)

def weighted_mean(values, weights):
    total_weight = sum(weights)
    if total_weight == 0:
        return 0
    return sum(v * w for v, w in zip(values, weights)) / total_weight


def weighted_stdev(values, weights):
    total_weight = sum(weights)
    if total_weight == 0:
        return 0
    mean_val = weighted_mean(values, weights)
    variance = sum(w * (v - mean_val) ** 2 for v, w in zip(values, weights)) / total_weight
    return math.sqrt(variance)


def weighted_median(values, weights):
    sorted_data = sorted(zip(values, weights), key=lambda x: x[0])
    total_weight = sum(weights)
    cumulative = 0
    for v, w in sorted_data:
        cumulative += w
        if cumulative >= total_weight / 2:
            return v
    return sorted_data[-1][0]

def weighted_mode(values, weights):
    counts = {}
    for v, w in zip(values, weights):
        counts[v] = counts.get(v, 0) + w
    return max(counts.items(), key=lambda x: x[1])[0]


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

        self.households = []

    def __str__(self):
        if self.category == 'Gmina':
            return 'Gmina'
        elif type(self.category) == int or str:
            return f"{self.category} os. w gospodarstwie"

        return None

    def json(self,round_values=False):
        if round_values:
            return {
                "category": str(self),
                "count": self.count,
                "consumption": round(self.consumption,2),
                "population": self.population,
                "mean": round(self.mean,2),
                "mode": round(self.mode,2),
                "median": round(self.median,2),
                "stdev": round(self.stdev,2)
            }
        return {
            "category": str(self),
            "count": self.count,
            "consumption": self.consumption,
            "population": self.population,
            "mean": self.mean,
            "mode": self.mode,
            "median": self.median,
            "stdev": self.stdev
        }

    def process(self):
        self.households = sorted(self.households, key=lambda x: x.consumption)
        self.count = 0
        self.consumption = 0.0
        self.population = 0

        self.mean = 0.0
        self.mode = 0.0
        self.median = 0.0
        self.stdev = 0.0

        #self.cutoff()

        values = []
        weights = []

        for household in self.households:
            values.append(household.mean)
            weights.append(household.population)
            self.consumption += household.consumption
            self.population += household.population
            self.count += 1

        self.mean = weighted_mean(values, weights)
        self.stdev = weighted_stdev(values, weights)
        self.mode = weighted_mode(values, weights)
        self.median = weighted_median(values, weights)

    def add_household(self, household):
        self.households.append(household)


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
