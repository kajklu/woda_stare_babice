import ssl
ssl._create_default_https_context = ssl._create_unverified_context

from flask import Flask, render_template, request
import importlib
import main
import config

app = Flask(__name__)
app.secret_key = 'woda'

def reload():
    importlib.reload(main)
    missing_statistics, household_types, commune = main.reload_and_get_data()
    households_list = [commune] + list(household_types.values())

    for i in range(len(households_list)):
        households_list[i] = households_list[i].json(True)
    return missing_statistics, households_list

missing_statistics, households = reload()
@app.route('/', methods=['GET', 'POST'])
def statystyki_wody():
    global missing_statistics, households
    if request.method == 'POST':
        config.group_household_types = request.form.get('group_households') == 'True'
        config.use_town_hall_averages = request.form.get('use_town_hall_calculations') == 'True'
        config.reject_non_yearly_consumption_values = request.form.get(
            'reject_non_yearly_consumption_values') == 'True'
        config.monthly_overusage_threshold = float(request.form.get('monthly_overusage_threshold'))
        config.monthly = request.form.get('monthly') == 'True'
        # Wybór listy gospodarstw zależnie od stanu checkboxa
        missing_statistics, households = reload()
        return render_template("home.html", active_page = 'Woda', households=households, config=config,
                               missing_statistics=missing_statistics)
    return render_template("home.html", active_page = 'Woda', households=households, config=config, missing_statistics=missing_statistics)

# -----------------------------



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
