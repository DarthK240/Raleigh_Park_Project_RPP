# Packages needed for project
import requests
import pandas as pd
import matplotlib.pyplot as plt
import mplcursors
import numpy as np
import PySimpleGUI as Sg

# Importing API and initializing Dataframe
response = requests.get('https://services1.arcgis.com/a7CWfuGP5ZnLYE7I/arcgis/rest/services/Wake_Parks_Public/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json')

response_data = response.json()
parks = response_data['features']
column_names = list(parks[0]['attributes'].keys()) + ['Longitude', 'Latitude']
feature_columns = column_names[9:30]
parks_features = pd.DataFrame()

# Taking data from API and concatenating into DataFrame
for park in parks:
    hello = park['attributes']
    location = park['geometry']
    attributes = list(hello.values())
    coordinates = list(location.values())
    all_values = pd.Series(attributes+coordinates)

    row_df = pd.DataFrame([all_values])
    parks_features = pd.concat([row_df, parks_features], ignore_index=True)

# Renaming columns for DataFrame(Column names were previously integers)
old_names = parks_features.columns
old_new = dict()
for i in old_names:
    old_new.update({i: column_names[i]})

parks_features = parks_features.rename(columns=old_new)

# Establishing all Parks, all Row indexes, and ScatterPlot Title *DEFAULT*
wanted_parks = list(parks_features.loc[:, 'NAME'])
wanted_rows = list(parks_features.index.values)
plot_title = 'All Parks in Raleigh and Surrounding Areas'


# Defining function which creates ScatterPlot
def park_plotter(features, rows, title, f_parks):
    geo_lat = np.array([features.loc[z, 'Latitude'] for z in rows])
    geo_lon = np.array([features.loc[z, 'Longitude'] for z in rows])

    map_image = plt.imread('/Users/kavithsr/Downloads/Chiggi Coderdojo Project/raleigh_map.png')

    bbox = ((features.loc[:, 'Longitude'].min() - 0.07, features.loc[:, 'Longitude'].max() + 0.07,
            features.loc[:, 'Latitude'].min() - 0.07, features.loc[:, 'Latitude'].max() + 0.07))

    fig, ax = plt.subplots(figsize=(8, 7))
    ax.set_title(title)
    ax.set_xlim(bbox[0], bbox[1])
    ax.set_ylim(bbox[2], bbox[3])
    ax.scatter(geo_lon, geo_lat, zorder=2)

    mplcursors.cursor(ax).connect(
        "add", lambda sel: sel.annotation.set_text(f_parks[sel.target.index]))

    ax.imshow(map_image, extent=bbox, aspect='equal', zorder=1)

    plt.show()


user_input = None

# PySimpleGUI Code
Sg.theme('DarkAmber')
layout = [[Sg.Combo(feature_columns, enable_events=True, key='combo', size=(300, 300))],
          [Sg.Button(button_text='Plot'), Sg.Exit()]]
window = Sg.Window('Park Mapper', layout, size=(500, 500))

while True:
    event, values = window.Read()
    # When the 'Exit' button on the UI is clicked
    if event is None or event == 'Exit':
        break
    # When the 'Plot' button on the UI is clicked
    if event == 'Plot':
        combo = values['combo']
        # Seting user_input to whatever the User chooses, and taking the Park Names and lat/long for that choice
        user_input = combo
        if user_input:
            flags = parks_features.loc[:, user_input].tolist()
            wanted_parks = []
            wanted_rows = []
            for x_index, x in enumerate(flags):
                if x == 'Yes':
                    wanted_rows.append(x_index)
                    wanted_parks.append(parks_features.loc[x_index, 'NAME'])
            plot_title = 'Parks in the RTP area That Offer: ' + user_input
        # Calling function
        park_plotter(parks_features, wanted_rows, plot_title, wanted_parks)

window.close()

# This part of the code was an attempt at me trying to manually input all of the column names in the pandas DataFrame,
# before my dad showed me how to loop through them lol. Sad mistake on my part, wasted too much time.
'''
    attributes = pd.Series(
        [hello['NAME'], loc['y'], loc['x'], hello['ADDRESS'], hello['URL'], hello['PHONE'], hello['ARTSCENTER'], 
         hello['BALLFIELDS'],
         hello['BOATRENTAL'], hello['CANOE'], hello['DISCGOLF'], hello['DOGPARK'], hello['ENVCTR'],
         hello['FISHING'], hello['GREENWAYACCESS'], hello['GYM'], hello['MULTIPURPOSEFIELD'],
         hello['OUTDOORBASKETBALL'], hello['PICNICSHELTER'], hello['PLAYGROUND'], hello['POOL'],
         hello['COMMUNITYCENTER'],
         hello['NEIGHBORHOODCENTER'], hello['TENNISCOURTS'], hello['TRACK'], hello['WALKINGTRAILS'], hello['RESTROOMS'],
         hello['AMUSEMENTTRAIN'], hello['CAROUSEL'], hello['TENNISCENTER'], hello['THEATER'], hello['BOCCE'],
         hello['HANDBALL'], hello['HORSESHOE'], hello['INLINESKATING'], hello['SANDVOLLEYBALL'], hello['SKATEPARK'],
         hello['BMXTRACK'], hello['BOATRIDE'], hello['LIBRARY'], hello['MUSEUM'], hello['TEEN'], hello['BIKING'],
         hello['LIVEANIMALS'], hello['GARDENS'], hello['EQUESTRIAN'], hello['CAMPING']])
    '''
