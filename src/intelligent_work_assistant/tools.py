import requests
import json
import time
from .mocked_functions import get_mails, get_chats, get_notes

def call_tool(tool_name: str, tool_args: dict) -> str:
    return tools_map[tool_name](**tool_args)

def get_weather(city: str) -> str:
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

def get_current_time() -> str:
    """
    Get the current time
    """
    return time.asctime()

def generate_work_report(since: str, until: str) -> str:
    """
    Generate your work report

    Args:
        since: The begin of work
        until: The end of work
    """
    return get_mails(since, until) + get_chats(since, until) + get_notes(since, until)

tools = [get_weather, get_current_time, generate_work_report]
tools_map = {"get_weather": get_weather, "get_current_time":get_current_time, "generate_work_report":generate_work_report}