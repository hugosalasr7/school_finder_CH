'''''''''''''''''''''''''''
	Purpose: Generates the function that will create the map.
    Output:  A map that is used by the HTML file to display.
	Authors: Ana Sofía Muñoz, Antonia Sanhueza, Hugo Salas
	Date Last Modified: 3/17/2021
'''''''''''''''''''''''''''

from django.shortcuts import render
import descartes
import matplotlib.pyplot as plt
import geopandas as gpd
import contextily as ctx
import bokeh
from shapely.geometry import Point
from pyproj import Proj, CRS, Transformer, transform
from bokeh.plotting import gmap
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure, save, output_file, show
from bokeh.tile_providers import OSM, get_provider
from bokeh.embed import components
import pandas as pd

############# Paths #######################
raw_data = 'data/raw/'
clean_data = 'data/clean/'
gis_data = raw_data + 'GIS/'

# Import relevant databases
schools = pd.read_csv(clean_data + 'schools_data_SCL.csv', delimiter=',')
schools.fillna('-', inplace=True)
schools_dist = pd.read_csv(
    clean_data +
    'dist_school_comuna.csv',
    delimiter=',')

# Transform driving time into minutes
temp = schools_dist['TIME'].str.split(pat=' ', expand=True)
temp = temp.rename(columns = {0: 'min', 1: 'min2', 2: 'hrs', 3 : 'hrs2'}, inplace = False)
for (idx, min_, min_2, hrs_, hrs_2) in temp.itertuples():
    if min_2 in ['mins', 'min']:
        temp.iloc[idx, 1] = 1
    elif min_2 in ['hours', 'hour']:
        temp.iloc[idx, 1] = 60
    else:
        temp.iloc[idx, 1] = 0
        temp.iloc[idx, 0] = 0
    if type(hrs_) is str and type(hrs_) != float('NaN'):
        temp.iloc[idx, 2] = int(hrs_)
    else:
        temp.iloc[idx, 2] = 0       
temp['min'] = pd.to_numeric(temp['min'], downcast="float")
temp['TIME_min'] = temp['min'] * temp['min2'] + temp['hrs'] 
temp['TIME_min'] = pd.to_numeric(temp['TIME_min'], downcast="float")
schools_dist['TIME_min'] = temp['TIME_min']
schools_dist['name_comuna'] = schools_dist['name_comuna'].str.upper()

def homepage(request):
    # Gather the information from each request to inputs
    inputs_lst = ['comuna', 'urbrur', 'pubpriv', 'ori_religiosa', 'niv_educ']
    inputs_html = {input: '' for input in inputs_lst}
    if request.method == 'POST':
        for input in inputs_lst:
            inputs_html[input] = request.POST.get(input)
            print(input, ':', inputs_html.get(input))

    # Filter: Subset schools data so it matches the filters used
    s_schools = schools.copy()
    if inputs_html.get('urbrur') != '':
        s_schools = s_schools[s_schools['RURAL_RBD'] == inputs_html.get('urbrur')]
    if inputs_html.get('ori_religiosa') != '':
        s_schools = s_schools[s_schools['ORI_RELIGIOSA'] == \
                              inputs_html.get('ori_religiosa')]
    if inputs_html.get('pubpriv') != '':
        if inputs_html.get('pubpriv') == 'PÚBLICA':
            s_schools = s_schools[(s_schools['PAGO_MENSUAL'] == 'GRATUITO') | (
                                   s_schools['PAGO_MATRICULA'] == 'GRATUITO')]
        else:
            s_schools = s_schools[(s_schools['PAGO_MENSUAL'] != 'GRATUITO') | (
                                   s_schools['PAGO_MATRICULA'] != 'GRATUITO')]
    if inputs_html.get('niv_educ') != '':
        s_schools = s_schools[s_schools['all_levels'].astype(str).str.contains(
                                        inputs_html.get('niv_educ'), case=False)]
    if inputs_html.get('comuna') != '':
        schools_near = set(schools_dist[(schools_dist['name_comuna'] == \
            inputs_html.get('comuna')) & (schools_dist['TIME'].notnull()
            )].sort_values(by = 'TIME_min').head(15)['RBD'])
        s_schools = s_schools.loc[s_schools['RBD'].isin(schools_near)]

    if s_schools.empty:
        div = 'There are no schools that match those characteristics'
        return render(request, 'pages/base.html', {'script': '', 'div': div})

    s_schools = pd.merge(s_schools, schools_dist[schools_dist['name_comuna'] == \
						             inputs_html.get('comuna')][['TIME', 'RBD']],
                        on='RBD', how='left')
    s_schools['TIME'] = s_schools['TIME'].fillna('No se especificó comuna')

    # Set up GIS
    # Create points based on each school
    transformer = Transformer.from_crs('epsg:4326', 'epsg:3857')
    points_schools = [
        transformer.transform(
            row['LATITUD'],
            row['LONGITUD']) for index,
        row in s_schools.iterrows()]

    # Import Shapefile and make points a geoDF
    points_schools = [Point(x, y) for x, y in points_schools]

    # Dataframe for bukeh
    s_schools['geometry'] = points_schools
    geo_df2 = gpd.GeoDataFrame(s_schools, crs='EPSG:3857')
    # get x and y of points
    geo_df2['x'] = geo_df2['geometry'].apply(lambda point: point.x)
    geo_df2['y'] = geo_df2['geometry'].apply(lambda point: point.y)
    # make copy of geometry and drop it from df
    points_df = geo_df2.drop('geometry', axis=1).copy()

    psource_bad = ColumnDataSource(
        points_df[points_df['cat_desempeno_2019'] == 'MEDIO-BAJO'])
    psource_average = ColumnDataSource(
		points_df[points_df['cat_desempeno_2019'] == 'MEDIO'])
    psource_nocat = ColumnDataSource(points_df[(
	points_df['cat_desempeno_2019'] == 'SIN CATEGORIA: BAJA MATRICULA') |
	    (points_df['cat_desempeno_2019'] == 'SIN CATEGORIA: FALTA DE INFORMACIÓN')])
    psource_good = ColumnDataSource(
        points_df[points_df['cat_desempeno_2019'] == 'ALTO'])
    psource_bad_bad = ColumnDataSource(
        points_df[points_df['cat_desempeno_2019'] == 'INSUFICIENTE'])

    # Colors for each point vary depending on school's quality classification
    points_figure = figure(title='Schools of Chile')
    points_figure.circle(
		'x',
		'y',
		source = psource_good, color = 'green',
        size = 12,
		legend_label = 'High performance')
    points_figure.circle(
        'x',
        'y',
        source = psource_average,
        color = 'yellow',
        size = 12,
        legend_label = 'Medium performance')
    points_figure.circle(
        'x',
        'y',
        source = psource_bad,
        color = 'red',
        size = 12,
        legend_label = 'Medium-low performance')
    points_figure.circle(
        'x',
        'y',
        source = psource_bad_bad,
        color = 'black',
        size = 12,
        legend_label = 'Deficient performance')
    points_figure.circle(
        'x',
        'y',
        source = psource_nocat,
        color = 'grey',
        size = 12,
        legend_label = 'Not classified')

    # Initialize tool
    my_hover = HoverTool()
    my_hover.tooltips = [('Nombre', '@NOM_RBD'),
                         ('Tiempo de manejo', '@TIME'),
                         ('Orientación religiosa', '@ORI_RELIGIOSA'),
                         ('Pago matrícula', '@PAGO_MATRICULA'),
                         ('Pago mensual', '@PAGO_MENSUAL'),
                         ('Categorīa desempeńo 2019', '@cat_desempeno_2019'),
                         ('SIMCE Lenguaje 2018 2m', '@prom_lect2m_rbd'),
                         ('SIMCE Matemáticas 2018 2m', '@prom_mate2m_rbd'),
                         ('SIMCE Lenguaje 2019 8b', '@prom_lect8b_rbd'),
                         ('SIMCE Matemáticas 2019 8b', '@prom_mate8b_rbd'),
                         ('SIMCE Lenguaje 2018 4b', '@prom_lect4b_rbd'),
                         ('SIMCE Matemáticas 2018 4b', '@prom_mate4b_rbd')]

    points_figure.add_tools(my_hover)
    tile_provider = get_provider(OSM)
    points_figure.add_tile(tile_provider)
    script, div = components(points_figure)
    return render(request, 'pages/base.html', {'script': script, 'div': div})
