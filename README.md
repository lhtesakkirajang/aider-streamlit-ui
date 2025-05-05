# Aider Dry-Run Demo

This project is a proof of concept using [Aider](https://github.com/paul-gauthier/aider) with a Streamlit app.

## 🚀 Features

- Streamlit-powered UI (`demo.py`)
- Dependency management using [`uv`](https://github.com/astral-sh/uv)
- Aider integration for AI-assisted development

## 🛠️ Setup

### Prerequisites

- Python 3.13+
- `uv` package manager installed

### Installation

```bash
# Create virtual environment using uv
uv venv

# Activate the virtual environment
source .venv/Scripts/activate  # On Windows with Git Bash

# Install dependencies
uv pip install -r requirements.txt

# Install aider
aider-install

# Run Streamlit demo in browser
streamlit run demo.py
