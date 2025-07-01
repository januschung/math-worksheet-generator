import random
from fractions import Fraction
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

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

class SubtractionProblem(MathProblem):
    def __init__(self, a, b):
        self.a, self.b = a, b
    def format_problem(self):
        return [f"{self.a}", f"- {self.b}", "___"]
    def get_answer(self):
        return str(self.a - self.b)

class DivisionProblem(MathProblem):
    def __init__(self, divisor, quotient):
        self.divisor = divisor
        self.quotient = quotient
        self.dividend = divisor * quotient
    def format_problem(self):
        return [f"{self.dividend}", f"÷ {self.divisor}", "___"]
    def get_answer(self):
        return str(self.quotient)

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
# Each entry is ((term1_min, term1_max), (term2_min, term2_max)).
PROBLEM_DEFAULTS = {
    MultiplicationProblem: ((3, 12), (2, 19)),
    AdditionProblem: ((50, 300), (10, 99)),
    SubtractionProblem: ((10, 99), (10, 99)),
    MissingFactorProblem: ((2, 12), (2, 20)),
    DivisionProblem: ((2, 12), (2, 12)),
    FractionComparisonProblem: ((2, 12), (2, 12)),
}

DEFAULT_N = 100

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

    def create_pdf(self):
        c = canvas.Canvas(self.output_file, pagesize=letter)
        w, h = letter
        self._draw_problem_pages(c, w, h)
        self._draw_answer_key(c, w, h)
        c.save()

    def _grid(self):
        if self.problem_cls in (MissingFactorProblem, FractionComparisonProblem):
            return 5, 10
        return 10, 5

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

class MixedWorksheetGenerator:
    SECTION_LABELS = {
        MultiplicationProblem: "Multiplication",
        AdditionProblem: "Addition",
        SubtractionProblem: "Subtraction",
        DivisionProblem: "Division",
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
        groups = [(cls, plist) for cls, plist in self.problems_by_type if plist]
        chunked = []
        for cls, plist in groups:
            chunks = [plist[i : i + 25] for i in range(0, len(plist), 25)]
            chunked.append((cls, chunks))
        header_height = 22
        margin = 0.5 * inch
        usable_w = w - 2 * margin
        usable_h = h - 2 * margin
        cols, rows = 5, 5
        col_w = usable_w / cols
        row_h = (usable_h / 2 - header_height) / rows
        page_idx = 0
        chunk_idx = 0
        while True:
            rendered = False
            for pair_i in range(0, len(chunked), 2):
                top = chunked[pair_i]
                bottom = chunked[pair_i + 1] if pair_i + 1 < len(chunked) else None
                top_ok = chunk_idx < len(top[1])
                bottom_ok = bottom and chunk_idx < len(bottom[1])
                if not (top_ok or bottom_ok):
                    continue
                if page_idx or rendered:
                    c.showPage()
                for idx, group in enumerate([top, bottom]):
                    if not group or chunk_idx >= len(group[1]):
                        continue
                    cls, chunks = group
                    problems = chunks[chunk_idx]
                    y_off = 0 if idx == 0 else -(usable_h / 2)
                    header_y = h - margin + y_off - 2
                    c.setFont("Helvetica-Bold", 13)
                    label = self.SECTION_LABELS.get(cls, str(cls.__name__))
                    c.drawCentredString(w / 2, header_y, label)
                    c.setLineWidth(0.5)
                    c.line(margin, header_y - 5, w - margin, header_y - 5)
                    for i, p in enumerate(problems):
                        col = i % cols
                        row = i // cols
                        x = margin + col * col_w + 0.05 * col_w
                        y = (
                            h - margin - row * row_h - 0.15 * row_h + y_off - header_height
                        )
                        WorksheetGenerator._draw_single(c, p, x, y)
                page_idx += 1
                rendered = True
            if not rendered:
                break
            chunk_idx += 1
        self._draw_answer_key(c, w, h)
        c.save()

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
# Helpers
# -----------------------------------------------------------------------------
def parse_range(txt):
    try:
        a, b = map(int, txt.split(".."))
        if a > b:
            raise ValueError
        return a, b
    except ValueError:
        raise ValueError("Range must be 'min..max' with min ≤ max")

def make_problems(cls, n, term1_range, term2_range):
    recent = []
    max_recent = 10
    plist = []
    for _ in range(n):
        for _ in range(50):
            a = random.randint(*term1_range)
            b = random.randint(*term2_range)
            if (a, b) not in recent:
                plist.append(cls(a, b))
                recent.append((a, b))
                if len(recent) > max_recent:
                    recent.pop(0)
                break
        else:
            a = random.randint(*term1_range)
            b = random.randint(*term2_range)
            plist.append(cls(a, b))
    return plist 