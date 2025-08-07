import matplotlib.pyplot as plt
import math
from Household import Household

# Data file path
data_csv = 'dane_raw.csv'

# Set to True if the data is monthly, False if it is annual
monthly = True

# Method of stealing verification
overusage_threshold = 'mean+stdev'  # Options: 'sigma+average', 'sigma+mode', 'sigma+median', static_value

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

considered_households = int
considered_population = int
considered_consumption = float
considered_mean = float
considered_mode = float
considered_median = float
considered_stdev = float

household_types_data = {}
households = []

if monthly:
    divider = 12
else:
    divider = 1


def load_data(data_file):
    with open(data_file, "r", encoding="utf-8") as file:
        lines = file.readlines()

    file.close()

    for line in lines:
        line.replace(',', '.')
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

    header = f"Typ | Liczba gospodarstw uwzględnionych | Całkowite zużycie w typie gospodarstw [m3] | Dominanta [m3] | Średnia [m3] | Odchylenie standardowe [m3] | Mediana [m3] "

    final_cell_length = []
    header_cells = header.split('|')
    printing_data.append(header_cells)

    for i in range(len(header_cells)):
        cell_length = len(str(header_cells[i]))
        final_cell_length.append(cell_length)

    reference = f"Gmina | {considered_households} ({round(considered_households / considered_households * 100, 2)}%) | {round(considered_consumption, 2)} ({round(considered_consumption / considered_consumption * 100, 2)}%) | {round(considered_mode, 2)} | {round(considered_mean, 2)} | {round(considered_stdev, 2)} | {round(considered_median, 2)}"

    reference_cells = reference.split('|')
    printing_data.append(reference_cells)

    for i in range(len(reference_cells)):
        cell_length = len(str(reference_cells[i]))
        if final_cell_length[i] < cell_length:
            final_cell_length[i] = cell_length

    for household_type in household_types_data:
        household_type_data = household_types_data[household_type]
        print_data = f"{household_type} os. w gospodarstwie | {household_type_data['count']} ({round(household_type_data['count'] / considered_households * 100, 2)}%) | {round(household_type_data['consumption'], 2)} ({round(household_type_data['consumption'] / considered_consumption * 100, 2)}%) | {round(household_type_data['mode'], 2)} | {round(household_type_data['mean'], 2)} | {round(household_type_data['stdev'], 2)} | {round(household_type_data['median'], 2)}"
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
            print((sum(final_cell_length) + len(final_cell_length)) * '-')


def display_output():
    print(f"Ujęcie: {'miesięczne' if monthly else 'roczne'}")
    print()
    print(f"Całkowita liczba gospodarstw domowych: {len(households)}")
    print(f"Całkowita liczba mieszkańców w systemie: {commune_population}")
    print()
    print(
        f"Wyliczenia uwzględniają {considered_households} gospodarstw domowych, zamieszkiwanych przez {considered_population} mieszkańców.")
    print()
    print(f"Prawdopodobna liczba gospodarstw domowych z nadmiarowym zużyciem wody: {sum(stealers_in_cities.values())}")
    print(f"Prawdopodobna liczba niewykazanych w umowach śmieciowych osób: {missing_people}")
    print(f"Luka finansowa w systemie śmieciowym: {missing_money.replace(',', ' ')} zł")
    print()

    print_table()
    print()
    print(f"Liczba nadmiarowego użycia w poszczególnych sołectwach")
    for city in stealers_in_cities:
        print_data = f"{city}: {stealers_in_cities[city]}"
        print_data = print_data.replace("\"", "")
        print_data = print_data.replace('	', '')
        print(print_data)

    plot_histogram()
    plot_average_water_consumption_vs_household_population()


def process_global_variables():
    global commune_population, commune_households, considered_mean, considered_population, considered_households, considered_consumption, household_types_data

    commune_households = len(households)

    commune_population = 0
    considered_population = 0
    considered_consumption = 0
    considered_households = 0

    for household in households:
        if type(household.population) == int:
            commune_population += household.population

        if household.consider_flag:
            considered_consumption += household.consumption
            considered_population += household.population
            considered_households += 1

            household_type = household.population

            if household_type not in household_types_data:
                household_types_data[household_type] = {'count': 0, 'consumption': 0, 'averages': []}

            household_types_data[household_type]['count'] += 1
            household_types_data[household_type]['consumption'] += household.consumption

            for _ in range(household_type):
                household_types_data[household_type]['averages'].append(household.mean)

    for household_type in household_types_data:
        household_type_data = household_types_data[household_type]

        household_type_data['stdev'] = stdev(household_types_data[household_type]['averages'])
        household_type_data['mode'] = mode(household_types_data[household_type]['averages'])
        household_type_data['mean'] = mean(household_types_data[household_type]['averages'])
        household_type_data['median'] = median(household_types_data[household_type]['averages'])

        household_types_data[household_type] = household_type_data

    household_types_data = dict(sorted(household_types_data.items()))

    considered_mean = considered_consumption / considered_population
    calculate_considered_mode()
    calculate_considered_stdev()
    calculate_considered_median()


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


def calculate_considered_mode():
    global considered_mode

    if considered_population == 0:
        return 0

    consumptions = []
    for household in households:
        if household.consider_flag:
            for _ in range(household.population):
                consumptions.append(household.mean)

    considered_mode = mode(consumptions)


def calculate_considered_stdev():
    global considered_stdev

    if considered_population == 0:
        return 0

    consumptions = []
    for household in households:
        if household.consider_flag:
            for _ in range(household.population):
                consumptions.append(household.mean)

    considered_stdev = stdev(consumptions)


def calculate_considered_median():
    global considered_median

    if considered_population == 0:
        return 0

    consumptions = []
    for household in households:
        if household.consider_flag:
            for _ in range(household.population):
                consumptions.append(household.mean)

    considered_median = median(consumptions)


def count_overusage_by_cities():
    global households
    overusages_in_cities = {}

    for household in households:
        if check_overusage(household):
            if household.town in overusages_in_cities:
                overusages_in_cities[household.town] += 1
            else:
                overusages_in_cities[household.town] = 1

    return overusages_in_cities


def check_overusage(household):
    global overusage_threshold, considered_mean, considered_stdev, considered_mode_population, considered_median

    if type(overusage_threshold) in (int, float):
        threshold = overusage_threshold
    elif overusage_threshold == 'mean':
        threshold = considered_mean
    elif overusage_threshold == 'mode+stdev':
        threshold = considered_stdev + considered_mode_population
    elif overusage_threshold == 'median+stdev':
        threshold = considered_stdev + considered_median
    elif overusage_threshold == 'mean+stdev':
        threshold = considered_stdev + considered_mean
    else:
        threshold = 0

    if household.mean > threshold:
        return True
    else:
        return False


def count_missing_people():
    missing_people = 0
    for household in households:
        local_household = Household(household.town,household.street,household.consumption,household.population)
        while check_overusage(local_household):  # nie usunąłem bo myślę o bardziej zaawansowanym liczeniu
            local_household.population += 1
            local_household.mean = local_household.consumption / local_household.population
            missing_people += 1
    return missing_people


def count_missing_money(number_of_missing_people):
    global fee, divider
    missing_money = number_of_missing_people * fee * 12 / divider
    return missing_money


def plot_histogram():
    averages = []
    for household in households:
        if household.consider_flag:
            for _ in range(household.population):
                averages.append(household.mean)

    plt.hist(averages, bins=distribution_bins, color='blue', alpha=0.7)
    plt.title("Liczba osób wg zużycia wody")
    plt.xlabel(f"{'Miesięczne' if monthly else 'Roczne'} zużycie wody [m3] na osobę ")
    plt.ylabel("Liczba osób")
    plt.grid(axis='y', alpha=0.75)
    plt.axvline(considered_mean, color='red', linestyle='dashed', label='Średnia')
    plt.axvline(considered_mode, color='green', linestyle='dashed', label='Dominanta')
    plt.axvline(considered_median, color='yellow', linestyle='dashed', label='Mediana')
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

            if check_overusage(household):
                label = 'Powyżej normy' if not added_labels['Powyżej normy'] else None
                added_labels['Powyżej normy'] = True
                plt.plot(population, mean, 'o', markersize=3, color='red', label=label)
            else:
                label = 'W normie' if not added_labels['W normie'] else None
                added_labels['W normie'] = True
                plt.plot(population, mean, 'o', markersize=3, color='blue', label=label)

    plt.plot(
        household_types_data.keys(),
        [household_types_data[population]['mean'] for population in household_types_data],
        '-', markersize=3, color='orange',
        label='Średnie zużycie wody dla danej liczby mieszkańców'
    )

    plt.legend()
    plt.title('Średnie zużycie wody w zależności od liczby mieszkańców w gospodarstwie domowym')
    plt.xlabel('Liczba mieszkańców w gospodarstwie domowym')
    plt.ylabel('Średnie zużycie wody [m3]')
    plt.grid(axis='y', alpha=0.75)
    plt.show()


# Load data from file
load_data(data_csv)

# Calculate statistics
process_global_variables()
missing_people = count_missing_people()
missing_money = f"{count_missing_money(missing_people):,}"
stealers_in_cities = count_overusage_by_cities()
stealers_in_cities = dict(sorted(stealers_in_cities.items(), key=lambda item: item[1], reverse=True))

# Output
display_output()
