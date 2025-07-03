"""
worksheet_core.py
-----------------
Core logic for generating math worksheet problems and PDFs. Contains all problem type classes, worksheet generators, and helpers. No CLI or web dependencies. All logic is parameterized and stateless.
"""
import random
from fractions import Fraction
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

# -----------------------------------------------------------------------------
# Problem type classes
# -----------------------------------------------------------------------------
class MathProblem:
    """Abstract base for printable math problems."""
    def format_problem(self):
        """Return a list of strings representing the problem for display."""
        raise NotImplementedError
    def get_answer(self):
        """Return the answer as a string."""
        raise NotImplementedError

class MultiplicationProblem(MathProblem):
    """A multiplication problem: a × b = ___"""
    def __init__(self, a, b):
        self.a, self.b = a, b
    def format_problem(self):
        return [f"{self.a}", f"x {self.b}", "___"]
    def get_answer(self):
        return str(self.a * self.b)

class AdditionProblem(MathProblem):
    """An addition problem: a + b = ___"""
    def __init__(self, a, b):
        self.a, self.b = a, b
    def format_problem(self):
        return [f"{self.a}", f"+ {self.b}", "___"]
    def get_answer(self):
        return str(self.a + self.b)

class SubtractionProblem(MathProblem):
    """A subtraction problem: a - b = ___"""
    def __init__(self, a, b):
        self.a, self.b = a, b
    def format_problem(self):
        return [f"{self.a}", f"- {self.b}", "___"]
    def get_answer(self):
        return str(self.a - self.b)

class DivisionProblem(MathProblem):
    """A division problem: (dividend) ÷ (divisor) = ___ (quotient)"""
    def __init__(self, divisor, quotient):
        self.divisor = divisor
        self.quotient = quotient
        self.dividend = divisor * quotient
    def format_problem(self):
        return [f"{self.dividend}", f"÷ {self.divisor}", "___"]
    def get_answer(self):
        return str(self.quotient)

class MissingFactorProblem(MathProblem):
    """A missing-factor multiplication: __ × b = prod or a × __ = prod"""
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
    """A fraction comparison: n1/d1 [__] n2/d2, answer is <, =, or >"""
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
    """Generates a worksheet PDF for a single problem type."""
    def __init__(self, problem_cls, n, term1_range, term2_range, output_file):
        """
        Args:
            problem_cls: The problem class (e.g., MultiplicationProblem)
            n: Number of problems
            term1_range: Tuple (min, max) for first term
            term2_range: Tuple (min, max) for second term
            output_file: Path to output PDF
        """
        self.problem_cls = problem_cls
        self.n = n
        self.term1_range = term1_range
        self.term2_range = term2_range
        self.output_file = output_file
        self.problems = []

    def generate_problems(self):
        """Generate n unique problems for the worksheet."""
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
                # Fallback if all recent pairs are exhausted
                a = random.randint(*self.term1_range)
                b = random.randint(*self.term2_range)
                self.problems.append(self.problem_cls(a, b))

    def create_pdf(self):
        """Create the worksheet PDF with problems and answer key."""
        c = canvas.Canvas(self.output_file, pagesize=letter)
        w, h = letter
        self._draw_problem_pages(c, w, h)
        self._draw_answer_key(c, w, h)
        c.save()

    def _grid(self):
        """Return (cols, rows) for the worksheet grid layout."""
        if self.problem_cls in (MissingFactorProblem, FractionComparisonProblem):
            return 5, 10
        return 10, 5

    def _draw_problem_pages(self, c, width, height):
        """Draw the problems in a grid layout on the PDF."""
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
        """Draw a single problem at (x, y) on the PDF canvas."""
        lines = problem.format_problem()
        lh = 16
        c.setFont("Helvetica", 14)
        max_w = max(c.stringWidth(L, "Helvetica", 14) for L in lines)
        for i, L in enumerate(lines):
            line_x = x + max_w - c.stringWidth(L, "Helvetica", 14)
            c.drawString(line_x, y - i * lh, L)

    def _draw_answer_key(self, c, width, height):
        """Draw the answer key on a new PDF page."""
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
    """Generates a worksheet PDF with multiple problem types, each in its own section.

    The ``chunk_size`` parameter controls how many problems from each type are
    shown together. The default of 25 matches the previous behaviour where two
    types are displayed on a single page (25 problems each). Larger ``chunk_size``
    values will dedicate a full page to the chunk.
    """
    SECTION_LABELS = {
        MultiplicationProblem: "Multiplication",
        AdditionProblem: "Addition",
        SubtractionProblem: "Subtraction",
        DivisionProblem: "Division",
        MissingFactorProblem: "Missing Factor",
        FractionComparisonProblem: "Fraction Comparison",
    }
    def __init__(self, problems_by_type, output_file, chunk_size=25):
        """
        Args:
            problems_by_type: List of (problem_cls, problems) pairs
            output_file: Path to output PDF
        """
        self.problems_by_type = problems_by_type
        self.output_file = output_file
        self.chunk_size = chunk_size
        self.all_problems = [p for _, plist in problems_by_type for p in plist]

    def create_pdf(self):
        """Create the mixed worksheet PDF with sections and answer key."""
        c = canvas.Canvas(self.output_file, pagesize=letter)
        w, h = letter
        groups = [(cls, plist) for cls, plist in self.problems_by_type if plist]
        chunked = []
        for cls, plist in groups:
            chunks = [
                plist[i : i + self.chunk_size]
                for i in range(0, len(plist), self.chunk_size)
            ]
            chunked.append((cls, chunks))
        header_height = 22
        margin = 0.5 * inch
        usable_w = w - 2 * margin
        usable_h = h - 2 * margin
        page_idx = 0

        if self.chunk_size <= 25:
            # Half-page layout: two sections per page
            cols, rows = 5, 5
            col_w = usable_w / cols
            row_h = (usable_h / 2 - header_height) / rows

            # Build flat list of sections in display order
            sections = []
            max_chunks = max(len(chunks) for _, chunks in chunked)
            for i in range(max_chunks):
                for cls, chunks in chunked:
                    if i < len(chunks):
                        sections.append((cls, chunks[i]))

            for pair_i in range(0, len(sections), 2):
                top = sections[pair_i]
                bottom = sections[pair_i + 1] if pair_i + 1 < len(sections) else None
                if pair_i:
                    c.showPage()
                for idx, section in enumerate([top, bottom]):
                    if not section:
                        continue
                    cls, problems = section
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
                            h
                            - margin
                            - row * row_h
                            - 0.15 * row_h
                            + y_off
                            - header_height
                        )
                        WorksheetGenerator._draw_single(c, p, x, y)
                page_idx += 1
        else:
            # Full-page layout: one section per page
            for cls, chunks in chunked:
                # Determine grid based on problem type
                if cls in (
                    MissingFactorProblem,
                    FractionComparisonProblem,
                ):
                    cols, rows = 5, 10
                else:
                    cols, rows = 10, 5
                col_w = usable_w / cols
                row_h = (usable_h - header_height) / rows
                for problems in chunks:
                    if page_idx:
                        c.showPage()
                    header_y = h - margin - 2
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
                            h - margin - row * row_h - 0.15 * row_h - header_height
                        )
                        WorksheetGenerator._draw_single(c, p, x, y)
                    page_idx += 1
        self._draw_answer_key(c, w, h)
        c.save()

    def _draw_answer_key(self, c, width, height):
        """Draw the answer key for all problems on a new PDF page."""
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
    """Parse a string like '2..12' into a tuple (2, 12)."""
    try:
        a, b = map(int, txt.split(".."))
        if a > b:
            raise ValueError
        return a, b
    except ValueError:
        raise ValueError("Range must be 'min..max' with min ≤ max")

def make_problems(cls, n, term1_range, term2_range):
    """Generate a list of n unique problems for the given class and ranges."""
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