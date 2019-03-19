# -*- coding: utf-8 -*-

"""
Gareth Funk 2019
"""

class Driver():
    def __init__(self, api_data):
        self.data = api_data
        self.code = api_data["code"]
        self.score = 0
        self.qualy_streak = 0
        self.race_streak = 0
