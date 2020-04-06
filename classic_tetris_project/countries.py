import csv
import os

COUNTRIES_CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "countries.csv")

class Country:
    ACCEPTED_MAPPINGS = {}

    def __init__(self, two_letter, full_name):
        self.abbreviation = two_letter
        self.full_name = full_name

    def get_flag(self):
        return f":flag_{self.abbreviation}:"

    @staticmethod
    def populate_mappings(path=COUNTRIES_CSV_PATH):
        with open(path, "r") as f:
            rows = csv.reader(f)
            for row in rows:
                country = Country(row[0], row[1])
                for column in row:
                    Country.ACCEPTED_MAPPINGS[column.lower()] = country


    @staticmethod
    def get_country(input_string):
        try:
            return Country.ACCEPTED_MAPPINGS[input_string.lower()]
        except KeyError:
            return None

Country.populate_mappings()
