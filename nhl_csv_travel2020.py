import os
import csv
import requests
import datetime
import glob

STADIUM_XY_LOCATIONS_PATH = "D:\\PythonProjects\\NHLTravel2020\\nhlteams.csv"
DOWN_CSV_PATH = "D:\\PythonProjects\\NHLTravel2020\\csv2020"
TRAVEL_CSV_PATH = "D:\\PythonProjects\\NHLTravel2020\\OutputDir2020"

teams = ["GoldenKnights", "Ducks", "Coyotes", "Bruins", "Sabres", "Flames", "Hurricanes", "Blackhawks", "Avalanche", "BlueJackets",
         "Stars", "Oilers", "RedWings", "Panthers", "Kings", "Wild", "Canadians", "Predators", "Devils",
         "Islanders", "Rangers", "Senators", "Flyers",  "Penguins", "Sharks", "Blues", "Lightning",
         "Leafs", "Canucks", "Capitals", "Jets"]

teamCity= ["Vegas", "Anaheim", "Arizona", "Boston", "Buffalo", "Calgary", "Carolina", "Chicago", "Colorado", "Columbus",
         "Dallas", "Edmonton", "Detroit", "Florida", "Los Angeles", "Minnesota", "Montreal", "Nashville",
         "New Jersey", "Ny Islanders", "Ny Rangers", "Ottawa", "Philadelphia",  "Pittsburgh", 
         "San Jose", "St Louis", "Tampa Bay", "Toronto", "Vancouver", "Washington", "Winnipeg"]

allTogetherNow = {"Vegas":"GoldenKnights","Anaheim":"Ducks","Boston":"Bruins","Buffalo":"Sabres","Calgary":"Flames",
                  "Carolina":"Hurricanes","Chicago":"Blackhawks","Colorado":"Avalanche",
                  "Columbus":"BlueJackets","Dallas":"Stars","Edmonton": "Oilers","Detroit":"RedWings",
                  "Florida":"Panthers","Los Angeles":"Kings","Minnesota":"Wild","Montreal":"Canadiens",
                  "Nashville":"Predators","New Jersey":"Devils","Ny Islanders":"Islanders",
                  "Ny Rangers":"Rangers","Ottawa":"Senators","Philadelphia":"Flyers","Arizona":"Coyotes",
                  "Pittsburgh":"Penguins","San Jose":"Sharks","St Louis": "Blues","Tampa Bay":"Lightning",
                  "Toronto":"MapleLeafs","Vancouver":"Canucks","Washington":"Capitals","Winnipeg": "Jets"}
         

def collectCSV(teams):
    
    for k,v in teams.items():
    
        #http://ducks.ice.nhl.com/schedule/full.csv
        URL = "http://{}.ice.nhl.com/schedule/full.csv".format(v)
        localName = os.path.join(DOWN_CSV_PATH, k + ".csv")
        
        try:
            print("Fetching and saving: {}".format(URL))            
            response = requests.get(URL)
        
            if response.status_code == 200:
                with open(localName, 'wb') as f:
                    for chunk in response:
                        f.write(chunk)
            else:
                print("did not return a 200 on the file get: \n {}".format(response.text))

        except Exception as e:
            print ("problem : \n{}".format(e))
        
        
def makeTeamTravelTables(teamSchedules, teamXYLookUp):

    teamDict = {}
    
    for team in teamSchedules:
        currentTeam = os.path.splitext(os.path.basename(team))[0]
        currentTeam = "St. Louis" if "Louis" in currentTeam else currentTeam
        
        with open(team) as f:
            reader = csv.DictReader(f)

            teamDict[currentTeam] = [] #initialize the team
            # Add the first row for teams to start at home, with a date before season starts
            teamDict[currentTeam].append( (currentTeam, "Null", "Null", "10/1/2021", 0)+ teamXYLookUp[currentTeam] )
            gamesCounted = 0
            flightCounter = 0
            prvCity = currentTeam
            olympicBreak = False         

            for row in reader:
                #Skip pre-season games if any
                if datetime.datetime.strptime(row['START_DATE'], '%m/%d/%Y').date() <= datetime.date(2021, 1, 10):
                    pass
                else: 
                    match_up = row['SUBJECT']
                    away_city = match_up[:match_up.find("at")-1]
                    home_city = match_up[match_up.find("at")+3:]   
                    
                    if prvCity != home_city:
                        prvCity = home_city
                        flightCounter += 1

                    if away_city == currentTeam:                       
                        teamDict[currentTeam].append( (currentTeam, away_city, home_city, row['START_DATE'], flightCounter)+ teamXYLookUp[home_city] )                        
                        gamesCounted += 1
                        
                        # if last game of the season is on the road, finish the team at home                            
                        if gamesCounted == 56:
                            # July 1 is safe guess as to when regular reason will be over
                            teamDict[currentTeam].append( (currentTeam, "Null", "Null", "7/01/2021", flightCounter)+ teamXYLookUp[currentTeam] )
                            
                    else: 
                        # use the coordinates of the team we're processing
                        teamDict[currentTeam].append( (currentTeam, away_city, home_city,  row['START_DATE'], flightCounter)+ teamXYLookUp[currentTeam] )
                        gamesCounted += 1
                        
            print("{} - games: {} - flights: {}".format(currentTeam, gamesCounted, flightCounter ))
      
       
    print ("finished making time csvs")
    return teamDict
        
def writeTravelCSV(teamTravel, outputDir):
    
    for k,v in teamTravel.items():
        resultFile = open(os.path.join(outputDir,k+'.csv'), 'w')
        wr = csv.writer(resultFile, dialect='excel')
        wr.writerows(v)    
    

def setXY(teamListFile):
    ''' Helper function to load up a dict of XY '''

    teamXY = {}
    
    with open(teamListFile, 'r') as f:
        reader = csv.reader(f)
        for row in reader: 
            teamXY[row[6]] = (str(row[4]), str(row[5]))
          
    del reader
    return teamXY     
        
def doArcpyStuff(outputDIR):
    
    import arcpy
    arcpy.env.overwriteOutput = True
    
    gdb = os.path.join(outputDIR, "f.gdb")
    if not arcpy.Exists(gdb):        
        arcpy.CreateFileGDB_management(outputDIR, "f.gdb")    
    
    travelCSV = glob.glob(outputDIR + '\*.csv')
    
    for csv in travelCSV:
        teamName = os.path.splitext(os.path.basename(csv))[0].replace(" ","")
        teamName = teamName.replace('.','')
        print (teamName)
        
        arcpy.MakeXYEventLayer_management(csv,"Field6","Field7",teamName,
                                          "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119522E-09;0.001;0.001;IsHighPrecision","#")
        outputPoint = os.path.join(gdb, teamName + "_pts") #"in_memory\\TempPoint"
        arcpy.CopyFeatures_management(teamName,outputPoint,"#","0","0","0")             
        finalLines = os.path.join(gdb, teamName)
        arcpy.PointsToLine_management(outputPoint,finalLines,"","Field1","NO_CLOSE")
        arcpy.AddField_management(finalLines, "distance", "DOUBLE")
        arcpy.AddField_management(finalLines, "team", "TEXT", 50)
        arcpy.CalculateField_management(finalLines,"team", "\'"+teamName+"\'","PYTHON_9.3")
        arcpy.CalculateField_management(finalLines,"distance","!shape.length@kilometers!","PYTHON_9.3","#")
        
        
    return gdb
    
def mergeFCs(gdb): 
    
    import arcpy
    print("merging fcs")
    feature_classes = []
    walk = arcpy.da.Walk(gdb, datatype="FeatureClass", type="Polyline")

    for dirpath, dirnames, filenames in walk:
        for filename in filenames:
            if filename != "_finalLine":            
                feature_classes.append(os.path.join(dirpath, filename))
    
    finalFC = os.path.join(gdb, "_finalLine")
    arcpy.Merge_management(feature_classes, finalFC)   
    
        
if __name__ == "__main__": 

    #Set the XY Values for
    teamXYLookUp = setXY(STADIUM_XY_LOCATIONS_PATH)
    
    #download team csv's from the www -- set to True if you dont have these. (This wont capture Vegas)
    #  Vegas >> https://gist.github.com/eito/92a5ce0ae2425513d53096633c50f4b1
    if False:
        collectCSV(allTogetherNow)   
    
    #gather list of csv teams    
    teamSchedules = glob.glob(os.path.join(DOWN_CSV_PATH, '*.csv'))
    
    teamTravel = makeTeamTravelTables(teamSchedules, teamXYLookUp)
    
    writeTravelCSV(teamTravel, TRAVEL_CSV_PATH)
    
    if True:
        # arcpy: make lines, merge them into single FC
        gdb = doArcpyStuff(TRAVEL_CSV_PATH)
        mergeFCs(gdb)
    
    
 