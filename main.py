import matplotlib.pyplot as plt
import math
import config
from Household import Household
import operator


# Data file path
data_csv = 'dane_raw.csv'

# Set to True if the data is monthly, False if it is annual
monthly = True

# Method of stealing verification
overusage_threshold = 'mean+stdev' # Options: 'sigma+average', 'sigma+mode', 'sigma+median', static_value

# Rubbish handling fee
fee = 38

# Water consumption data processing parameters
reject_negative_consumption_values = True
reject_null_consumption_values = True
reject_zero_consumption_values = True

# Population data processing parameters
reject_population_with_negative_consumption = True
reject_population_with_zero_consumption = True
reject_population_with_null_consumption = True

# Display parameters
distribution_bins = 120

# Global variables for water consumption and population data
commune_population = int
commune_households = int

class HouseholdType:
    def __init__(self, type):
        self.type = type
        self.count = 0
        self.consumption = 0.0
        self.population = 0
        self.mean = float
        self.mode = float
        self.median = float
        self.stdev = float
        self.averages = []
    def __str__(self):
        if type(self.type) == int:
            return f"{self.type} os. w gospodarstwie"
        elif type(self.type) == str:
            return f"{self,type}"

    def process(self):
        self.mean = mean(self.averages)
        self.stdev = stdev(self.averages)
        self.mode = mode(self.averages)
        self.median = median(self.averages)

    def add_household(self, household):
        self.count += 1
        self.population += household['population']
        self.consumption += household['consumption']
        for _ in range(household['population']):
            self.averages.append(household['mean'])

considered = HouseholdType("Gmina")
household_types_data = []
households = []
missing_by_town = {}

if monthly:
    divider = 12
else:
    divider = 1


def load_data(data_file):
    with open(data_file, "r", encoding="utf-8") as file:
        lines = file.readlines()

    file.close()

    for line in lines:
        line.replace(',','.')
        data = line.split(';')
        
        if data[0] != '﻿Miejscowość':
            town = data[0]
            street = data[1]
            consumption = data[2].replace(',', '.')
            population = data[3].replace(',', '.')

            household = Household(town,street,consumption,population)

            if population is not None:
                households.append(household)

def print_table():
    printing_data = []

    header = f"Typ | Liczba gospodarstw uwzględnionych | Liczba osób | Całkowite zużycie w typie gospodarstw [m3] | Dominanta [m3] | Średnia [m3] | Odchylenie standardowe [m3] | Mediana [m3] "

    final_cell_length = []
    header_cells = header.split('|')
    printing_data.append(header_cells)

    for i in range(len(header_cells)):
        cell_length = len(str(header_cells[i]))
        final_cell_length.append(cell_length)

    reference = f"Gmina | {considered.count} ({round(considered.count / considered.count * 100, 2)}%) | {considered.population} ({round(considered.population / considered.population * 100)}%) | {round(considered.consumption, 2)} ({round(considered.consumption / considered.consumption * 100, 2)}%) | {round(considered.mode, 2)} | {round(considered.mean,2)} | {round(considered.stdev,2)} | {round(considered.median,2)}"

    reference_cells = reference.split('|')
    printing_data.append(reference_cells)

    for i in range(len(reference_cells)):
        cell_length = len(str(reference_cells[i]))
        if final_cell_length[i] < cell_length:
            final_cell_length[i] = cell_length

    for household_type in household_types_data:
        print_data = f"{household_type} | {household_type.count} ({round(household_type.count / considered.count * 100, 2)}%) | {household_type.population} ({round(household_type.population / considered.population * 100)}%) | {round(household_type.consumption, 2)} ({round(household_type.consumption / considered.consumption * 100, 2)}%) | {round(household_type.mode, 2)} | {round(household_type.mean, 2)} | {round(household_type.stdev, 2)} | {round(household_type.median, 2)}"
        cells = print_data.split('|')
        printing_data.append(cells)
        for i in range(len(cells)):
            cell_length = len(str(cells[i]))
            if final_cell_length[i] < cell_length:
                final_cell_length[i] = cell_length

    for i in range(len(printing_data)):
        line = printing_data[i]
        line_to_print = ""
        for j in range(len(line)):
            current_cell = str(line[j])
            line_to_print = line_to_print + current_cell + ' ' * (final_cell_length[j] - len(current_cell)) + '|'
        print(line_to_print)
        if i == 0:
            print((sum(final_cell_length)+len(final_cell_length))*'-')

def display_output():
    print(f"Ujęcie: {'miesięczne' if monthly else 'roczne'}")
    print()
    print(f"Całkowita liczba gospodarstw domowych: {len(households)}")
    print(f"Całkowita liczba mieszkańców w systemie: {commune_population}")
    print()
    print(f"Wyliczenia uwzględniają {considered.count} gospodarstw domowych, zamieszkiwanych przez {considered.population} mieszkańców.")
    print()

    count = 0
    for town in missing_by_town:
        count += missing_by_town[town]['count']

    print(f"Prawdopodobna liczba gospodarstw domowych z nadmiarowym zużyciem wody: {count}")
    print(f"Prawdopodobna liczba niewykazanych w umowach śmieciowych osób: {missing}")
    print(f"Luka finansowa w systemie śmieciowym: {missing_money.replace(',',' ')} zł")
    print()

    print_table()
    print()
    print(f"Liczba nadmiarowego użycia w poszczególnych sołectwach")
    for town in missing_by_town:
        print_data = f"{town}: {missing_by_town[town]['count']} gospodarstw, {missing_by_town[town]['missing']} osób"
        print_data = print_data.replace("\"","")
        print_data = print_data.replace('	','')
        print(print_data)

    plot_histogram()
    plot_average_water_consumption_vs_household_population()

def process_globals():
    global commune_population, commune_households, considered, household_types_data

    commune_households = len(households)
    commune_population = 0


    for household in households:
        if type(household.population) == int:
            commune_population += household.population
            
        if household.consider_flag:
            considered.add_household(household)

            household_type_id = household.population

            if not any(household_type.type == household_type_id for household_type in household_types_data):
                household_types_data.append(HouseholdType(household_type_id))

            for index in range(len(household_types_data)):
                if (household_types_data[index].type == household_type_id):
                    household_types_data[index].add_household(household)

    for index in range(len(household_types_data)):
        household_types_data[index].process()

    considered.process()

    household_types_data = sorted(household_types_data, key = lambda x: x.type)

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
    mean = sum(values) / len(values)
    return mean

def missing_in_towns():
    global households
    missing_by_town = {}

    for household in households:
        missing = count_missing(household)

        if missing > 0:
            if household.town in missing_by_town:
                missing_by_town[household.town]['count'] += 1
                missing_by_town[household.town]['missing'] += missing
            else:
                missing_by_town[household.town] = {'count': 1, 'missing': missing}

    return missing_by_town

def is_overusage(household):
    global overusage_threshold, considered

    if type(overusage_threshold) in (int, float):
        threshold = overusage_threshold
    elif overusage_threshold == 'mean':
        threshold = considered.mean
    elif overusage_threshold == 'mode+stdev':
        threshold = considered.stdev + considered.mode
    elif overusage_threshold == 'median+stdev':
        threshold = considered.stdev + considered.median
    elif overusage_threshold == 'mean+stdev':
        threshold = considered.stdev + considered.mean
    else:
        threshold = 0

    if household.mean > threshold:
        return True
    else:
        return False


def count_missing_people():
    missing_people = 0
    for household in households:
        local_household = Household(household.town,household.street,household.consumption*config.divider,household.population)
        while is_overusage(local_household):  # nie usunąłem bo myślę o bardziej zaawansowanym liczeniu
            local_household.population += 1
            local_household.mean = local_household.consumption / local_household.population
            missing_people += 1
    return missing_people

def count_missing_money(missing_count):
    missing_money = missing_count * fee * 12 / divider
    return missing_money

def plot_histogram():
    plt.hist(considered.averages, bins=distribution_bins, color='blue', alpha=0.7)
    plt.title("Liczba osób wg zużycia wody")
    plt.xlabel(f"{'Miesięczne' if monthly else 'Roczne'} zużycie wody [m3] na osobę ")
    plt.ylabel("Liczba osób")
    plt.grid(axis='y', alpha=0.75)
    plt.axvline(considered.mean, color='red', linestyle='dashed', label='Średnia')
    plt.axvline(considered.mode, color='green', linestyle='dashed', label='Dominanta')
    plt.axvline(considered.median, color='yellow', linestyle='dashed', label='Mediana')
    plt.legend()
    plt.show()

def plot_average_water_consumption_vs_household_population():
    added_labels = {
        'Powyżej normy': False,
        'W normie': False
    }

    for household in households:
        if household.consider_flag:
            population = household.population
            mean = household.mean

            if is_overusage(household):
                label = 'Powyżej normy' if not added_labels['Powyżej normy'] else None
                added_labels['Powyżej normy'] = True
                plt.plot(population, mean, 'o', markersize=3, color='red', label=label)
            else:
                label = 'W normie' if not added_labels['W normie'] else None
                added_labels['W normie'] = True
                plt.plot(population, mean, 'o', markersize=3, color='blue', label=label)

    x = []
    y = []
    for household_type in household_types_data:
        x.append(household_type.type)
        y.append(household_type.mean)


    plt.plot(x, y, '-', markersize=3, color='orange', label='Średnie zużycie wody dla danej liczby mieszkańców')



    plt.title('Średnie zużycie wody w zależności od liczby mieszkańców w gospodarstwie domowym')
    plt.xlabel('Liczba mieszkańców w gospodarstwie domowym')
    plt.ylabel('Średnie zużycie wody [m3]')
    plt.grid(axis='y', alpha=0.75)
    plt.axhline(y = overusage_threshold, color = "red", linestyle ="-")
    plt.legend()
    plt.show()

# Load data from file
load_data(data_csv)

# Calculate statistics
process_globals()
missing_by_town = missing_in_towns()

missing = 0
for town in missing_by_town:
    missing += missing_by_town[town]['missing']

missing_money = f"{count_missing_money(missing):,}"

missing_by_town = dict(sorted(missing_by_town.items(), key=lambda item: item[1]['count'], reverse=True))

# Output
display_output()
