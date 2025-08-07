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
reject_zero_consumption_values = True

# Display parameters
distribution_bins = 120

if monthly:
    divider = 12
else:
    divider = 1