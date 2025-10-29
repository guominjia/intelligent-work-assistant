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

## Download models
1. Download Embedding model
```
modelscope download --model "OpenVINO/Qwen3-Embedding-0.6B-int8-ov" --local_dir Qwen3-Embedding-0.6B-int8-ov
```

2. Download Text-Generation model
```
modelscope download --model "OpenVINO/Qwen3-0.6B-int8-ov" --local_dir Qwen3-0.6B-int8-ov
```

## How to Run
```bash
iwa --model <Text-Generate model> --embed-model <Embedding model>
```
Assume that you downloaded **Qwen3-Embedding-0.6B-int8-ov** and **Qwen3-0.6B-int8-ov** model, the command should be
```
iwa --model Qwen3-0.6B-int8-ov --embed-model Qwen3-Embedding-0.6B-int8-ov
```

This will launch the Streamlit application in your default web browser.

## Project Structure

```
IntelligentWorkAssistant/
├── src/
│   └── intelligent_work_assistant/
│       ├── __init__.py
│       ├── __main__.py
│       ├── main.py          # Entry point and launcher with CLI arguments
│       ├── model.py         # OpenVINO LLM wrapper with streaming support
│       └── st_main.py       # Main Streamlit multi-page application
├── tests/
│   └── __init__.py
├── threads-history/         # Chat history storage (auto-created)
├── pyproject.toml           # Project configuration and dependencies
└── README.md
```

### Key Files

- **main.py**: Command-line interface entry point that validates models and launches Streamlit
- **model.py**: OpenVINO GenAI wrapper class for LLM inference with streaming capabilities
- **st_main.py**: Streamlit application with multi-page navigation, chat interface, and history management

## Development

To contribute or modify the application:

1. Install in editable mode: `pip install -e .`
2. Make your changes to the code
3. Test by running `iwa` command
4. The changes will be reflected immediately without reinstallation

## License

MIT