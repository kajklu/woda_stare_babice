# Data file path
data_file = 'dane_raw.csv'

# Set to True if the data is monthly, False if it is annual
monthly = True

# Method of stealing verification
overusage_threshold = 'sigma+average' # Options: 'sigma+average', 'sigma+mode', 'sigma+median', static_value

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













import matplotlib.pyplot as plt
import math

# Global variables for water consumption and population data
commune_population = 0

commune_water_consumption = 0
commune_average_water_consumption = 0




household_types_data = {}

households = []

if monthly:
    divider = 12
else:
    divider = 1



def mode_value(values):
    if type(values) != list:
        return None
    return max(set(values), key=values.count)

def sigma(values):
    if type(values) != list or len(values) == 0:
        return 0
    variance = sum((x - mean(values)) ** 2 for x in values) / len(values)
    return math.sqrt(variance)

def median(values):
    values.sort()
    index = int(len(values) / 2)
    if type(index) != int:
        value1 = values[int(index)]
        value2 = values[int(index+1)]
        return value1+value2/2
    return values[int(index)]

def mean(values):
    if type(values) != list or len(values) == 0:
        return 0
    mean = sum(values) / len(values)
    return mean





def process_water_consumption(household):
    household['consider_water_consumption'] = True

    try:
        value = float(water_consumption)
        household['water_consumption'] = household['water_consumption'] / divider
        if value < 0 and reject_negative_consumption_values:
                household['consider_water_consumption'] = False
        elif value == 0 and reject_zero_consumption_values:
                household['consider_water_consumption'] = False
    except ValueError:
        if household['water_consumption'] == '' and reject_null_consumption_values:
            household['water_consumption'] = 0
            household['consider_water_consumption'] = False
        elif water_consumption == '':
            household['water_consumption'] = 0

    return household

def process_population(household):
    water_consumption = household['water_consumption']
    population = household['population']
    household['consider_population'] = True


    try:
        water_consumption = float(water_consumption)
        if water_consumption < 0 and reject_population_with_negative_consumption:
                household['consider_population'] = False
        elif water_consumption == 0 and reject_population_with_zero_consumption:
                household['consider_population'] = False
    except ValueError:
        if water_consumption == '' and reject_null_consumption_values:
            household['consider_water_consumption'] = False

    household['population'] = population

    return household





def process_global_variables():
    global commune_water_consumption, \
        commune_population, \
        commune_average_water_consumption, \
        households, \
        household_types_data

    for household in households:
        if household['consider_water_consumption'] and type(household['water_consumption']) in (float,int):
            commune_water_consumption += household['water_consumption']


        if household['consider_population'] and type(household['population']) in (float,int):
            commune_population += household['population']



        if household['consider_population'] and household['consider_water_consumption']:
            if household['population'] in household_types_data:
                for _ in range(household['population']):
                    household_types_data[household['population']]['water_consumption'].append(household['water_consumption'])
                    household_types_data[household['population']]['averages'].append(household['average_water_consumption'])
            else:
                household_types_data[household['population']] = {}
                for _ in range(household['population']):
                    household_types_data[household['population']]['averages'] = [household['average_water_consumption']]
                    household_types_data[household['population']]['water_consumption'] = [household['water_consumption']]

    commune_average_water_consumption = commune_water_consumption / commune_population

    for household_population in household_types_data:
        household_type_data = household_types_data[household_population]
        household_type_data['sigma'] = sigma(household_types_data[household_population]['averages'])
        household_type_data['mode_households'] = mode_value(household_types_data[household_population]['averages'])
        household_type_data['mode_population'] = mode_value(household_types_data[household_population]['averages'])
        household_type_data['average'] = mean(household_types_data[household_population]['averages'])
        household_type_data['median'] = median(household_types_data[household_population]['averages'])
        household_types_data[household_population]= household_type_data

    household_types_data = dict(sorted(household_types_data.items()))

def calculate_commune_population_mode():
    global commune_population, household_types_data

    if commune_population == 0:
        return 0
    water_consumption = []
    for household in households:
        if household['consider_water_consumption']:
            for _ in range(household['population']):
                water_consumption.append(household['average_water_consumption'])

    commune_population_mode = mode_value(water_consumption)

    return commune_population_mode

def calculate_commune_household_mode():
    global commune_population, household_types_data

    if commune_population == 0:
        return 0
    water_consumption = []
    for household in households:
        if household['consider_water_consumption']:
            water_consumption.append(household['average_water_consumption'])

    commune_household_mode = mode_value(water_consumption)

    return commune_household_mode



def calculate_commune_sigma():
    if commune_population == 0:
        return 0
    water_consumption = []
    for household in households:
        if household['consider_water_consumption']:
            for _ in range(household['population']):
                water_consumption.append(household['average_water_consumption'])
    commune_sigma = sigma(water_consumption)
    return commune_sigma


def calculate_commune_median():
    global commune_population, household_types_data

    if commune_population == 0:
        return 0
    water_consumption = []
    for household in households:
        if household['consider_water_consumption']:
            for _ in range(household['population']):
                water_consumption.append(household['average_water_consumption'])
    commune_median = median(water_consumption)
    return commune_median





def count_overusage_by_cities():
    global households
    overusages_in_cities = {}

    for household in households:
        if check_overusage(household):
            if household['city'] in overusages_in_cities:
                overusages_in_cities[household['city']] += 1
            else:
                overusages_in_cities[household['city']] = 1

    return overusages_in_cities

def count_missing_people():
    global households, overusage_threshold
    missing_people = 0
    for household in households:
        local_household = household.copy()
        while check_overusage(local_household):
            local_household['population'] += 1
            local_household['average_water_consumption'] = local_household['water_consumption'] / local_household['population']
            missing_people += 1
    return missing_people

def count_missing_money(number_of_missing_people):
    global fee, divider
    missing_money = number_of_missing_people * fee * 12 / divider
    return missing_money

def check_overusage(household):
    global overusage_threshold, commune_average_water_consumption, commune_population_mode, household_types_data, commune_household_mode
    threshold = household['average_water_consumption']

    if type(overusage_threshold) in (int, float):
        threshold = overusage_threshold
    elif overusage_threshold == 'sigma+mode':
        threshold = commune_sigma+commune_household_mode
    elif overusage_threshold == 'sigma+median':
        threshold = commune_sigma+commune_median
    elif overusage_threshold == 'sigma+average':
        threshold = commune_sigma+commune_average_water_consumption


    if household['average_water_consumption'] > threshold:
        return True
    else:
        return False



def plot_histogram_households_average():
    global households, commune_household_mode, commune_average_water_consumption
    average_water_consumption = []
    for household in households:
        if household['consider_water_consumption']:
            average_water_consumption.append(household['average_water_consumption'])
    plt.hist(average_water_consumption, bins=1000, color='blue', alpha=0.7)
    plt.title('Liczba gospodarstw domowych zużywających określone ilości wody')
    plt.xlabel('Średnie zużycie wody (m3)')
    plt.ylabel('Liczba gospodarstw domowych')
    plt.grid(axis='y', alpha=0.75)
    plt.axvline(commune_average_water_consumption, color='red', linestyle='dashed', label='Średnie zużycie wody gminy')
    plt.axvline(commune_household_mode, color='green', linestyle='dashed', label='Dominanta zużycia wody gminy')
    plt.legend()
    plt.show()

def plot_histogram_households_total():
    global households, commune_mode, commune_average_water_consumption
    average_water_consumption = []
    for household in households:
        if household['consider_water_consumption']:
            average_water_consumption.append(household['water_consumption'])
    plt.hist(average_water_consumption, bins=1000, color='blue', alpha=0.7)
    plt.title('Liczba gospodarstw domowych zużywających określone ilości wody')
    plt.xlabel('Całkowite zużycie wody (m3)')
    plt.ylabel('Liczba gospodarstw domowych')
    plt.grid(axis='y', alpha=0.75)
    plt.axvline(commune_water_consumption/len(average_water_consumption), color='red', linestyle='dashed', label='Zużycie wody gminy')
    plt.axvline(commune_household_mode, color='green', linestyle='dashed', label='Dominanta zużycia wody gminy')
    plt.legend()
    plt.show()

def plot_histogram_population_average():
    global households, commune_population_mode, commune_average_water_consumption
    average_water_consumption = []
    for household in households:
        if household['consider_water_consumption']:
            for _ in range(household['population']):
                average_water_consumption.append(household['average_water_consumption'])
    plt.hist(average_water_consumption, bins=1000, color='blue', alpha=0.7)
    plt.title('Liczba osób zużywających określone ilości wody')
    plt.xlabel('Zużycie wody (m3)')
    plt.ylabel('Liczba osób')
    plt.grid(axis='y', alpha=0.75)
    plt.axvline(commune_water_consumption/len(average_water_consumption), color='red', linestyle='dashed', label='Zużycie wody gminy')
    plt.axvline(commune_population_mode, color='green', linestyle='dashed', label='Dominanta zużycia wody gminy')
    plt.legend()
    plt.show()

def plot_average_water_consumption_vs_household_population():
    global households, overusage_threshold, household_types_data

    added_labels = {
        'Powyżej normy': False,
        'W normie': False
    }

    for household in households:
        if household['consider_water_consumption']:
            population = household['population']
            average_water_consumption = household['average_water_consumption']

            if check_overusage(household):
                label = 'Powyżej normy' if not added_labels['Powyżej normy'] else None
                added_labels['Powyżej normy'] = True
                plt.plot(population, average_water_consumption, 'o', markersize=3, color='red', label=label)
            else:
                label = 'W normie' if not added_labels['W normie'] else None
                added_labels['W normie'] = True
                plt.plot(population, average_water_consumption, 'o', markersize=3, color='blue', label=label)

    plt.plot(
        household_types_data.keys(),
        [household_types_data[population]['average'] for population in household_types_data],
        '-', markersize=3, color='orange',
        label='Średnie zużycie wody dla danej liczby mieszkańców'
    )

    plt.legend()
    plt.title('Średnie zużycie wody w zależności od liczby mieszkańców w gospodarstwie domowym')
    plt.xlabel('Liczba mieszkańców w gospodarstwie domowym')
    plt.ylabel('Średnie zużycie wody (m3)')
    plt.grid(axis='y', alpha=0.75)
    plt.show()

def count_considered_households():
    considered_households = 0
    for household in households:
        if household['consider_water_consumption']:
            considered_households += 1
    return considered_households


def print_table():
    printing_data = []

    header = f"Typ | Dominanta populacji m3 | Dominanta gospodarstw m3 | Średnia m3 | Odchylenie standardowe | Mediana"


    final_cell_length = []
    header_cells = header.split('|')
    printing_data.append(header_cells)

    for i in range(len(header_cells)):
        cell_length = len(str(header_cells[i]))
        final_cell_length.append(cell_length)

    reference = f"Gmina | {round(commune_population_mode,2)} | {round(commune_household_mode,2)} | {round(commune_average_water_consumption,2)} | {round(commune_sigma,2)} | {round(commune_median,2)}"


    reference_cells = reference.split('|')
    printing_data.append(reference_cells)


    for i in range(len(reference_cells)):
        cell_length = len(str(reference_cells[i]))
        if final_cell_length[i] < cell_length:
            final_cell_length[i] = cell_length

    for household_type in household_types_data:
        household_type_data = household_types_data[household_type]
        print_data = f"{household_type} mieszkańców | {round(household_type_data['mode_population'], 2)} | {round(household_type_data['mode_households'], 2)} | {round(household_type_data['average'], 2)} | {round(household_type_data['sigma'], 2)} | {round(household_type_data['median'], 2)} "
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



with open(data_file, "r") as file:
    lines = file.readlines()

for line in lines:
    line.replace(',','.')
    data = line.split(';')
    city = data[0]
    if city != '﻿Miejscowość':
        street = data[1]
        water_consumption = data[2].replace(',', '.')
        population = data[3].replace(',', '.')

        try:
            water_consumption = float(water_consumption)
        except ValueError:
            pass
        try:
            population = int(population)
        except ValueError:
            population = 0


        household = dict(city=city, street=street, population=population, water_consumption=water_consumption)

        household = process_water_consumption(household)

        household = process_population(household)

        try:
            household['average_water_consumption'] = household['water_consumption']/household['population'] if population else 0
        except TypeError:
            household['average_water_consumption'] = 0


        if population is not None:
            households.append(household)


process_global_variables()
considered_households = count_considered_households()
commune_population_mode = calculate_commune_population_mode()
commune_household_mode = calculate_commune_household_mode()
commune_sigma = calculate_commune_sigma()
commune_median = calculate_commune_median()
missing_people = count_missing_people()
missing_money = f"{count_missing_money(missing_people):,}"
stealers_in_cities = count_overusage_by_cities()
stealers_in_cities = dict(sorted(stealers_in_cities.items(), key=lambda item: item[1], reverse=True))

print(f'Ujęcie: {'miesięczne' if monthly else 'roczne'}')
print()
print(f"Liczba mieszkańców: {commune_population}")
print(f"Całkowita liczba gospodarstw domowych: {len(households)}")
print(f"Liczba uwzględnionych gospodarstw domowych: {considered_households}")
print(f"Zużycie wody gminy: {round(commune_water_consumption,2)} m3")
print()
print(f"Prawdopodobna liczba gospodarstw domowych z nadmiarowym zużyciem wody: {sum(stealers_in_cities.values())}")
print(f"Prawdopodobna liczba niewykazanych w umowach śmieciowych osób: {missing_people}")
print(f"Brakujący przychód: {missing_money.replace(',',' ')} zł")
print()

print_table()
print()
print(f"Liczba nadmiarowego użyć w poszczególnych sołectwach")
for city in stealers_in_cities:
    print_data = f"{city}: {stealers_in_cities[city]}"
    print_data = print_data.replace("\"","")
    print_data = print_data.replace('	','')
    print(print_data)

plot_histogram_households_average()
plot_histogram_population_average()
plot_average_water_consumption_vs_household_population()

