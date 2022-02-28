'''''''''''''''''''''''''''
	Purpose: Calculate distances between each comuna and school.
    Output:  Generates a CSV file called dist_school_comuna.csv, 
             this has info of the driving time and the euclidean 
             distance between each comuna and each school.
	Authors: Hugo Salas, Ana Sofía Muñoz
	Date Last Modified: 3/2/2021
'''''''''''''''''''''''''''
APIKEY = 'AIzaSyDLtL6Gysy2ViK5sR5ww-i-AdIHmsbBlmo'

############# Packages to be used
from datetime import timedelta, datetime
import pandas as pd
import googlemaps
import numpy as np
import haversine as hs

# Paths
raw_data = "data/raw/"
clean_data = "data/clean/"

# Clean database
schools = pd.read_csv(clean_data + "schools_data_SCL.csv", delimiter = ",")
schools = schools.drop(['MRUN', 'RUT_SOSTENEDOR', 'P_JURIDICA','NOM_REG_RBD_A',
                        'COD_PRO_RBD', 'COD_DEPROV_RBD', 'NOM_DEPROV_RBD','COD_DEPE',
                        'COD_DEPE2', 'CONVENIO_PIE', 'ENS_01', 'ENS_02','ENS_03',
                        'ENS_04', 'ENS_05', 'ENS_06', 'ENS_07', 'ENS_08',
                        'ENS_09', 'ENS_10', 'ENS_11', 'MATRICULA',
                        'ESTADO_ESTAB'], axis = 1)
comunas = pd.read_excel(raw_data + "comunas_CL.xlsx")
comunas['REGION'] = comunas['Código Único Territorial'].apply(lambda x: str(x))
comunas['REGION'] = comunas['REGION'].apply(lambda x: x[0:2])
comunas = comunas[comunas['REGION']== '13']


def dms_to_dec(d, m, s):
    '''
    Transform coordinates of communes to correct format

    Input:
       d (int) : degrees
       m (int) : minutes
       s (int) : seconds
    Output: (float) coordinates in decimals
    '''
    sign = np.sign(d)
    return d + sign * m / 60 + sign * s / 3600


def calc_time(longitud_s, latitud_s, longitud_c, latitud_c):
    '''
    Calculates the driving time and distance from a place to another
    using the Google Maps API.

    Inputs:
      longitud_s (float): longitude of place 1
      latitud_s (float): latitude of place 2
      longitud_c (float): longitude of place 2
      longitud_c (float): latitude of place 2
    
    Returns (int): (str) driving time from school s to municipality c
    '''
    school_ubic = str(latitud_s) + ' ' + str(longitud_s)
    comune_ubic = str(latitud_c) + ' ' + str(longitud_c)
    daytime = datetime(2021, 3, 30) 
    daytime.replace(hour=7, minute=30) # We're interested in driving time at 7:30
    gmaps = googlemaps.Client(key= APIKEY)
    directions_result = gmaps.directions(school_ubic, comune_ubic,
                                        mode="driving", avoid="ferries",
                                        departure_time=daytime)
    if directions_result == []:
        return float("NaN")
    try:
        return directions_result[0]['legs'][0]['duration_in_traffic']['text']
    except KeyError:
        return float("NaN")


# Create coordinates
comunas['Long'] = comunas['Longitud'].apply(lambda x: 
                    x.replace("°", "_").replace("'", "_").replace('"', "").split("_"))
comunas['Long'] = comunas['Long'].apply(lambda x: 
                    dms_to_dec(float(x[0]), float(x[1]), float(x[2])))
comunas['Lat'] = comunas['Latitud'].apply(lambda x:
                    x.replace("°", "_").replace("'", "_").replace('"', "").split("_"))
comunas['Lat'] = comunas['Lat'].apply(lambda x: 
                    dms_to_dec(float(x[0]), float(x[1]), float(x[2])))

# Iterate through all schools and communes
directions = []
count, stop_rule, last_rbd_queried = 0 , 5, 10623
index = schools.index[schools['RBD'] == last_rbd_queried]
for _, row in schools.loc[index[0]:].iterrows():
    if row['LONGITUD'] != ' ':
        longitud_s, latitud_s  = float(row['LONGITUD']), float(row['LATITUD'])
        rbd, colegio = int(row['RBD']), row['NOM_RBD']
        for (idx, cod, com, _, _, _, _, _, _, _, _, l_1, l_2) in comunas.itertuples():
            euc = hs.haversine((longitud_s, latitud_s) , (float(l_1), float(l_2)))
            if euc < 15:
                t = calc_time(longitud_s, latitud_s, float(l_1), float(l_2))           
                count += 1
                if (count % 100 == 0):
                    print('Performed ' + str(count) + " queries.")
            else:
                t = float("NaN")
            directions.append({'RBD': rbd, 'TIME': t, 'colegio': colegio, 
                'comuna':  cod, 'name_comuna': com, 'euc_dist_km' : euc})
            if count == stop_rule:
                break
        if count == stop_rule:
            print('     Last school RBD was ' + str(rbd))
            break

directions = pd.DataFrame(directions)
# Append new entries to previous ones
prev_directions = pd.read_csv(clean_data + "dist_school_comuna.csv", delimiter = ",")
directions = prev_directions.append(directions)
directions = directions.drop_duplicates(subset=['RBD', 'comuna'])
directions.to_csv(clean_data +"dist_school_comuna_final.csv", index = False)
