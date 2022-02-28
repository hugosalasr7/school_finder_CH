'''''''''''''''''''''''''''
	Purpose: Import and merge several databases from Chile's Ministry of
             Education. Specifically, information containing school basic
             information, performance and standarized test scores (SIMCE).
    Output:  Generates a CSV file called schools.csv that includes all
             the relevant information for each school at the national level,
             and schools_data_SCL.csv for the Metropolitan Region.
	Authors: Antonia Sanhueza
	Date Last Modified: 3/17/2021
'''''''''''''''''''''''''''

import pandas as pd

# Paths
raw_data = 'data/raw/'
clean_data = 'data/clean/'

# Import data
schools = pd.read_csv(raw_data +
    '20200925_Directorio_Oficial_EE_2020_20200430_WEB.csv', delimiter=';')
comunas = pd.read_excel(
      raw_data + 'comunas_CL.xlsx')[['Código Único Territorial', 'Comuna']]
performance = pd.read_excel(
    raw_data + 'CDB2019.xlsx')[['RBD', 'Categoría Desempeño 2019']]
simce_2m = pd.read_excel( raw_data + 'simce2m2018_rbd_publica_final.xlsx')[
			['agno','rbd','cod_com_rbd','prom_lect2m_rbd','prom_mate2m_rbd',
			 'prom_nat2m_rbd']]
simce_8b = pd.read_excel(raw_data + 'simce8b2019_rbd.xlsx')[
        	['agno', 'rbd', 'cod_com_rbd', 'prom_lect8b_rbd', 'prom_mate8b_rbd',
		 	 'prom_soc8b_rbd']]
simce_4b = pd.read_excel(raw_data + 'simce4b2018_rbd_publica_final.xlsx')[
    ['agno', 'rbd', 'cod_com_rbd', 'prom_lect4b_rbd', 'prom_mate4b_rbd']]

# Cleaning schools data
schools['RURAL_RBD'].replace({0: 'Urbano', 1: 'Rural'}, inplace=True)
schools['ORI_RELIGIOSA'].replace({1: 'Laica', 2: 'Católica', 3: 'Evangélica',
                                  4: 'Musulmana', 5: 'Judía', 6: 'Budista',
                                  7: 'No especificada', 9: 'Sin información'},
                                 inplace=True)
schools['PAGO_MATRICULA'].replace({0: 'Sin información',
                                   1: 'Gratuito',
                                   2: '$1.000 a 10.000',
                                   3: '$10.001 a $25.000',
                                   4: '$25.001 a $50.000',
                                   5: '$50.001 a $100.000',
                                   6: 'Más de $100.000'},
                                  inplace=True)
schools['PAGO_MENSUAL'].replace({0: 'Sin información',
                                 1: 'Gratuito',
                                 2: '$1.000 a 10.000',
                                 3: '$10.001 a $25.000',
                                 4: '$25.001 a $50.000',
                                 5: '$50.001 a $100.000',
                                 6: 'Más de $100.000'},
                                inplace=True)

teaching_codes = ['ENS_01', 'ENS_02', 'ENS_03', 'ENS_04', 'ENS_05', 'ENS_06',
                  'ENS_07', 'ENS_08', 'ENS_09', 'ENS_10', 'ENS_11']

for col in teaching_codes:
    schools[col].replace(
        {    0: 'No Aplica',
            10: 'Educación Parvularia',
            110: 'Educación Básica',
            160: 'Educación Básica Común Adultos',
            161: 'EDucación Básica Especial Adultos',
            163: 'Escuelas Cárceles (Básica Adultos)',
            165: 'Educación Básica Adultos Sin Oficios',
            167: 'Educación Básica Adultos Con Oficios',
            211: 'Educación Especial Discapacidad Auditiva',
            212: 'Educación Especial Discapacidad Intelectual',
            213: 'Educación Especial Discapacidad Visual',
            214: 'Educación Especial Trastornos Específicos del Lenguaje',
            215: 'Educación Especial Trastornos Motores',
            216: 'Educación Especial Trastornos Motores',
            217: 'Educación Especial Discapcidad Graves Alteraciones en la Capacidad de Relación y Comunicación',
            218: '218',
            219: '219',
            299: 'Opción 4 Programa Integración Escolar',
            310: 'Enseñanza Media H-C niños y jóvenes',
            360: 'Educación Medica H-C adultos vespertino y nocturno',
            361: 'Educación Media H-C adultos',
            362: 'Escuela Cárceles',
            363: 'Educación Media H-C Adultos',
            410: 'Enseñanza Media T-P Comercial Niños y Jóvenes',
            460: 'Educación Media T-P Comercial Adultos',
            461: 'Educación Media T-P Comercial Adultos',
            463: 'Educación Media T-P Comercial Adultos',
            510: 'Enseñanza Media T-P Industrial Niños y Jóvenes',
            560: 'Educación Media T-P Industrial Adultos',
            561: 'Educación Media T-P Industrial Adultos',
            563: 'Educación Media T-P Industrial Adultos',
            610: 'Enseñanza Media T-P Técnica Niños y Jóvenes',
            660: 'Educación Media T-P Técnica Adultos',
            661: 'Educación Media T-P Técnica Adultos',
            663: 'Educación Media T-P Técnica Adultos',
            710: 'Enseñanza Media T-P Agrícola Niños y Jóvenes',
            760: 'Educación Media T-P Agrícola Adultos',
            761: 'Educación Media T-P Agrícola Adultos',
            763: 'Educación Media T-P Agrícola Adultos',
            810: 'Enseñanza Media T-P Marítima Niños y Jóvenes',
            860: 'Enseñanza Media T-P Marítima Adultos',
            863: 'Enseñanza Media T-P Marítima Adultos',
            910: 'Enseñanza Media Artística Niños y Jóvenes',
            963: 'Enseñanza Media Artística Adultos'},
        inplace=True)

school_level = schools.loc[:, teaching_codes]
schools['all_levels'] = school_level.apply(lambda x: '/'.join(x), axis=1)

# Merges

# Combine all SIMCE's db
merge_simce = pd.merge(simce_2m, simce_8b, on='rbd', how='outer',
                       suffixes=['_2m', '_8b'])
merge_simce = pd.merge(merge_simce, simce_4b, on='rbd', how='outer')

# Leaving only one municipality variable
merge_simce.drop(['cod_com_rbd_2m', 'cod_com_rbd_8b', 'cod_com_rbd'],
                 inplace=True, axis=1)

# Create a new db w/info from all schools
schools_c = schools.merge(comunas, left_on='COD_COM_RBD',
								right_on='Código Único Territorial', how='left')
schools_cp = schools_c.merge(performance, on='RBD', how='left')
school_cps = schools_cp.merge(merge_simce, left_on='RBD', right_on='rbd', how='left')
school_cps.rename(columns={'Código Único Territorial': 'cod_comuna',
        		'Categoría Desempeño 2019': 'cat_desempeno_2019'}, inplace=True)

# Extra cleaning
school_cps = school_cps[school_cps['LATITUD'] != ' '][school_cps['LONGITUD'] != ' ']
school_cps['LONGITUD'] = pd.to_numeric(school_cps['LONGITUD'])
school_cps['LATITUD'] = pd.to_numeric(school_cps['LATITUD'])
school_cps['ORI_RELIGIOSA'] = school_cps['ORI_RELIGIOSA'].str.upper()
school_cps['RURAL_RBD'] = school_cps['RURAL_RBD'].str.upper()
school_cps['cat_desempeno_2019'] = school_cps['cat_desempeno_2019'].fillna(
									'SIN CATEGORIA: FALTA DE INFORMACIÓN')

# Export DB
school_cps.to_csv(clean_data + 'schools_data.csv', index=False)
# Export DB for only the Metropolitan Region
schools_santiago = school_cps[school_cps['COD_REG_RBD'] == 13]
schools_santiago.to_csv(clean_data + 'schools_data_SCL.csv', index=False)
