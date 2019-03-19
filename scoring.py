# -*- coding: utf-8 -*-

"""
Gareth Funk 2019
API Call to the ergast API.
Scoring based on https://fantasy.formula1.com/points-scoring
On Streaks: When a driver or constructor achieves a streak, that streak will
reset and must be built up again. For example: A driver achieves three top
tens in a row. He will be awarded a streak, but must achieve another three top
tens in a row to get streak points for a second time.
"""

race_position_bonus_lookup = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
    

def scoreQualy(qualy_result, full_qualy_results, drivers, constructors):
    driver_code = qualy_result["Driver"]["code"]
    constructorId = qualy_result["Constructor"]["constructorId"]
    qualy_pos = int(qualy_result["position"])
    # Progressed to Q3 = 3 pts
    if "Q3" in qualy_result:
        drivers[driver_code].score += 3
        constructors[constructorId].score += 3
    # Progressed to Q2 but did not progress to Q3 = 2 pts
    elif "Q2" in qualy_result:
        drivers[driver_code].score += 2
        constructors[constructorId].score += 2
    # Did not progress to Q2 = 1pt
    elif "Q1" in qualy_result:
        drivers[driver_code].score += 1
        constructors[constructorId].score += 1
    # Did not qualify = -5 pts (driver only)
    else:
        drivers[driver_code].score += -5
    # Qualified ahead of team mate = 2 pts (driver only) 
    if beatTeamMate(constructorId, qualy_pos, full_qualy_results):
        drivers[driver_code].score += 2
    # Qualifying Position Bonuses
    qualy_position_bonus = max(11 - qualy_pos, 0)
    drivers[driver_code].score += qualy_position_bonus
    constructors[constructorId].score += qualy_position_bonus
    # Streak Counter
    if qualy_pos <= 10:
        drivers[driver_code].qualy_streak += 1
        if teamMateInTopTen(constructorId, qualy_pos, full_qualy_results):
            constructors[constructorId].qualy_streak += 0.5  # When we see the team mate, we will increment this again
        # Driver Qualifying - driver qualifies in Top 10 for 5 races in a row = 5 pts
        if drivers[driver_code].qualy_streak == 5:
            drivers[driver_code].qualy_streak = 0  # Reset
            drivers[driver_code].score += 5
        # Constructor Qualifying - both drivers qualify in Top 10 for 3 races in a row = 5 pts
        if constructors[constructorId].qualy_streak  == 3:
            constructors[constructorId].qualy_streak = 0  # Reset
            constructors[constructorId].score += 5
    else:
        drivers[driver_code].qualy_streak = 0  # Reset
        constructors[constructorId].qualy_streak = 0  # Reset
    return

def scoreRace(result, full_results, drivers, constructors):
    driver_code = result["Driver"]["code"]
    constructorId = result["Constructor"]["constructorId"]
    grid_pos = int(result["grid"])
    final_pos = int(result["position"])  # If it's a number it's their position. Otherwise: E = excluded, F = 107% rule (?), D = disqualified, N = Not classified , R = retired, W = withdrew
    if result["positionText"].isdigit():
        # Finished Race = 1 pt
        final_pos = int(final_pos)
        if final_pos > 0:
            drivers[driver_code].score += 1
            constructors[constructorId].score += 1
            # Fastest lap = 5 pts (driver only)
            if result["FastestLap"]["rank"] == "1":
                drivers[driver_code].score += 5
            # Finished ahead of team mate = 3 pts (driver only)
            if beatTeamMate(constructorId, final_pos, full_results):
                drivers[driver_code].score += 3
            # Finished race, position gained = +2 pts per place gained (max +10 pts)
            if grid_pos > final_pos:
                pos_gained_bonus = min(10, 2*(grid_pos - final_pos))
                drivers[driver_code].score += pos_gained_bonus
                constructors[constructorId].score += pos_gained_bonus
            # Started race within Top 10, finished race but lost position = -2 pts per place lost (max -10 pts)
            else:
                if grid_pos <= 10:
                    lost_pos_penalty = max(-10, -2*(final_pos - grid_pos))
                    drivers[driver_code].score += lost_pos_penalty
                    constructors[constructorId].score += lost_pos_penalty
            # Started race outside Top 10, finished race but lost position = -1 pt per place lost (max -5 pts)
                else:
                    lost_pos_penalty = max(-5, -1*(final_pos - grid_pos))
                    drivers[driver_code].score += lost_pos_penalty
                    constructors[constructorId].score += lost_pos_penalty
            # Finishing Position Bonuses
            race_pos_bonus = racePositionBonus(int(final_pos))
            drivers[driver_code].score += race_pos_bonus
            constructors[constructorId].score += race_pos_bonus 
    else:
        # Disqualification from race = -20 pts (driver only)
        if final_pos == "D":
            drivers[driver_code].score += -20
        else:
            # Not classifed = -15 pts (driver only)
            drivers[driver_code].score += -15
    # Streak Counter
    if final_pos <= 10:
        drivers[driver_code].race_streak += 1
        if teamMateInTopTen(constructorId, final_pos, full_results):
            constructors[constructorId].race_streak += 0.5  # When we see the team mate, we will increment this again
        # Driver Race - driver finishes race in Top 10 for 5 races in a row = 10 pts
        if drivers[driver_code].race_streak == 5:
            drivers[driver_code].race_streak = 0  # Reset
            drivers[driver_code].score += 10
        # Constructor Race - both drivers finish race in Top 10 for 3 races in a row = 10 pts
        if constructors[constructorId].race_streak  == 3:
            constructors[constructorId].race_streak = 0  # Reset
            constructors[constructorId].score += 10
    else:
        drivers[driver_code].race_streak = 0  # Reset
        constructors[constructorId].race_streak = 0  # Reset
    return

def racePositionBonus(race_position):
    if race_position <= 10:
        points = race_position_bonus_lookup[race_position - 1]
    else:
        points = 0
    return points

def beatTeamMate(constructorId, driverPos, full_results):
    try:
        driverPos = int(driverPos)
    except ValueError:
        # Non-number, cannot have beaten team mate.
        return False
    for result in full_results:
        if result["Constructor"]["constructorId"] == constructorId:
            # Same team
            if int(result["position"]) == driverPos:
                # Same person
                continue
            else:
                # This is the team mate
                try:
                    teammatePos = int(result["position"])
                except ValueError:
                    # Team mate had non-numeric, driver beat team mate by default.
                    return True
                if teammatePos > driverPos:
                    return True
    return False

def teamMateInTopTen(constructorId, driverPos, full_results):
    try:
        driverPos = int(driverPos)
    except ValueError:
        raise ValueError("This function shouldn't be called for drivers not in the top 10 already")
    for result in full_results:
        if result["Constructor"]["constructorId"] == constructorId:
            # Same team
            if int(result["position"]) == driverPos:
                # Same person
                continue
            else:
                # This is the team mate
                try:
                    teammatePos = int(result["position"])
                except ValueError:
                    # Team mate had non-numeric, not in top 10
                    return False
                if teammatePos <= 10:
                    return True
    return False