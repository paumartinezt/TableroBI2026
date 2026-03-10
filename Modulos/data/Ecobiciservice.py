import pandas as pd
import requests


def cargar_estaciones():

    # dataset 1
    url_stations = "https://gbfs.mex.lyftbikes.com/gbfs/es/station_information.json"
    response = requests.get(url_stations)
    data = response.json()

    df = pd.DataFrame(data['data']['stations'])
    df = df[['station_id', 'name', 'lat', 'lon', 'capacity']]

    # dataset 2
    url_station_status = "https://gbfs.mex.lyftbikes.com/gbfs/es/station_status.json"
    response_station_status = requests.get(url_station_status)

    station_status = response_station_status.json()
    df_status = pd.DataFrame(station_status['data']['stations'])

    columnas = [
        'num_bikes_available',
        'num_bikes_disabled',
        'num_docks_available',
        'num_docks_disabled'
    ]

    df_status = df_status[columnas]

    df_final = pd.concat([df, df_status], axis=1)

    return df_final
