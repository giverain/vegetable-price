# AGENTS.md - Guidelines for Agentic Coding

## Project Overview
This is a simple Python Flask application that scrapes vegetable prices from Taizhou government website and displays them in a web interface.

## Project Structure
```
Vegetable/
├── app.py              # Main Flask application
└── requirements.txt   # Python dependencies
```

## Build/Lint/Test Commands

### Installation
```bash
pip install -r requirements.txt
```

### Running the Application
```bash
# Local development
python app.py

# Runs on http://localhost:5000 with debug mode enabled
```

### Running a Single Test
This project does not have a formal test suite. To test functionality:
1. Run the app and visit http://localhost:5000
2. Check console output for price update logs
3. Manually verify data displays correctly

### Linting
```bash
# Install flake8 or pylint
pip install flake8

# Lint all Python files
flake8 app.py

# With specific configuration
flake8 app.py --max-line-length=120 --ignore=E501,W503
```

### Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```

## Code Style Guidelines

### General Principles
- Write clean, readable code with clear variable names
- Add comments for complex logic (Chinese comments OK since this is a Chinese-language project)
- Keep functions focused and concise (under 50 lines when possible)
- Handle exceptions gracefully with meaningful error messages

### Imports
- Standard library imports first
- Third-party imports second
- Local imports last
- Sort alphabetically within each group
```python
# Good
import re
import threading
import time
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template_string
```

### Formatting
- Maximum line length: 120 characters
- Use 4 spaces for indentation (not tabs)
- Add spaces around operators: `x = 1 + 2`
- No trailing whitespace
- Two blank lines between top-level definitions

### Types
- Python 3.x (type hints optional for simple scripts)
- Use descriptive variable names instead of complex type annotations
- Example type hints when used:
```python
def get_price(vegetable: str) -> float:
    ...
```

### Naming Conventions
- `snake_case` for functions and variables: `update_vegetable_price()`, `latest_data`
- `SCREAMING_SNAKE_CASE` for constants: `HEADERS`, `MAX_RETRIES`
- `PascalCase` for classes (if added): `PriceTracker`
- Use Chinese/English mixed naming where appropriate for domain terms

### Error Handling
- Use try/except blocks for external operations (HTTP requests, parsing)
- Catch specific exceptions when possible
- Log errors with descriptive messages
- Never expose stack traces to end users
```python
# Good
try:
    resp = requests.get(url, timeout=15)
    resp.encoding = "utf-8"
except requests.RequestException as e:
    print(f"请求失败：{str(e)}")
    return None
```

### HTTP Requests
- Always set User-Agent headers
- Set reasonable timeouts (15 seconds default)
- Handle encoding explicitly: `resp.encoding = "utf-8"`

### Flask Specific
- Use `render_template_string()` for simple inline templates
- Keep HTML templates separate for complex pages
- Use appropriate HTTP methods (@app.route defaults to GET)

### Pandas Usage
- Use descriptive column names when creating DataFrames
- Handle missing/null values explicitly
- Prefer explicit iteration over complex vectorized operations for readability

### Concurrency
- Use `threading` for background tasks
- Avoid shared state between threads when possible
- Use locks if shared state is necessary

## Common Patterns

### Price Scraping Pattern
```python
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ..."
}

def fetch_data():
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.encoding = "utf-8"
    # Parse and process...
```

### Flask Route Pattern
```python
@app.route('/')
def index():
    return render_template_string(html_template, data=data)
```

## Adding New Features
1. Keep functions small and focused
2. Add appropriate error handling
3. Test locally before committing
4. Update documentation/comments for complex logic

## Security Considerations
- Never commit secrets or API keys
- Validate all external input
- Use parameterized queries if adding database access
- Keep dependencies updated
