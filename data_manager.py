import json
import os
from datetime import datetime

DATA_DIR = "data"

class DataManager:
    def __init__(self):
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

    def get_filepath(self, date):
        """Generates the filepath for a given date."""
        date_str = date.strftime("%Y-%m-%d")
        return os.path.join(DATA_DIR, f"{date_str}.json")

    def save_data(self, date, data):
        """Saves the data for a given date to a JSON file."""
        filepath = self.get_filepath(date)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)

    def load_data(self, date):
        """Loads the data for a given date from a JSON file."""
        filepath = self.get_filepath(date)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return None  # Or handle corrupted file
        return None
