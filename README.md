# Dokumentacja
## Cel programu
Program ma na celu wyliczenie danych statystycznych potrzebnych do analizy zużycia wody w gminie. Dane są przekształcane i 
przedstawiane pod postacią graficzną. Analizowane są również dane przekroczenia określonego limitu zużycia wody.

## Konfiguracja
`data_file` - plik z danymi do analizy. Należy podać jego ścieżkę. 

`monthly` - tryb analizy. Należy ustawić `True`, jeżeli analiza ma być miesięczna lub `False` dla analizy rocznej.

`overusage_threshold` - próg nadmiernego zużycia. Należ podać wartość powyżej której zużycie traktowane jest jako podejrzane. 
Dostępne opcje:

    - stała liczba
    - 'sigma+average' - próg określany jako odchylenie standardowe + średnia (wartości dla całej gminy)
    - 'sigma+median' - próg określany jako odchylenie standardowe + mediana (wartości dla całej gminy)
    - 'sigma+mode' - próg określany jako odchylenie standardowe + średnia (wartości dla całej gminy)


`fee` - stawka opłaty za śmieci

`reject_negative_consumption_values` - czy odrzucić dane zużycia wody, w których zużycie jest ujemne. Dostępne opcje:
`True` oraz `False`

`reject_null_consumption_values` - czy odrzucić dane zużycia wody, w których zużycie nie zostało wpiasne. Dostępne opcje:
`True` oraz `False`

`reject_zero_consumption_values` - czy odrzucić dane zużycia wody, w których zużycie jest zerowe. Dostępne opcje:
`True` oraz `False`

`reject_population_with_negative_consumption` - czy odrzucić dane populacji, w których zużycie wody jest ujemne. Dostępne opcje:
`True` oraz `False`

`reject_population_with_null_consumption` - czy odrzucić dane populacji, w których zużycie wody nie zostało wpisane. Dostępne opcje:
`True` oraz `False`

`reject_population_with_zero_consumption` - czy odrzucić dane populacji, w których zużycie wody jest zerowe. Dostępne opcje:
`True` oraz `False`

## Omówienie kodu i metodyka

### Funkcje matematyczne

Funkcje `mode(values)`, `median(values)`, `mean(values)` oraz `sigma(values)` jako argument przyjmują listę wartości i zwracają odpowiednio dominantę, 
medianę, średnią i odchylenie standardowe

### Przetwarzanie danych
`process_water_consumption(household)` - funkcja ta jako argument przyjmuje gospodarstwo domowe i dodaje do niego informacje
czy należy analizować zużycie wody przez to gospodarstwo w zależności od ustawionych w konfiguracji flag.

`process_population(household)` - funkcja ta jako argument przyjmuje gospodarstwo domowe i dodaje do niego informacje
czy należy analizować liczbę domowników tego gospodarstwa w zależności od ustawionych w konfiguracji flag.

`process_global_variables()` - w tym fragmencie kodu przetwarzane są dane globalne tj. zużycie wody przez gminę, średnie
zużycie wody na mieszkańca, liczba mieszkańców, oraz dane statystyczne dla poszczególnych typów gospodarstw domowych

`count_considered_households()` - oblicza liczbę gospodarstw domowych spełniających warunki określone w konfiguracji.

### Obliczanie danych statystycznych dla gminy
`calculate_commune_population_mode()` - obliczenie dominanty średniego zużycia wody dla populacji gminy.
Dominanta ta określa jaką średnią ilość wody zużywa największa liczba mieszkańców.

`calculate_commune_household_mode()` - obliczenie dominanty średniego zużycia wody dla gospodarstw domowych w gminie.
Dominanta ta określa jaką średnią ilość wody zużywa największa liczba gospodarstw domowych.

`calculate_commune_sigma()` - obliczenie odchylenia standardowego zużycia wody dla populacji gminy.

`calculate_commune_median()` - obliczenie mediany (wartości środkowej) zużycia wody dla populacji gminy.


### Funkcje znajdujące nadmierne zużycia
`count_overusage_by_cities()` - pozwala na wyliczenie gospodarstw domowych z nadmiarowych zużyciem w poszczególnych
miejscowościach.

`count_missing_people()` - wylicza liczbę osób, których brakuje w danym domostwie, aby średnie tego domostwa mieściły się
w dopuszczalnym limicie.

`count_missing_money(missing_people)` - wylicza stratę pieniężną ze względu na niezadeklarowanie brakujących osób.

`check_overusage(household)` - sprawdza, czy dane gospodarstwo przekracza określony w konfiguracji maksymalny próg zużycia wody.

### Wykreślanie wykresów

`plot_histogram_households_average()` - sporządza wykres histogramu ilości gospodarstw domowych zużywających określoną 
ilość wody na mieszkańców.

`plot_histogram_households_total()` - sporządza wykres histogramu ilości gospodarstw domowych zużywających określoną 
ilość wody.

`plot_histogram_population_average()` - sporządza wykres histogramu liczby osób zużywających określoną ilość wody.

`plot_average_water_consumption_vs_household_population()` - sporządza wykres zależności zużycia wody od liczby osób 
zamieszkujących gospodarstwo domowe.

### Drukowanie wyników
`print_table()` - drukuje wyniki danych statystycznych dla poszczególnych typów gospodarstw domowych.



