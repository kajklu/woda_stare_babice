# Dokumentacja
## Cel programu
Program ma na celu wyliczenie danych statystycznych potrzebnych do analizy zużycia wody w gminie. Dane są przekształcane i 
przedstawiane pod postacią graficzną. Analizowane są również dane przekroczenia określonego limitu zużycia wody.

## Konfiguracja
Konfiguracja programu odbywa się poprzez ustawienie odpowiednich zmiennych w pliku `config.py`.

### Dane wejściowe
`data_csv` - plik z danymi do analizy w formacie csv. Należy podać jego ścieżkę. 

### Generowanie wykresów
`render_graphs` - czy wygenerować wykresy.

`group_household_types` - czy grupować typy gospodarstw domowych.

`distribution_bins` - liczba przedziałów na wykresach histogramów.

### Analiza danych

`monthly` - tryb analizy. Należy ustawić `True`, jeżeli analiza ma być miesięczna lub `False` dla analizy rocznej.


`monthly_overusage_threshold` - próg nadmiernego zużycia. Należ podać wartość powyżej której zużycie traktowane jest jako podejrzane. 
Dostępne opcje:

    - stała liczba
    - 'sigma+average' - próg określany jako odchylenie standardowe + średnia (wartości dla całej gminy)
    - 'sigma+median' - próg określany jako odchylenie standardowe + mediana (wartości dla całej gminy)
    - 'sigma+mode' - próg określany jako odchylenie standardowe + średnia (wartości dla całej gminy)
    - 'mean' - próg określany jako średnia (wartości dla całej gminy)

`fee` - stawka opłaty za śmieci

`reject_negative_consumption_values` - czy odrzucić dane zużycia wody, w których zużycie jest ujemne. Dostępne opcje:
`True` oraz `False`

`reject_zero_consumption_values` - czy odrzucić dane zużycia wody, w których zużycie jest zerowe. Dostępne opcje:
`True` oraz `False`

`lower_cutoff_percentage` - dolny próg odcięcia zużycia wody. Należy podać wartość procentową (0-100).

`upper_cutoff_percentage` - górny próg odcięcia zużycia wody. Należy podać wartość procentową (0-100).

### Symulacja przejścia na rozliczanie przez zużycie wody
`linear_reckoning_threshold` - próg liniowego rozliczania zużycia wody.

`water_price` - cena za 1 m³ wody.

`base_price` - opłata stała za wodę.



