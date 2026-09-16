#import
import sqlite3
import pandas as pd
import yaml

with open("config.yaml") as f:
    config = yaml.safe_load(f)

#Paths
DB_path = config["DB"]