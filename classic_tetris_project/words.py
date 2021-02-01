import csv
import random
from pathlib import Path

class Words:
    WORDS_CSV_PATH = Path(__file__).parent.resolve() / "data" / "words.csv"
    FULL_LIST = []

    @staticmethod
    def populate(path=WORDS_CSV_PATH):
        with open(path, "r") as f:
            Words.FULL_LIST = list(csv.reader(f))[0]

    @staticmethod
    def get_word():
        return random.choice(Words.FULL_LIST).upper()

Words.populate()
