#!/usr/bin/env python3
"""
Math Worksheet Generator

A flexible PDF worksheet generator for math practice problems.
Supports multiplication and addition with customizable number ranges.

Usage:
    python run.py --multiplication --n=100 --term1=2..15 --term2=2..20
    python run.py --addition --n=50 --term1=1..20 --term2=1..20 --output=homework.pdf

Features:
    - 50 problems per page in a 10x5 grid layout
    - Automatic answer key generation on final page
    - Right-aligned problem formatting for clean appearance
    - Extensible architecture for adding new operation types

Dependencies:
    pip install reportlab

Author: Math Worksheet Generator
"""

import argparse
import random
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

# Default values (easy to edit)
DEFAULT_N = 100
DEFAULT_TERM1_MIN = 2
DEFAULT_TERM1_MAX = 12
DEFAULT_TERM2_MIN = 2
DEFAULT_TERM2_MAX = 20
DEFAULT_OUTPUT = "worksheet.pdf"

class MathProblem:
    """Base class for math problems"""
    def __init__(self, term1, term2):
        self.term1 = term1
        self.term2 = term2
    
    def format_problem(self):
        """Return formatted problem as list of lines"""
        raise NotImplementedError
    
    def get_answer(self):
        """Return the answer"""
        raise NotImplementedError

class MultiplicationProblem(MathProblem):
    def format_problem(self):
        # Format for right-aligned numbers with proper spacing
        return [f"{self.term1}", f"x {self.term2}", "___"]
    
    def get_answer(self):
        return self.term1 * self.term2

class AdditionProblem(MathProblem):
    def format_problem(self):
        # Format for right-aligned numbers with proper spacing
        return [f"{self.term1}", f"+ {self.term2}", "___"]
    
    def get_answer(self):
        return self.term1 + self.term2

# Future operations can be added here:
# class SubtractionProblem(MathProblem):
#     def format_problem(self):
#         return f"{self.term1:>3}\n- {self.term2:>2}\n___"
#     
#     def get_answer(self):
#         return self.term1 - self.term2

class WorksheetGenerator:
    def __init__(self, problem_class, n, term1_range, term2_range, output_file):
        self.problem_class = problem_class
        self.n = n
        self.term1_range = term1_range
        self.term2_range = term2_range
        self.output_file = output_file
        self.problems = []
        
    def generate_problems(self):
        """Generate n random problems, avoiding duplicates in recent problems"""
        self.problems = []
        recent_problems = []  # Track recent problems to avoid duplicates
        max_recent = 10  # Number of recent problems to check for duplicates
        max_attempts = 50  # Prevent infinite loops if range is very small
        
        for _ in range(self.n):
            attempts = 0
            while attempts < max_attempts:
                term1 = random.randint(self.term1_range[0], self.term1_range[1])
                term2 = random.randint(self.term2_range[0], self.term2_range[1])
                
                # Check if this problem matches any recent problems
                problem_tuple = (term1, term2)
                if problem_tuple not in recent_problems:
                    problem = self.problem_class(term1, term2)
                    self.problems.append(problem)
                    
                    # Add to recent problems list
                    recent_problems.append(problem_tuple)
                    # Keep only the last max_recent problems
                    if len(recent_problems) > max_recent:
                        recent_problems.pop(0)
                    break
                
                attempts += 1
            else:
                # If we couldn't find a unique problem after max_attempts,
                # just add a duplicate (prevents infinite loop with small ranges)
                term1 = random.randint(self.term1_range[0], self.term1_range[1])
                term2 = random.randint(self.term2_range[0], self.term2_range[1])
                problem = self.problem_class(term1, term2)
                self.problems.append(problem)
    
    def create_pdf(self):
        """Create PDF with problems and answer key"""
        c = canvas.Canvas(self.output_file, pagesize=letter)
        width, height = letter
        
        # Problem pages
        self._draw_problem_pages(c, width, height)
        
        # Answer key page
        self._draw_answer_key(c, width, height)
        
        c.save()
        print(f"Worksheet saved as {self.output_file}")
    
    def _draw_problem_pages(self, c, width, height):
        """Draw the problem pages"""
        problems_per_page = 50
        cols = 10
        rows = 5
        
        # Calculate spacing
        margin = 0.5 * inch
        usable_width = width - 2 * margin
        usable_height = height - 2 * margin
        
        col_width = usable_width / cols
        row_height = usable_height / rows
        
        problem_index = 0
        
        while problem_index < len(self.problems):
            # Start new page
            if problem_index > 0:
                c.showPage()
            
            for row in range(rows):
                for col in range(cols):
                    if problem_index >= len(self.problems):
                        break
                    
                    problem = self.problems[problem_index]
                    
                    # Calculate position
                    x = margin + col * col_width + col_width * 0.1
                    y = height - margin - row * row_height - row_height * 0.2
                    
                    # Draw problem
                    self._draw_single_problem(c, problem, x, y)
                    
                    problem_index += 1
                
                if problem_index >= len(self.problems):
                    break
    
    def _draw_single_problem(self, c, problem, x, y):
        """Draw a single problem at the given position with proper alignment"""
        lines = problem.format_problem()
        line_height = 16  # Increased font size spacing
        
        # Set larger font for problems
        c.setFont("Helvetica", 14)
        
        # Calculate the maximum width needed for right alignment
        max_width = 0
        for line in lines:
            text_width = c.stringWidth(line, "Helvetica", 14)
            max_width = max(max_width, text_width)
        
        # Draw each line right-aligned
        for i, line in enumerate(lines):
            text_width = c.stringWidth(line, "Helvetica", 14)
            # Right-align by positioning based on max_width
            line_x = x + max_width - text_width
            line_y = y - i * line_height
            c.drawString(line_x, line_y, line)
    
    def _draw_answer_key(self, c, width, height):
        """Draw the answer key on the last page"""
        c.showPage()
        
        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(0.5 * inch, height - 0.5 * inch, "Answer Key")
        
        # Answers in compact grid
        c.setFont("Helvetica", 10)
        answers_per_row = 10
        margin = 0.5 * inch
        usable_width = width - 2 * margin
        col_width = usable_width / answers_per_row
        
        start_y = height - 1 * inch
        row_height = 15
        
        for i, problem in enumerate(self.problems):
            row = i // answers_per_row
            col = i % answers_per_row
            
            x = margin + col * col_width
            y = start_y - row * row_height
            
            answer_text = f"{i+1}. {problem.get_answer()}"
            c.drawString(x, y, answer_text)

def parse_range(range_str):
    """Parse range string like '2..15' into tuple (2, 15)"""
    try:
        min_val, max_val = map(int, range_str.split('..'))
        return (min_val, max_val)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Range must be in format 'min..max', got '{range_str}'")

def main():
    parser = argparse.ArgumentParser(
        description='Generate math worksheets with problems and answer keys',
        epilog='''Examples:
  %(prog)s --multiplication
  %(prog)s --addition --n=50 --term1=1..20 --term2=5..15
  %(prog)s --multiplication --term1=3..12 --term2=2..10 --output=homework.pdf''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Operation type (mutually exclusive)
    operation_group = parser.add_mutually_exclusive_group(required=True)
    operation_group.add_argument('--multiplication', action='store_true',
                                help='Generate multiplication problems')
    operation_group.add_argument('--addition', action='store_true',
                                help='Generate addition problems')
    
    # Problem parameters
    parser.add_argument('--n', type=int, default=DEFAULT_N, metavar='NUM',
                       help=f'Number of problems to generate (default: {DEFAULT_N})')
    parser.add_argument('--term1', type=parse_range, metavar='MIN..MAX',
                       default=f"{DEFAULT_TERM1_MIN}..{DEFAULT_TERM1_MAX}",
                       help=f'Range for first number, e.g., 2..15 (default: {DEFAULT_TERM1_MIN}..{DEFAULT_TERM1_MAX})')
    parser.add_argument('--term2', type=parse_range, metavar='MIN..MAX',
                       default=f"{DEFAULT_TERM2_MIN}..{DEFAULT_TERM2_MAX}",
                       help=f'Range for second number, e.g., 3..20 (default: {DEFAULT_TERM2_MIN}..{DEFAULT_TERM2_MAX})')
    parser.add_argument('--output', default=DEFAULT_OUTPUT, metavar='FILE',
                       help=f'Output PDF filename (default: {DEFAULT_OUTPUT})')
    
    args = parser.parse_args()
    
    # Determine problem type
    if args.multiplication:
        problem_class = MultiplicationProblem
    elif args.addition:
        problem_class = AdditionProblem
    
    # Generate worksheet
    generator = WorksheetGenerator(
        problem_class=problem_class,
        n=args.n,
        term1_range=args.term1,
        term2_range=args.term2,
        output_file=args.output
    )
    
    generator.generate_problems()
    generator.create_pdf()

if __name__ == "__main__":
    main()