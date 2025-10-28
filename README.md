# Intelligent Work Assistant

A personal intelligent work assistant application running on your local computer, built with Streamlit.

## Description

Intelligent Work Assistant (IWA) is a Python-based application designed to help you with your daily work tasks. It provides an interactive web interface powered by Streamlit for easy interaction.

## Features

- Local execution for privacy and security
- Web-based user interface using Streamlit
- Lightweight and easy to use

## Requirements

- Python >= 3.12
- Streamlit >= 1.50.0

## Installation

Install the package:
```bash
pip install intelligent-work-assistant
```

## How to Run
```bash
iwa
```

This will launch the Streamlit application in your default web browser.

## Project Structure

```
IntelligentWorkAssistant/
├── src/
│   └── intelligent_work_assistant/
│       ├── __init__.py
│       ├── __main__.py
│       ├── main.py          # Entry point and launcher
│       └── st_main.py       # Main Streamlit application
├── tests/
│   └── __init__.py
├── pyproject.toml           # Project configuration and dependencies
└── README.md
```

## Development

To contribute or modify the application:

1. Install in editable mode: `pip install -e .`
2. Make your changes to the code
3. Test by running `iwa` command
4. The changes will be reflected immediately without reinstallation

## License

MIT