# Math Worksheet Generator

A Python script that generates PDF math worksheets with customizable problem types, ranges, and quantities.

## Installation

```bash
pip install reportlab
```

## Usage

```bash
# Basic multiplication worksheet (100 problems, default ranges)
python run.py --multiplication

# Custom multiplication worksheet
python run.py --multiplication --n=50 --term1=3..12 --term2=2..15 --output=homework.pdf

# Addition worksheet
python run.py --addition --n=200 --term1=10..99 --term2=1..50

# Mixed worksheet with two types (defaults only)
python run.py --multiplication --addition --n=60

# Full example
python run.py --multiplication --n=100 --term1=2..15 --term2=2..20 --output=worksheet.pdf
```

## Options

- `--multiplication`, `--addition`, `--missingfactor`, `--fractioncompare`: Select one or more problem types. When more than one is chosen, built‑in defaults are used for each type.
- `--all`: Generate a mixed worksheet using the built‑in defaults for each type.
  When more than 25 problems are requested for a type, extra pages are added in
  25‑problem sections and the answer key is placed after the last problem page.
- `--n`: Number of problems (default: 100)
- `--term1`: Range for first number (`min..max`, overrides the per‑type default when a single type is chosen)
- `--term2`: Range for second number (`min..max`)
- `--output`: Output PDF filename (default: worksheet.pdf)

When multiple problem types are selected, custom term ranges are ignored and the defaults for each type are used.
## Output

- **Worksheet Pages**: 50 problems per page in a 10×5 grid
- **Answer Key**: Compact answer grid on the final page

## Customization

Edit the per‑type defaults in `run.py` by modifying `PROBLEM_DEFAULTS`:
```python
PROBLEM_DEFAULTS = {
    MultiplicationProblem: ((10, 99), (10, 99)),  # two‑digit multiplication
    AdditionProblem: ((100, 999), (100, 999)),    # three‑digit addition
    # ...
}
```
