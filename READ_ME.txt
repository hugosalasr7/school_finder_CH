
Options for running files:

a) To run distances with Google API:
   chmod 775 install.sh
   bash install.sh -d distances.py

b) To run clean up data base:
   chmod 775 install.sh
   bash install.sh -d data_cleanup.py

c) To run only the map:
   chmod 775 install.sh
   bash install.sh

Files:

1) data_cleanup.py
    Location: bokeh_map/
    Purpose: Import and merge several databases from Chile's Ministry of
             Education. Specifically, containing schools basic information, 
             academic performance and test scores. 
    Output:  Generates a CSV file called schools_data.csv that summarizes the information
		 of all schools in Chile and another file called schools_data_SCL.csv 
		 that focuses on Santiago's Metropolitan Region.

2) distances.py
    Location: bokeh_map/
    Purpose: Calculate distances between each comuna's centroid and school.
    Output:  Generates a CSV file called dist_school_comuna.csv, 
             this has info of the driving time and the euclidean 
             distance between each comuna and each school.
3) views.py
	Location: bokeh_map/mysite/
	Purpose: Transform CSV's into geopandas objects and constructs map.
	Output:  html script that manage uses to display map.

4) base.html
	Location: bokeh_map/mysite/templates/pages
	Purpose: Construct the website's skeleton.
	Output:  base html that manage.py uses to display map.

5) manages.py
	Location: bokeh_map/
	Purpose: Execute files views.py and base.html
	Output:  Displays html file in website.