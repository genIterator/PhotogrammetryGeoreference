######################
# ver 0.1
# Python 3.4
#
# Reads geodata from a file and adds the elevation data using the google elevation api:
# https://developers.google.com/maps/documentation/elevation/intro
#
# The Elevation API has the following limits in place:
#
# Users of the free API:
#
#        2500 requests per 24 hour period.
#        512 locations per request.
#        5 requests per second. 
#
# Google Maps API for Work customers:
#
#        100 000 requests per 24 hour period.
#        512 locations per request.
#        10 requests per second. 
#
#
######################

######################
#
# JSON response for request:
#https://maps.googleapis.com/maps/api/elevation/json?&locations=40.714728,-73.998672|-34.397,150.644
#
#{
#   "results" : [
#      {
#         "elevation" : 8.883694648742676,
#         "location" : {
#            "lat" : 40.714728,
#            "lng" : -73.998672
#         },
#         "resolution" : 76.35161590576172
#      },
#      {
#         "elevation" : 392.5118713378906,
#         "location" : {
#            "lat" : -34.397,
#            "lng" : 150.644
#         },
#         "resolution" : 152.7032318115234
#      }
#   ],
#   "status" : "OK"
#}
#
######################


import urllib.request
import requests
import json
import glob
import os
import shutil
import sys



def getGeoDataFile (tempFileName):    
    if glob.glob(tempFileName):
        print("Datei gefunden.")
        return tempFileName
    else:
        fileName = ""
        weiter = True
        while (weiter):
            fileName = input("Bitte den Dateinamen angeben (z.B. geodata.txt):")
            if glob.glob(fileName):
                weiter = False
                print("Datei gefunden.")
                return fileName
            else:
                print("Datei im aktuellen Ordner nicht gefunden.")

def readGeoDataFile(fileName):
    
    geoData = []
    counter = 0
    
    if fileName is not None:
        f = open(fileName, 'r')        
        for line in f:
            if line != "":
                counter += 1
                geoData.append(line)                
        print(str(counter) + " Zeilen gelesen.")
        return geoData
    else:
        print("Dateiname ist None!")
        return

            
def createGeoDataString (geoData):
    
    geodataString = ""
    lineNr = 0
    for line in geoData:        
        temp = line.strip().split(",")
        lineNr += 1
        if len(temp) >= 3:
            if lineNr == 512: # reached 512 limit for free google elevation API
                print("Limit von 512 locations für den Request erreicht.")
                print("511 Locations werden übermittelt...")
                #TODO: split data into 512 chunks an transmit data this way...
                return geodataString
            if lineNr == 1:
                geodataString = geodataString + "&locations="+ temp[1] + "," + temp[2]
            else:
                geodataString = geodataString + "|" + temp[1] + "," + temp[2]                                           
        else:
            print("Zeile " + str(lineNr) + "nicht geparsed!")
    return geodataString

def getGoogleElevationData (geoData):
    testUrl = "http://maps.googleapis.com/maps/api/elevation/json?&locations=52.411302,%2012.537468"
    
    baseURL = "http://maps.googleapis.com/maps/api/elevation/json?"    
    elevationData = []    
    geoDataString = createGeoDataString(geoData)
    url = baseURL + geoDataString + "&sensor=false"
    
    print(url)   

    req = requests.get(url)
    status = req.json()["status"]
    results = req.json()["results"]
     
    if status == "OK":         
        for data in results:
            elevationData.append(data["elevation"])             
        return elevationData         
    else:
        print("An error occured: "+ status)
        return


    
def writeGeoData (geoData, elevationData, path, fileName): 
    
    textLine = "" 
    
    if fileName is not None:
        baseName = os.path.splitext(fileName)[0]
        baseName = baseName + "_elev.txt"
    else:
        baseName = "output.txt"
        
    file = open(fileName, 'w+')
    
    for index, line in enumerate(geoData):
        print(line)
        

###########
# without globals, still crappy
##########
def main(argv=None):
    if argv is None:
        argv = sys.argv
    print(argv)
    
    if len(argv) > 1: 
        fileName = getGeoDataFile(argv[1])
    else:
        fileName = getGeoDataFile(" ")
        
    geoData = readGeoDataFile(fileName)
    elevationData = getGoogleElevationData(geoData)
    writeGeoData(geoData, elevationData, argv[0], fileName)
    sys.exit()

if __name__ == "__main__":
    main()
    