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

# Full example
python run.py --multiplication --n=100 --term1=2..15 --term2=2..20 --output=worksheet.pdf
```

## Options

- `--multiplication` or `--addition`: Problem type (required)
- `--n`: Number of problems (default: 100)
- `--term1`: Range for first number, format `min..max` (default: 2..15)
- `--term2`: Range for second number, format `min..max` (default: 2..20)
- `--output`: Output PDF filename (default: worksheet.pdf)

## Output

- **Worksheet Pages**: 50 problems per page in a 10×5 grid
- **Answer Key**: Compact answer grid on the final page

## Customization

Edit the default values at the top of `run.py`:
```python
DEFAULT_N = 100
DEFAULT_TERM1_MIN = 2
DEFAULT_TERM1_MAX = 15
# etc.
```