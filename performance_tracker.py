import json
import os

FILE = "data/performance.json"

def save_performance(user, topic, score):
    if not os.path.exists(FILE):
        with open(FILE, "w") as f:
            json.dump({}, f)

    with open(FILE, "r") as f:
        data = json.load(f)

    if user not in data:
        data[user] = {}

    data[user][topic] = score

    with open(FILE, "w") as f:
        json.dump(data, f)