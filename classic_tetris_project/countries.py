import csv
from pathlib import Path

COUNTRIES_CSV_PATH = Path(__file__).parent.resolve() / "data" / "countries.csv"

class Country:
    ACCEPTED_MAPPINGS = {}
    ALL = []

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
                Country.ALL.append(country)
                for column in row:
                    Country.ACCEPTED_MAPPINGS[column.lower()] = country
        Country.ALL.sort(key=lambda country: country.full_name)


    @staticmethod
    def get_country(input_string):
        try:
            return Country.ACCEPTED_MAPPINGS[input_string.lower()]
        except KeyError:
            return None

Country.populate_mappings()
