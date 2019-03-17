# -*- coding: utf-8 -*-

"""
Gareth Funk 2019
API Call to the ergast API.
"""

import requests
import json

import scoring

season = "2019"
api_base_url = "https://ergast.com/api/f1/" + season + "/"

def getConstructors():
    req = requests.get(api_base_url + "constructors.json")
    constructors = {}
    for constructor in json.loads(req.content)["MRData"]["ConstructorTable"]["Constructors"]:
        constructors[constructor["constructorId"]] = constructor
        constructors[constructor["constructorId"]]["score"] = 0
    return constructors

def getDrivers():
    req = requests.get(api_base_url + "drivers.json")
    drivers = {}
    for driver in json.loads(req.content)["MRData"]["DriverTable"]["Drivers"]:
        drivers[driver["code"]] = driver
        drivers[driver["code"]]["score"] = 0
    return drivers

def qualy(drivers, constructors):
    req = requests.get(api_base_url + "qualifying.json")
    for race in json.loads(req.content)["MRData"]["RaceTable"]["Races"]:
        for result in race["QualifyingResults"]:
            scoring.scoreQualy(result, race["QualifyingResults"], drivers, constructors)

def race(drivers, constructors):
    req = requests.get(api_base_url + "results.json")
    for race in json.loads(req.content)["MRData"]["RaceTable"]["Races"]:
        for result in race["Results"]:
            scoring.scoreRace(result, race["Results"], drivers, constructors)
            
            

if __name__ == "__main__":
    constructors = getConstructors()
    drivers = getDrivers()
    qualy(drivers, constructors)
    race(drivers, constructors)
    for driver in drivers.values():
        print(driver["code"] + " = " + str(driver["score"]))
    for constructor in constructors.values():
        print(constructor["constructorId"] + " = " + str(constructor["score"]))
    pass 
