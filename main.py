import matplotlib.pyplot as plt
import config
from math import ceil
from Household import Household
from HouseholdType import HouseholdType


# Global variables for water consumption and population data
commune_population = 0
commune_households = 0
missing_people = 0
considered = HouseholdType("Gmina")

household_types_data = []
households = []
missing_by_town = {}


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
    print(f"Ujęcie: {'miesięczne' if config.monthly else 'roczne'}")
    print()
    print(f"Całkowita liczba gospodarstw domowych: {len(households)}")
    print(f"Całkowita liczba mieszkańców w systemie: {commune_population}")
    print()
    print(f"Wyliczenia uwzględniają {considered.count} gospodarstw domowych, zamieszkiwanych przez {considered.population} mieszkańców.")

    print()
    print()
    print("DANE STATYSTYCZNE")
    print('------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
    print_table()

    print()
    print()
    print("LICZBA NADMIERNYCH ZUŻYĆ WODY")
    print('------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
    count = 0
    for town in missing_by_town:
        count += missing_by_town[town]['count']
    print(f"Prawdopodobna liczba gospodarstw domowych z nadmiarowym zużyciem wody: {count}")
    print(f"Prawdopodobna liczba niewykazanych w umowach śmieciowych osób: {missing_people}")
    print()
    print(f"Liczba nadmiarowego użycia w poszczególnych sołectwach")
    for town in missing_by_town:
        print_data = f"{town}: {missing_by_town[town]['count']} gospodarstw, {missing_by_town[town]['missing']} osób"
        print_data = print_data.replace("\"","")
        print_data = print_data.replace('	','')
        print(print_data)


    print()
    print()
    print("ANALIZA PIENIĘŻNA")
    print('------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
    money_analysis()



    if config.render_graphs:
        plot_histogram()
        plot_average_water_consumption_vs_household_population()


def process_data():
    global commune_population, \
        commune_households, \
        considered, \
        household_types_data, \
        missing_by_town, \
        missing_people \

    commune_households = len(households)
    commune_population = 0


    for household in households:
        if type(household.population) == int:
            commune_population += household.population

        if household.consider_flag:
            considered.add_household(household)

            household_type_id = household.population

            if not any(household_type.category == household_type_id for household_type in household_types_data):
                household_types_data.append(HouseholdType(household_type_id))

            for index in range(len(household_types_data)):
                if household_types_data[index].category == household_type_id:
                    household_types_data[index].add_household(household)

    for index in range(len(household_types_data)):
        household_types_data[index].process()

    considered.process()

    household_types_data = sorted(household_types_data, key = lambda x: x.category)

    missing_by_town = missing_in_towns()

    missing_people = 0
    for town in missing_by_town:
        missing_people += missing_by_town[town]['missing']


def missing_in_towns():
    global households, missing_by_town

    for household in households:
        if household.consider_flag:
            missing_in_household = count_missing_people(household)

            if missing_in_household > 0:
                if household.town in missing_by_town:
                    missing_by_town[household.town]['count'] += 1
                    missing_by_town[household.town]['missing'] += missing_in_household
                else:
                    missing_by_town[household.town] = {'count': 1, 'missing': missing_in_household}

    missing_by_town = dict(sorted(missing_by_town.items(), key=lambda item: item[1]['count'], reverse=True))

    return missing_by_town

def calculate_threshold():
    global considered

    if type(config.overusage_threshold) in (int, float):
        threshold = config.overusage_threshold
    elif config.overusage_threshold == 'mean':
        threshold = considered.mean
    elif config.overusage_threshold == 'mode+stdev':
        threshold = considered.stdev + considered.mode
    elif config.overusage_threshold == 'median+stdev':
        threshold = considered.stdev + considered.median
    elif config.overusage_threshold == 'mean+stdev':
        threshold = considered.stdev + considered.mean
    else:
        threshold = 0
    return threshold

def is_overusage(household, threshold = calculate_threshold()):
    if household.mean > threshold:
        return True
    else:
        return False

def count_missing_people(household):
    missing_in_household = 0
    threshold = calculate_threshold()
    if is_overusage(household, threshold):
        missing_in_household = ceil(household.consumption/threshold - household.population)
    return missing_in_household

def plot_histogram():
    bins = round(config.distribution_bins * (config.upper_cutoff_percentage-config.lower_cutoff_percentage)/100)
    plt.hist(considered.averages, bins=bins, color='blue', alpha=0.7)
    plt.title("Liczba osób wg zużycia wody")
    plt.xlabel(f"{'Miesięczne' if config.monthly else 'Roczne'} zużycie wody [m3] na osobę ")
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
        x.append(household_type.category)
        y.append(household_type.mean)


    plt.plot(x, y, '-', markersize=3, color='orange', label='Średnie zużycie wody dla danej liczby mieszkańców')



    plt.title('Średnie zużycie wody w zależności od liczby mieszkańców w gospodarstwie domowym')
    plt.xlabel('Liczba mieszkańców w gospodarstwie domowym')
    plt.ylabel('Średnie zużycie wody [m3]')
    plt.grid(axis='y', alpha=0.75)
    plt.axhline(y = config.overusage_threshold, color = "red", linestyle ="-")
    plt.legend()
    plt.show()

def money_analysis():

    current_income = config.fee * commune_population * 12 / config.divider
    missing_money = missing_people * config.fee * 12 / config.divider
    income_after_correction = current_income + missing_money
    total_population = commune_population + missing_people
    if config.monthly:
        new_fee = current_income / total_population
    else:
        new_fee = current_income / total_population / 12

    water_reckoning = 0
    for household in households:
        overconsumption = household.consumption - config.linear_reckoning_threshold
        overconsumption = max(0, overconsumption)
        water_reckoning += round(config.base_price + overconsumption * config.water_price,2)

    current_income = f"{round(current_income,2):,}".replace(",", " ")
    missing_money = f"{round(missing_money,2):,}".replace(",", " ")
    income_after_correction = f"{round(income_after_correction,2):,}".replace(",", " ")
    water_reckoning = f"{round(water_reckoning,2):,}".replace(",", " ")
    new_fee = f"{round(new_fee,2):,}".replace(",", " ")
    print(f"Aktualne wpływy z umów za wywóz śmieci: {current_income} zł")
    print(f"Brakujące wpływy ze względu na niezgłoszenie osób: {missing_money} zł")
    print(f"Wpływy po zgłoszeniu brakujących osób: {income_after_correction} zł")
    print(f"Nowa opłata za wywóz śmieci bez zmian w budżecie: {new_fee} zł")



    print()
    print(f"Wpływy w przypadku przejścia na rozliczenie wodą: {water_reckoning} zł")


# Load data from file
load_data(config.data_csv)

# Calculate statistics
process_data()

# Output
display_output()