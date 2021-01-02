# NHL-Travel-Calculator
Calculate NHL teams travel over the course of a season

Python script that pulls down CSV files for each team's schedule. From this schedule, new CSV files for each team and where they're travelling to is created. From these points, lines and distances are determined.

The location the CSVs are pulled from do not include Vegas and probably wont include Seattle next year. The API is probably not maintained but somehow generates the required CSV files for each year.

Inside the ZIP file is a fGDB (file geodatabase) of each team travel points and the lines. 

Use the CSV file, `nhlteam.csv` for stadium XY locations.
