# School Finder in Santiago, Chile
An application based on Django that helps parents find the closest schools available in Chile’s Metropolitan Region. This uses information from Chile's Ministry of Education and calculations made with Google Maps' API. The idea is that a parent can easily input the municipality where he/she lives and certain filters (public/private, urban/rural, religious orientation, elementary/middle/high school) and find the closest schools available. The output is a map with the locations and attributes of the schools close by. These attributes contain each school's name, most recent academic performance, school fees, religious affiliation and driving time from the input municipality. For more information on its functionality, please watch this video: [url](https://github.com/hugosalasr7/school_finder_CH/blob/main/Images%20%26%20Video/vid_sample_sfCH.mp4).

<p align="center">
  <img src="https://github.com/hugosalasr7/school_finder_CH/blob/main/Images%20%26%20Video/Screenshot%202022-02-27%20215729.png" alt="drawing" width="400" />
</p>

### On the map: 

- A point icon indicates the location of the school and the color corresponds to the schools’ performance classification.
- The user can view information about a school by running the cursor over the point. The information provided inside corresponds to:
  1. Nombre: name of the school.
  2. Urbano/rural: if the school is in an urban or rural area.
  3. Driving time: calculated time it would take to drive from the centroid of the selected municipality to the school at 7:30 am (in Chile school starts at 8 am). We calculated this using Python and Google Maps API.
  4. Pago Matrícula: range of tuition fee paid once a year. “Gratuito” if it is a public school.
  5. Pago Mensual: range of tuition paid monthly. “Gratuito” if it is a public school.
  6. Categoría desempeño 2019: Ministry of Education’s school performance classification.
  7. Orientación Religiosa: school’s religious orientation.
  8. SIMCE: schools scores in the last standardized national level test. This indicator is divided into several variables. First, it is divided between math and language scores. Second, it has one value for high school (2m) and another value for middle school (8b and 4b).

## Relevant files

1) data_cleanup.py
    - Location:
    - Purpose: Import and merge several databases from Chile's Ministry of Education. Specifically, containing schools basic information, academic performance and test scores.
    - Output:  Generates a CSV file called schools_data.csv that summarizes the information of all schools in Chile and another file called schools_data_SCL.csv that focuses on Santiago's Metropolitan Region.

2) distances.py
    - Location:
    - Purpose: Calculate distances between each comuna's centroid and school.
    - Output:  Generates a CSV file called dist_school_comuna.csv, this has info of the driving time and the euclidean distance between each comuna and each school.

3) views.py
    - Location:
    - Purpose: Transform CSV's into geopandas objects and constructs map.
    - Output: html script that manage uses to display map.

4) base.html
    - Location: mysite/templates/pages
    - Purpose: Construct the website's skeleton.
    - Output: base html that manage.py uses to display map.

5) manages.py
    - Location: mysite/templates/pages
    - Purpose: Execute files views.py and base.html
    - Output: Displays html file in website.

## To run on local host 
```
chmod 775 install.sh
bash install.sh
```
