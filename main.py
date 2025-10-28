import time

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import config
from Household import Household
from HouseholdType import mean
from HouseholdType import covariance
from HouseholdType import pearson_correlation
from HouseholdType import HouseholdType


# Global variables for water consumption and population data
commune_population = 0
commune_households = 0
missing_people = 0
considered = HouseholdType("Gmina")

households_grouped = {}
households_not_grouped = {}

households = []

missing_statistics = {}


def load_data(data_file):
    global commune_population, \
        commune_households, \
        considered, \
        households_grouped, \
        missing_people, \
        households_not_grouped, households

    commune_population = 0
    commune_households = 0
    missing_people = 0

    considered = HouseholdType("Gmina")

    households_grouped = {}
    households_not_grouped = {}
    households = []

    print("Wczytywanie danych z pliku...")
    with open(data_file, "r", encoding="utf-8") as file:
        lines = file.readlines()

    file.close()
    print("Tworzenie obiektów gospodarstw domowych...")
    for line in lines:
        line.replace(',','.')
        data = line.split(';')
        if data[0] != '﻿Miejscowość':
            town = data[0]
            street = data[1]
            consumption = data[2].replace(',', '.')
            population = int(data[3].replace(',', '.'))
            average_consumption = data[4].replace(',', '.').replace("\n","")

            if average_consumption == '' or average_consumption is None:
                average_consumption = 0.0
            if consumption == '' or consumption is None:
                consumption = 0.0

            household = Household(town,street,float(consumption),float(average_consumption),population)

            if population is not None:
                households.append(household)
                commune_population+=household.population
                commune_households += 1
                if household.consider_flag:
                    considered.add_household(household)
                    if household.category not in households_grouped:
                        household_type = HouseholdType(household.category)
                        households_grouped[household.category] = household_type
                        household_type.add_household(household)
                    else:
                        household_type = households_grouped[household.category]
                        household_type.add_household(household)

                    if household.population not in households_not_grouped:
                        household_type = HouseholdType(household.population)
                        households_not_grouped[household.population] = household_type
                        household_type.add_household(household)
                    else:
                        household_type = households_not_grouped[household.population]
                        household_type.add_household(household)
    print("Przetwarzanie danych typów gospodarstw domowych...")
    for household_type in households_grouped:
        household_type = households_grouped[household_type]
        household_type.process()

    for household_type in households_not_grouped:
        household_type = households_not_grouped[household_type]
        household_type.process()

    considered.process()

    def sort_key(obj):
        import re
        # Szukamy pierwszej liczby w napisie
        match = re.search(r'\d+', str(obj.category))
        if match:
            return int(match.group())  # liczba do sortowania
        return float('inf')  # jeśli brak liczby, wrzucamy na koniec

    households_grouped= dict(sorted(households_grouped.items(), key=lambda item: sort_key(item[1])))
    households_not_grouped = dict(sorted(households_not_grouped.items(), key=lambda item: sort_key(item[1])))


def display_output():
    def print_table():
        printing_data = []

        header = f"Typ | Liczba gospodarstw uwzględnionych | Liczba osób | Całkowite zużycie w typie gospodarstw [m³] | Dominanta [m³] | Średnia [m³] | Odchylenie standardowe [m³] | Mediana [m³] "

        final_cell_length = []
        header_cells = header.split('|')
        printing_data.append(header_cells)

        for i in range(len(header_cells)):
            cell_length = len(str(header_cells[i]))
            final_cell_length.append(cell_length)

        reference = f"Gmina | {considered.count} ({round(considered.count / considered.count * 100, 2)}%) | {considered.population} ({round(considered.population / considered.population * 100)}%) | {round(considered.consumption, 2)} ({round(considered.consumption / considered.consumption * 100, 2)}%) | {round(considered.mode, 2)} | {round(considered.mean, 2)} | {round(considered.stdev, 2)} | {round(considered.median, 2)}"

        reference_cells = reference.split('|')
        printing_data.append(reference_cells)

        for i in range(len(reference_cells)):
            cell_length = len(str(reference_cells[i]))
            if final_cell_length[i] < cell_length:
                final_cell_length[i] = cell_length

        for household_type in households_grouped.values():
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
                print((sum(final_cell_length) + len(final_cell_length)) * '-')

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
    x = []
    y = []

    for household in households:
        if household.consider_flag:
            x.append(household.population)
            y.append(household.mean)

    household_average_population = mean(x)
    print(f"Średnia populacja: {household_average_population}")
    covariance_value = covariance(x, y)
    print(f"Kowariancja xy: {covariance_value}")
    covariance_value = covariance(x, x)
    print(f"Kowariancja xx: {covariance_value}")
    covariance_value = covariance(y, y)
    print(f"Kowariancja yy: {covariance_value}")
    p_correlation = pearson_correlation(x, y)
    print(f"Korelacja: {p_correlation}")
    print()
    print_table()

    print()
    print()
    print("LICZBA NADMIERNYCH ZUŻYĆ WODY")
    print('------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
    global missing_people
    count = 0

    print(f"Liczba nadmiarowego użycia w poszczególnych sołectwach")
    for town in missing_statistics:
        household_count = missing_statistics[town]['count']
        missing_people_in_town = missing_statistics[town]['missing']
        print_data = f"{town}: {household_count} gospodarstw, {missing_people_in_town} osób"
        print_data = print_data.replace("\"","")
        print_data = print_data.replace('	','')
        print(print_data)
        # for street in missing_statistics[town]['streets']:
        #     street_household_count = missing_statistics[town]['streets'][street]['count']
        #     street_missing_people = missing_statistics[town]['streets'][street]['missing']
        #     print_data = f"    {street}: {street_household_count} gospodarstw, {street_missing_people} osób"
        #     print_data = print_data.replace("\"","")
        #     print_data = print_data.replace('	','')
        #     print(print_data)
        count += household_count
        missing_people += missing_people_in_town
    print()
    print(f"Prawdopodobna liczba gospodarstw domowych z nadmiarowym zużyciem wody: {count}")
    print(f"Prawdopodobna liczba niewykazanych w umowach śmieciowych osób: {missing_people}")
    print()


    print(f"Liczba nadmiarowego użycia w poszczególnych sołectwach")
    for town in missing_statistics:
        household_count = missing_statistics[town]['count']
        missing_people_in_town = missing_statistics[town]['missing']
        print_data = f"{town}: {household_count} gospodarstw, {missing_people_in_town} osób"
        print_data = print_data.replace("\"","")
        print_data = print_data.replace('	','')
        print(print_data)
    print()
    print(f"Prawdopodobna liczba gospodarstw domowych z nadmiarowym zużyciem wody: {count}")
    print(f"Prawdopodobna liczba niewykazanych w umowach śmieciowych osób: {missing_people}")
    print()

    print()
    print()
    print("ANALIZA PIENIĘŻNA")
    print('------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
    money_analysis()



    if config.render_graphs:
        plot()

def calculate_threshold(threshold = config.monthly_overusage_threshold):
    global considered

    if type(config.monthly_overusage_threshold * 12 / config.divider) in (int, float):
        threshold = config.monthly_overusage_threshold * 12 / config.divider
    elif config.monthly_overusage_threshold== 'mean':
        threshold = considered.mean* 12 / config.divider
    elif config.monthly_overusage_threshold  == 'mode+stdev':
        threshold = (considered.stdev + considered.mode) * 12 / config.divider
    elif config.monthly_overusage_threshold  == 'median+stdev':
        threshold = (considered.stdev + considered.median) * 12 / config.divider
    elif config.monthly_overusage_threshold  == 'mean+stdev':
        threshold = (considered.stdev + considered.mean) * 12 / config.divider
    else:
        threshold = threshold * 12 / config.divider
    return threshold

def find_missing_people(town = None, street = None, number=None, threshold=calculate_threshold()):
    print(f"Obliczanie brakujących osób przy progu zużycia: {round(threshold,2)} m³")
    global missing_statistics, households
    missing_statistics = {}
    for household in households:
        if household.consider_flag:
            if (town is None or household.town == town) and (street is None or household.street == street) and (number is None or household.number == number):
                missing_in_household = household.count_missing_people(threshold=threshold)
                if missing_in_household > 0:
                    if household.town in missing_statistics:
                        if household.street in missing_statistics[household.town]['streets']:
                            missing_statistics[household.town]['streets'][household.street]['count'] += 1
                            missing_statistics[household.town]['streets'][household.street]['missing'] += missing_in_household
                            missing_statistics[household.town]['missing'] += missing_in_household
                            missing_statistics[household.town]['count'] += 1
                        else:
                            missing_statistics[household.town]['streets'][household.street] = {'count': 1, 'missing': missing_in_household}
                            missing_statistics[household.town]['missing'] += missing_in_household
                            missing_statistics[household.town]['count'] += 1
                    else:
                        missing_statistics[household.town] = {'streets':{household.street: {'count': 1, 'missing': missing_in_household}}, 'count': 1, 'missing': missing_in_household}
    missing_statistics = dict(sorted(missing_statistics.items(), key=lambda item: item[1]['count'], reverse=True))
    return missing_statistics

def plot():
    def plot_histogram():
        plt.rcParams['font.family'] = 'Times New Roman'
        plt.rcParams['font.size'] = 24
        plt.rcParams['axes.titlesize'] = 24
        plt.rcParams['axes.labelsize'] = 20
        plt.rcParams['legend.fontsize'] = 16


        bins = round(config.distribution_bins * (config.upper_cutoff_percentage-config.lower_cutoff_percentage)/100)
        plt.hist(considered.averages, bins=bins, color='blue', alpha=0.7)
        #plt.title ("Liczba osób wg zużycia wody")
        plt.xlabel(f"{'Miesięczne' if config.monthly else 'Roczne'} zużycie wody [m³] na osobę ")
        plt.ylabel("Liczba osób")
        plt.grid(axis='y', alpha=0.75)
        plt.axvline(considered.mean, color='red', linestyle='dashed', label='Średnia')
        plt.axvline(considered.mode, color='green', linestyle='dashed', label='Dominanta')
        plt.axvline(considered.median, color='yellow', linestyle='dashed', label='Mediana')
        plt.legend()
        plt.show()

    def plot_average_water_consumption_vs_household_population():
        plt.rcParams['font.family'] = 'Times New Roman'
        plt.rcParams['font.size'] = 24
        plt.rcParams['axes.titlesize'] = 24
        plt.rcParams['axes.labelsize'] = 20
        plt.rcParams['legend.fontsize'] = 16
        x = []
        y = []
        for household_type in households_grouped.values():
            x.append(household_type.category)
            y.append(household_type.mean)

        plt.plot(x, y, '-', markersize=3, color='orange', label='Średnie zużycie wody dla danej liczby mieszkańców')

        for household_type in households_grouped.values():
            print(household_type)
            for mean in household_type.averages:
                if mean > calculate_threshold():
                    plt.plot(str(household_type.category), mean, 'o', markersize=3, color='red')
                else:
                    plt.plot(str(household_type.category), mean, 'o', markersize=3, color='blue')


        #plt.title ('Średnie zużycie wody w zależności od liczby mieszkańców w gospodarstwie domowym')
        plt.xlabel('Liczba mieszkańców w gospodarstwie domowym')
        plt.ylabel('Średnie zużycie wody [m³]')
        plt.grid(axis='y', alpha=0.75)
        plt.axhline(y = config.monthly_overusage_threshold * 12 / config.divider, color = "red", linestyle ="-")
        legend_elements = [ Line2D([0], [0], color='orange', label='Średnie zużycie wody', markersize = 3),
                            Line2D([0], [0], color='red', label='Próg zużycia', markersize=3),
                            Line2D([0], [0], marker='o', color='w', label='Powyżej progu', markerfacecolor='r', markersize=10),
                            Line2D([0], [0], marker='o', color='w', label='Poniżej progu', markerfacecolor='b', markersize=10)]
        plt.legend(handles=legend_elements, loc ='upper right')
        plt.show()
    plot_histogram()
    plot_average_water_consumption_vs_household_population()

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
        overconsumption = household.consumption - config.linear_reckoning_threshold*12/config.divider
        overconsumption = max(0, overconsumption)
        water_reckoning += overconsumption * config.water_price
        if config.linear_reckoning_threshold > 0:
            water_reckoning += config.base_price*12/config.divider

    water_reckoning = round(water_reckoning,2)

    water_reckoning_vs_current_income = water_reckoning - current_income

    result = {
        "current_income": current_income,
        "missing_money": missing_money,
        "income_after_correction": income_after_correction,
        "new_fee": new_fee,
        "water_reckoning": water_reckoning,
        "water_reckoning_vs_current_income": water_reckoning_vs_current_income
    }

    water_reckoning_vs_current_income = f"{round(water_reckoning_vs_current_income, 2):,}".replace(",", " ")
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
    print(f"Stawka za metraż wody: {config.water_price} zł")
    print(f"Próg rozliczania liniowego: {config.linear_reckoning_threshold} m³")
    print(f"Wpływy w przypadku przejścia na rozliczenie wodą: {water_reckoning} zł")
    print(f"Zysk z zastosowania rozliczania wodą: {water_reckoning_vs_current_income} zł")


    return result

def reload():
    for household in households:
        household.apply_globals()
    for household_type in households_grouped.values():
        household_type.process()
    for household_type in households_not_grouped.values():
        household_type.process()


# Load data from file
start = time.time()
load_data(config.data_csv)
find_missing_people()
end = time.time()
print(f"Czas pierwszego uruchomienia: {round(end - start, 2)} sekund")

display_output()
start = time.time()
print("Przeładowanie")
reload()
end = time.time()
print(f"Czas przeładowania: {round(end - start, 2)} sekund")
# Output
