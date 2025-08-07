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