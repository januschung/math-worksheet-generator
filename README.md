# Math Worksheet Generator (Web Edition)

A modern, web-based Python app for generating customizable math worksheet PDFs. Supports multiple problem types, per-type term ranges, and a user-friendly web UI. Built with FastAPI and ReportLab.

## Features
- Generate printable math worksheets as PDFs
- Supports multiplication, addition, subtraction, division, missing factor, and fraction comparison
- Per-type term range customization (e.g., 2..12)
- Modern, interactive web UI (no CLI required)
- REST API for programmatic access
- Inline PDF preview and download

## Requirements
- Python 3.8+
- `reportlab` and `fastapi` (see `requirements.txt`)

## Quick Start
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the web app:
   ```bash
   python main.py
   ```
3. Open your browser to [http://localhost:8000](http://localhost:8000)

## Web UI Usage
- Select one or more problem types.
- Optionally adjust the term ranges (defaults are shown and can be reset).
- Set the number of problems per type.
- Click **Generate** to preview and download the worksheet PDF.

## API Endpoints
### `POST /generate`
Generate a worksheet PDF.
- **Request JSON:**
  ```json
  {
    "problem_types": ["multiplication", "addition"],
    "n": 100,
    "term1": "2..12",      // optional, single-type only
    "term2": "2..12",      // optional, single-type only
    "defaults": {           // optional per-type overrides
      "multiplication": {"term1": "3..12", "term2": "2..15"}
    }
  }
  ```
- **Response:** `{ "url": "/pdf/worksheet_xxx.pdf" }`

### `GET /pdf/{filename}`
Serve a generated PDF for inline display or download.

### `GET /defaults`
Return the default term1/term2 ranges for each problem type as a JSON object:
```json
{
  "multiplication": {"term1": "3..12", "term2": "2..19"},
  "addition": {"term1": "50..300", "term2": "10..99"},
  ...
}
```

## Customizing Problem Types and Ranges
- The web UI fetches `/defaults` and prepopulates the term range fields.
- You can edit the ranges before generating a worksheet.
- To change the built-in defaults, edit `PROBLEM_DEFAULTS` in `worksheet_core.py`.

## Extending the Core Logic
- All worksheet logic is in `worksheet_core.py`.
- To add a new problem type:
  1. Create a new class inheriting from `MathProblem`.
  2. Add it to `PROBLEM_DEFAULTS` and `PROBLEM_CLASS_MAP` in `main.py`.
  3. Update the web UI HTML if you want it selectable.

## Example: Programmatic API Usage
```python
import requests
payload = {
    "problem_types": ["multiplication"],
    "n": 50,
    "term1": "2..12",
    "term2": "2..12"
}
r = requests.post("http://localhost:8000/generate", json=payload)
print(r.json())  # {"url": "/pdf/worksheet_xxx.pdf"}
```

## Notes
- There is no CLI interface; all usage is via the web UI or API.
- All worksheet generation is stateless and per-request.

---

For more details, see the code and docstrings in `main.py` and `worksheet_core.py`.
