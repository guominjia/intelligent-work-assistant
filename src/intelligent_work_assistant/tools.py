import requests
import json
import time

def call_tool(tool_name: str, tool_args: dict) -> str:
    return tools_map[tool_name](**tool_args)

def get_weather(city: str):
    """
    Get the current weather in a given city name.

    Args:
        city: City name
    """
    key_selection = {
        "current_condition": [
            "temp_C",
            "FeelsLikeC",
            "humidity",
            "weatherDesc",
            "observation_time",
        ],
    }
    resp = requests.get(f"https://wttr.in/{city}?format=j1")
    resp.raise_for_status()
    resp = resp.json()
    ret = {k: {_v: resp[k][0][_v] for _v in v} for k, v in key_selection.items()}
    return json.dumps(ret, ensure_ascii=False)

def get_current_time():
    """
    Get the current time
    """
    return time.asctime()

tools = [get_weather, get_current_time]
tools_map = {"get_weather": get_weather, "get_current_time":get_current_time}