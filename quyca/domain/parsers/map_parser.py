import json
import os
from collections import defaultdict
from math import log

import pandas as pd


def parse_coauthorship_by_country_map(data: list) -> dict:
    countries: defaultdict = defaultdict(lambda: {"count": 0, "name": ""})
    for item in data:
        addresses = item.get("affiliation", {}).get("addresses", {})
        country_code = addresses.get("country_code")
        country_name = addresses.get("country")
        if country_code and country_name:
            country_data = countries[country_code]
            country_data["count"] += item["count"]
            country_data["name"] = country_name
    for country_data in countries.values():
        country_data["log_count"] = log(country_data["count"])
    worldmap_path = os.path.join(os.path.dirname(__file__), "concerns/worldmap.json")
    with open(worldmap_path, "r") as worldmap_file:
        plot = json.load(worldmap_file)
    for feature in plot["features"]:
        country_code = feature["properties"].get("country_code")
        if country_code in countries:
            country_data = countries[country_code]
            feature["properties"]["count"] = country_data["count"]
            feature["properties"]["log_count"] = country_data["log_count"]
        else:
            feature["properties"]["count"] = 0
            feature["properties"]["log_count"] = 0
    return {"plot": plot}


def get_coauthorship_by_colombian_department_map(data: list) -> dict:
    cities_by_state_path = os.path.join(os.path.dirname(__file__), "concerns/cities_by_state.csv")
    cities_by_state = pd.read_csv(cities_by_state_path)
    city_to_state = dict(zip(cities_by_state["MUNICIPIO"], cities_by_state["DEPARTAMENTO"]))
    states = {}
    for item in data:
        addresses = item.get("affiliation", {}).get("addresses", {})
        if addresses.get("country_code") and addresses.get("city"):
            city = addresses["city"]
            state = city_to_state.get(city)
            if state:
                if state not in states:
                    states[state] = {"count": 0, "name": state}
                states[state]["count"] += item["count"]
    for state_data in states.values():
        state_data["log_count"] = log(state_data["count"])
    colombiamap_path = os.path.join(os.path.dirname(__file__), "concerns/colombiamap.json")
    with open(colombiamap_path, "r") as colombiamap_file:
        plot = json.load(colombiamap_file)
    for feature in plot["features"]:
        state = feature["properties"]["NOMBRE_DPT"].capitalize()
        if "bogota" in state.lower():
            state = "Bogotá D.C."
        state_data = states.get(state, {"count": 0, "log_count": 0})
        feature["properties"]["count"] = state_data["count"]
        feature["properties"]["log_count"] = state_data["log_count"]
    return {"plot": plot}
