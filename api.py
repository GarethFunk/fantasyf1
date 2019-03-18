# -*- coding: utf-8 -*-

"""
Gareth Funk 2019
API Call to the ergast API.
"""

import requests
import json

import scoring

season = "2018"
api_base_url = "https://ergast.com/api/f1/" + season + "/"

def getConstructors():
    req = requests.get(api_base_url + "constructors.json")
    constructors = {}
    for constructor in json.loads(req.content)["MRData"]["ConstructorTable"]["Constructors"]:
        constructors[constructor["constructorId"]] = constructor
        constructors[constructor["constructorId"]]["score"] = 0
        constructors[constructor["constructorId"]]["qualy_streak"] = 0
        constructors[constructor["constructorId"]]["race_streak"] = 0
    return constructors

def getDrivers():
    req = requests.get(api_base_url + "drivers.json")
    drivers = {}
    for driver in json.loads(req.content)["MRData"]["DriverTable"]["Drivers"]:
        drivers[driver["code"]] = driver
        drivers[driver["code"]]["score"] = 0
        drivers[driver["code"]]["qualy_streak"] = 0
        drivers[driver["code"]]["race_streak"] = 0
    return drivers

def qualy(drivers, constructors):
    req = requests.get(api_base_url + "qualifying.json?limit=9999")
    all_qualy_data = json.loads(req.content)["MRData"]["RaceTable"]["Races"]
    # Score qualy individually
    for race in all_qualy_data:
        for result in race["QualifyingResults"]:
            scoring.scoreQualy(result, race["QualifyingResults"], drivers, constructors)

def race(drivers, constructors):
    req = requests.get(api_base_url + "results.json?limit=9999")
    all_race_data = json.loads(req.content)["MRData"]["RaceTable"]["Races"]
    # Score qualy individually 
    for race in all_race_data:
        for result in race["Results"]:
            scoring.scoreRace(result, race["Results"], drivers, constructors)
            
if __name__ == "__main__":
    constructors = getConstructors()
    drivers = getDrivers()
    qualy(drivers, constructors)
    race(drivers, constructors)
    driver_scores = sorted([(x["code"], x["score"]) for x in drivers.values()], key = lambda x:x[1], reverse=True)
    constructor_scores = sorted([(x["constructorId"], x["score"]) for x in constructors.values()], key = lambda x:x[1], reverse=True)
    for driver in driver_scores:
        print(driver[0] + " = " + str(driver[1]))
    for constructor in constructor_scores:
        print(constructor[0] + " = " + str(constructor[1]))
    pass 
