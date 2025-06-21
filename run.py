#!/usr/bin/env python3
"""
Math Worksheet Generator (stable v2)
===================================

Generates printable PDF worksheets containing math practice problems and an
answer key.  Now supports four problem types:

1. Multiplication (vertical layout)
2. Addition (vertical layout)
3. Missing‑factor / relational‑thinking equations
4. Fraction‑magnitude comparison (□ stands for <, =, >)

Changes in **v2 (this version)**
--------------------------------
* **Fixes "silent failure"** caused by an incomplete CLI section and by passing
  string defaults where tuples were expected.
* **Defaults are now proper tuples** so they work even when you don't supply
  `--term1/--term2`.
* Restores the full CLI block (the previous cut-off after `op.add_argument` is
  gone).
* Keeps wider grid (5 × 10) for the single-line problem types to prevent
  overlap.

Usage examples
--------------
```bash
# 20 fraction comparisons, denominators 2‑12, to fractions.pdf
python run.py --fractioncompare --n=20 --output=fractions.pdf

# Classic 100-problem multiplication sheet
python run.py --multiplication --n=100

# 80-problem mixed worksheet (run four times and merge PDFs, or use a script)
python run.py --multiplication   --n=20 --output=1_mult.pdf
python run.py --addition        --n=20 --output=2_add.pdf
python run.py --missingfactor   --n=20 --output=3_miss.pdf
python run.py --fractioncompare --n=20 --output=4_frac.pdf
```

Dependencies
------------
```bash
pip install reportlab
```

Author: Math Worksheet Generator (stable v2)
"""

import argparse
import random
from fractions import Fraction
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

# -----------------------------------------------------------------------------
# Defaults
# -----------------------------------------------------------------------------
DEFAULT_N = 100
DEFAULT_OUTPUT = "worksheet.pdf"
# Adjust PROBLEM_DEFAULTS below to adjust question type difficulty

# -----------------------------------------------------------------------------
# Problem type classes
# -----------------------------------------------------------------------------
class MathProblem:
    """Abstract base for printable items."""

    def format_problem(self):
        raise NotImplementedError

    def get_answer(self):
        raise NotImplementedError


class MultiplicationProblem(MathProblem):
    def __init__(self, a, b):
        self.a, self.b = a, b

    def format_problem(self):
        return [f"{self.a}", f"x {self.b}", "___"]

    def get_answer(self):
        return str(self.a * self.b)


class AdditionProblem(MathProblem):
    def __init__(self, a, b):
        self.a, self.b = a, b

    def format_problem(self):
        return [f"{self.a}", f"+ {self.b}", "___"]

    def get_answer(self):
        return str(self.a + self.b)


class MissingFactorProblem(MathProblem):
    def __init__(self, a, b):
        self.a, self.b = a, b
        self.prod = a * b
        self.blank_left = random.choice([True, False])

    def format_problem(self):
        if self.blank_left:
            return [f"__ × {self.b} = {self.prod}"]
        return [f"{self.a} × __ = {self.prod}"]

    def get_answer(self):
        return str(self.a if self.blank_left else self.b)


class FractionComparisonProblem(MathProblem):
    def __init__(self, d1, d2):
        n1 = random.randint(1, d1 - 1)
        n2 = random.randint(1, d2 - 1)
        self.f1 = Fraction(n1, d1)
        self.f2 = Fraction(n2, d2)

    def format_problem(self):
        return [f"{self.f1.numerator}/{self.f1.denominator}  [__]  "
                f"{self.f2.numerator}/{self.f2.denominator}"]

    def get_answer(self):
        if self.f1 > self.f2:
            return ">"

        if self.f1 < self.f2:
            return "<"
        return "="


# Default term ranges for each problem type.
# Each entry is ``((term1_min, term1_max), (term2_min, term2_max))``.
# The terms mean different things for each class:
#   - ``MultiplicationProblem`` – ranges for the two factors.
#   - ``AdditionProblem`` – ranges for the two addends.
#   - ``MissingFactorProblem`` – factor ranges used to build the equation.
#   - ``FractionComparisonProblem`` – ranges for the two denominators.
#     Numerators are chosen randomly from ``1`` up to ``denominator - 1`` so
#     the fractions are always proper.
PROBLEM_DEFAULTS = {
    MultiplicationProblem: ((2, 12), (2, 16)),  # two-digit multiplication
    AdditionProblem: ((50, 300), (10, 99)),     # three-digit addition
    MissingFactorProblem: ((2, 12), (2, 20)),   # original defaults
    FractionComparisonProblem: ((2, 12), (2, 12)),
}


# -----------------------------------------------------------------------------
# Worksheet generator
# -----------------------------------------------------------------------------
class WorksheetGenerator:
    def __init__(self, problem_cls, n, term1_range, term2_range, output_file):
        self.problem_cls = problem_cls
        self.n = n
        self.term1_range = term1_range
        self.term2_range = term2_range
        self.output_file = output_file
        self.problems = []

    # ---------------------------- problem creation ---------------------------
    def generate_problems(self):
        self.problems.clear()
        recent = []
        max_recent = 10
        for _ in range(self.n):
            for _ in range(50):
                a = random.randint(*self.term1_range)
                b = random.randint(*self.term2_range)
                if (a, b) not in recent:
                    self.problems.append(self.problem_cls(a, b))
                    recent.append((a, b))
                    if len(recent) > max_recent:
                        recent.pop(0)
                    break
            else:
                a = random.randint(*self.term1_range)
                b = random.randint(*self.term2_range)
                self.problems.append(self.problem_cls(a, b))

    # ------------------------------ PDF helpers ------------------------------
    def create_pdf(self):
        c = canvas.Canvas(self.output_file, pagesize=letter)
        w, h = letter
        self._draw_problem_pages(c, w, h)
        self._draw_answer_key(c, w, h)
        c.save()
        print(f"Worksheet saved as {self.output_file}")

    def _grid(self):
        if self.problem_cls in (MissingFactorProblem, FractionComparisonProblem):
            return 5, 10  # cols, rows – 50 per page
        return 10, 5     # original dense grid

    def _draw_problem_pages(self, c, width, height):
        cols, rows = self._grid()
        margin = 0.5 * inch
        usable_w = width - 2 * margin
        usable_h = height - 2 * margin
        col_w = usable_w / cols
        row_h = usable_h / rows

        idx = 0
        while idx < len(self.problems):
            if idx:
                c.showPage()
            for r in range(rows):
                for col in range(cols):
                    if idx >= len(self.problems):
                        break
                    p = self.problems[idx]
                    x = margin + col * col_w + 0.05 * col_w
                    y = height - margin - r * row_h - 0.15 * row_h
                    self._draw_single(c, p, x, y)
                    idx += 1
                if idx >= len(self.problems):
                    break

    @staticmethod
    def _draw_single(c, problem, x, y):
        lines = problem.format_problem()
        lh = 16
        c.setFont("Helvetica", 14)
        max_w = max(c.stringWidth(L, "Helvetica", 14) for L in lines)
        for i, L in enumerate(lines):
            line_x = x + max_w - c.stringWidth(L, "Helvetica", 14)
            c.drawString(line_x, y - i * lh, L)

    def _draw_answer_key(self, c, width, height):
        c.showPage()
        c.setFont("Helvetica-Bold", 16)
        c.drawString(0.5 * inch, height - 0.5 * inch, "Answer Key")
        c.setFont("Helvetica", 10)
        per_row = 10
        margin = 0.5 * inch
        col_w = (width - 2 * margin) / per_row
        start_y = height - 1 * inch
        row_h = 15
        for i, p in enumerate(self.problems):
            x = margin + (i % per_row) * col_w
            y = start_y - (i // per_row) * row_h
            c.drawString(x, y, f"{i+1}. {p.get_answer()}")

# Add MixedWorksheetGenerator here
class MixedWorksheetGenerator:
    SECTION_LABELS = {
        MultiplicationProblem: "Multiplication",
        AdditionProblem: "Addition",
        MissingFactorProblem: "Missing Factor",
        FractionComparisonProblem: "Fraction Comparison",
    }
    def __init__(self, problems_by_type, output_file):
        self.problems_by_type = problems_by_type  # List of (problem_cls, problems)
        self.output_file = output_file
        self.all_problems = [p for _, plist in problems_by_type for p in plist]

    def create_pdf(self):
        c = canvas.Canvas(self.output_file, pagesize=letter)
        w, h = letter

        # Split each problem list into chunks of 25
        chunked = []
        for cls, plist in self.problems_by_type:
            chunks = [plist[i : i + 25] for i in range(0, len(plist), 25)]
            chunked.append((cls, chunks))

        header_height = 22  # Space for header and line
        margin = 0.5 * inch
        usable_w = w - 2 * margin
        usable_h = h - 2 * margin
        cols, rows = 5, 5  # 25 per section
        col_w = usable_w / cols
        row_h = (usable_h / 2 - header_height) / rows

        # Pages are rendered in pairs using the existing top/bottom layout
        page_idx = 0
        chunk_idx = 0
        while True:
            rendered = False
            # pair (0,1)
            if chunk_idx < max(len(chunked[0][1]), len(chunked[1][1])):
                if page_idx:
                    c.showPage()
                for group_idx, group_i in enumerate([0, 1]):
                    cls, chunks = chunked[group_i]
                    if chunk_idx >= len(chunks):
                        continue
                    problems = chunks[chunk_idx]
                    y_offset = 0 if group_idx == 0 else -(usable_h / 2)
                    header_y = h - margin + y_offset - 2
                    c.setFont("Helvetica-Bold", 13)
                    label = self.SECTION_LABELS.get(cls, str(cls.__name__))
                    c.drawCentredString(w / 2, header_y, label)
                    c.setLineWidth(0.5)
                    c.line(margin, header_y - 5, w - margin, header_y - 5)
                    for i, p in enumerate(problems):
                        col = i % cols
                        row = i // cols
                        x = margin + col * col_w + 0.05 * col_w
                        y = h - margin - row * row_h - 0.15 * row_h + y_offset - header_height
                        WorksheetGenerator._draw_single(c, p, x, y)
                page_idx += 1
                rendered = True

            # pair (2,3)
            if chunk_idx < max(len(chunked[2][1]), len(chunked[3][1])):
                if rendered:
                    c.showPage()
                for group_idx, group_i in enumerate([2, 3]):
                    cls, chunks = chunked[group_i]
                    if chunk_idx >= len(chunks):
                        continue
                    problems = chunks[chunk_idx]
                    y_offset = 0 if group_idx == 0 else -(usable_h / 2)
                    header_y = h - margin + y_offset - 2
                    c.setFont("Helvetica-Bold", 13)
                    label = self.SECTION_LABELS.get(cls, str(cls.__name__))
                    c.drawCentredString(w / 2, header_y, label)
                    c.setLineWidth(0.5)
                    c.line(margin, header_y - 5, w - margin, header_y - 5)
                    for i, p in enumerate(problems):
                        col = i % cols
                        row = i // cols
                        x = margin + col * col_w + 0.05 * col_w
                        y = h - margin - row * row_h - 0.15 * row_h + y_offset - header_height
                        WorksheetGenerator._draw_single(c, p, x, y)
                page_idx += 1
                rendered = True

            if not rendered:
                break
            chunk_idx += 1

        self._draw_answer_key(c, w, h)
        c.save()
        print(f"Worksheet saved as {self.output_file}")

    def _draw_answer_key(self, c, width, height):
        c.showPage()
        c.setFont("Helvetica-Bold", 16)
        c.drawString(0.5 * inch, height - 0.5 * inch, "Answer Key")
        c.setFont("Helvetica", 10)
        per_row = 10
        margin = 0.5 * inch
        col_w = (width - 2 * margin) / per_row
        start_y = height - 1 * inch
        row_h = 15
        for i, p in enumerate(self.all_problems):
            x = margin + (i % per_row) * col_w
            y = start_y - (i // per_row) * row_h
            c.drawString(x, y, f"{i+1}. {p.get_answer()}")


# -----------------------------------------------------------------------------
# CLI helpers
# -----------------------------------------------------------------------------

def parse_range(txt):
    try:
        a, b = map(int, txt.split(".."))
        if a > b:
            raise ValueError
        return a, b
    except ValueError:
        raise argparse.ArgumentTypeError("Range must be 'min..max' with min ≤ max")


def main():
    parser = argparse.ArgumentParser(
        description="Generate printable math worksheets (PDF).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:\n  %(prog)s --multiplication --n=30\n  %(prog)s --fractioncompare --n=40 --term1=2..12 --term2=2..12\n  %(prog)s --all --n=40\n""",
    )

    g = parser.add_mutually_exclusive_group(required=False)
    g.add_argument("--multiplication", action="store_true")
    g.add_argument("--addition", action="store_true")
    g.add_argument("--missingfactor", action="store_true")
    g.add_argument("--fractioncompare", action="store_true")
    parser.add_argument("--all", action="store_true", help="Include all problem types equally mixed")

    parser.add_argument("--n", type=int, default=DEFAULT_N, help="Number of problems")
    parser.add_argument("--term1", type=parse_range, help="Range for first number e.g. 2..12")
    parser.add_argument("--term2", type=parse_range, help="Range for second number e.g. 2..20")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="PDF filename")

    args = parser.parse_args()

    # Mixed worksheet logic
    if args.all:
        problem_types = [
            MultiplicationProblem,
            AdditionProblem,
            MissingFactorProblem,
            FractionComparisonProblem,
        ]
        n_types = len(problem_types)
        n_each = args.n // n_types
        n_left = args.n - n_each * n_types
        problems_by_type = []
        for i, cls in enumerate(problem_types):
            t1, t2 = PROBLEM_DEFAULTS[cls]
            count = n_each + (1 if i < n_left else 0)
            recent = []
            max_recent = 10
            plist = []
            for _ in range(count):
                for _ in range(50):
                    a = random.randint(*t1)
                    b = random.randint(*t2)
                    if (a, b) not in recent:
                        plist.append(cls(a, b))
                        recent.append((a, b))
                        if len(recent) > max_recent:
                            recent.pop(0)
                        break
                else:
                    a = random.randint(*t1)
                    b = random.randint(*t2)
                    plist.append(cls(a, b))
            problems_by_type.append((cls, plist))
        gen = MixedWorksheetGenerator(problems_by_type, args.output)
        gen.create_pdf()
        return

    # Determine single problem type
    if args.multiplication:
        cls = MultiplicationProblem
    elif args.addition:
        cls = AdditionProblem
    elif args.missingfactor:
        cls = MissingFactorProblem
    elif args.fractioncompare:
        cls = FractionComparisonProblem
    else:
        parser.error("You must specify a problem type or --all.")

    default_t1, default_t2 = PROBLEM_DEFAULTS[cls]
    term1_range = args.term1 or default_t1
    term2_range = args.term2 or default_t2

    gen = WorksheetGenerator(cls, args.n, term1_range, term2_range, args.output)
    gen.generate_problems()
    gen.create_pdf()


if __name__ == "__main__":
    main()
