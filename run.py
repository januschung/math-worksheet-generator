"""
A module for creating .pdf math worksheets
"""

__author__ = 'januschung'

import argparse
import random
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from functools import reduce
from typing import List, Tuple, Dict

QuestionInfo = Tuple[int, str, int, int]


class MathWorksheetGenerator:
    """class for generating math worksheet of specified size and types"""
    def __init__(self, operation_config: Dict[str, int], question_count: int):
        self.operation_config = operation_config
        self.question_count = question_count
        self.pdf = FPDF()

        self.small_font_size = 8  # Decreased from 10 to 8
        self.middle_font_size = 12  # Decreased from 15 to 12
        self.large_font_size = 20  # Decreased from 30 to 20
        self.size = 16
        self.tiny_pad_size = 5  # Just used for the answer page
        self.pad_size = 4  # space between questions
        self.large_pad_size = 25  # Just used for the answer page
        self.num_x_cell = 5  # 5 columns of questions per page
        self.num_y_cell = 3  # 3 rows of questions per page
        self.font_1 = 'Times'
        self.font_2 = 'Helvetica'

    def factors(self, n: int):
        return set(reduce(list.__add__,
                          ([i, n//i] for i in range(1, int(n**0.5) + 1) if n % i == 0)))

    def division_helper(self, max_number) -> [int, int, int]:
        attempts = 0
        while attempts < 100:  # Limit attempts to prevent infinite loop
            num = random.randint(2, max_number)  # Start from 2 to avoid division by 1
            factors = list(self.factors(num))
            if len(factors) > 2:  # Check if there are factors other than 1 and the number itself
                factor = random.choice(factors[1:-1])  # Choose a factor that's not 1 or the number itself
                answer = num // factor
                return [num, factor, answer]
            attempts += 1
        
        # If we couldn't find a suitable number after 100 attempts, use a simple case
        return [4, 2, 2]  # A simple division problem as a fallback

    def generate_question(self) -> QuestionInfo:
        """Generates each question and calculate the answer depending on the type_ in a list"""
        current_type = random.choice(list(self.operation_config.keys()))
        max_number = self.operation_config[current_type]

        if current_type in ['+', '-', 'x']:
            num_1 = random.randint(0, max_number)
            num_2 = random.randint(0, max_number)
        elif current_type == '/':
            num_1, num_2, answer = self.division_helper(max_number)
            return num_1, current_type, num_2, answer

        if current_type == '+':
            answer = num_1 + num_2
        elif current_type == '-':
            num_1, num_2 = sorted((num_1, num_2), reverse=True)
            answer = num_1 - num_2
        elif current_type == 'x':
            answer = num_1 * num_2
        else:
            raise RuntimeError(f'Question type {current_type} not supported')

        return num_1, current_type, num_2, answer

    def get_list_of_questions(self, question_count: int) -> List[QuestionInfo]:
        """Generate all the questions for the worksheet in a list."""
        questions = []
        duplicates = 0
        while len(questions) < question_count:
            new_question = self.generate_question()
            if new_question not in questions or duplicates >= 10:
                questions.append(new_question)
            else:
                duplicates += 1
        return questions

    def make_question_page(self, data: List[QuestionInfo]):
        """Prepare a single page of questions"""
        page_area = self.num_x_cell * self.num_y_cell
        problems_per_page = self.split_arr(self.question_count, page_area)
        total_pages = len(problems_per_page)
        for page in range(total_pages):
            self.pdf.add_page(orientation='L')
            if problems_per_page[page] < self.num_x_cell:
                self.print_question_row(data, page * page_area, problems_per_page[page])
            else:
                problems_per_row = self.split_arr(problems_per_page[page], self.num_x_cell)
                total_rows = len(problems_per_row)
                self.print_question_row(data, page * page_area, problems_per_row[0])
                for row in range(1, total_rows):
                    page_row = row * self.num_x_cell
                    self.print_horizontal_separator()
                    self.print_question_row(data, page * page_area + page_row, problems_per_row[row])

    def split_arr(self, x: int, y: int):
        """Split x into x = y + y + ... + (x % y)"""
        quotient, remainder = divmod(x, y)
        if remainder != 0:
            return [y] * quotient + [remainder]
        return [y] * quotient

    def print_top_row(self, question_num: str):
        """Helper function to print first character row of a question row"""
        self.pdf.set_font(self.font_1, size=self.middle_font_size)
        self.pdf.cell(self.pad_size, self.pad_size, txt=question_num, border='LT', align='C')
        self.pdf.cell(self.size, self.pad_size, border='T')
        self.pdf.cell(self.size, self.pad_size, border='T')
        self.pdf.cell(self.pad_size, self.pad_size, border='TR')

    def print_second_row(self, num: int):
        """Helper function to print second character row of a question row"""
        self.pdf.set_font(self.font_2, size=self.large_font_size)
        self.pdf.cell(self.pad_size, self.size, border='L')
        self.pdf.cell(self.size, self.size)
        self.pdf.cell(self.size, self.size, txt=str(num), align='R')
        self.pdf.cell(self.pad_size, self.size, border='R')

    def print_second_row_division(self, num_1: int, num_2: int):
        """Helper function to print second character row of a question row for division"""
        self.pdf.set_font(self.font_2, size=self.large_font_size)
        self.pdf.cell(self.pad_size, self.size, border='L')
        self.pdf.cell(self.size, self.size, txt=str(num_2), align='R')
        x_cor = self.pdf.get_x() - 4  # Adjusted from -3 to -5 for better positioning
        y_cor = self.pdf.get_y()
        self.pdf.image(name='division.png', x=x_cor, y=y_cor)
        self.pdf.cell(self.size, self.size, txt=str(num_1), align='R')
        self.pdf.cell(self.pad_size, self.size, border='R')

    def print_third_row(self, num: int, current_type: str):
        """Helper function to print third character row of a question row"""
        self.pdf.cell(self.pad_size, self.size, border='L')
        self.pdf.cell(self.size, self.size, txt=current_type, align='L')
        self.pdf.cell(self.size, self.size, txt=str(num), align='R')
        self.pdf.cell(self.pad_size, self.size, border='R')

    def print_third_row_division(self):
        """Helper function to print third character row of a question row for division"""
        self.pdf.cell(self.pad_size, self.size, border='L')
        self.pdf.cell(self.size, self.size, align='L')
        self.pdf.cell(self.size, self.size, align='R')
        self.pdf.cell(self.pad_size, self.size, border='R')

    def print_bottom_row(self):
        """Helper function to print bottom row of question"""
        self.pdf.cell(self.pad_size, self.size, border='LB')
        self.pdf.cell(self.size, self.size, border='TB')
        self.pdf.cell(self.size, self.size, border='TB')
        self.pdf.cell(self.pad_size, self.size, border='BR')

    def print_bottom_row_division(self):
        """Helper function to print bottom row of question"""
        self.pdf.cell(self.pad_size, self.size, border='LB')
        self.pdf.cell(self.size, self.size, border='B')
        self.pdf.cell(self.size, self.size, border='B')
        self.pdf.cell(self.pad_size, self.size, border='BR')

    def print_edge_vertical_separator(self):
        """Print space between question for the top or bottom row"""
        self.pdf.cell(self.pad_size, self.pad_size)

    def print_middle_vertical_separator(self):
        """Print space between question for the second or third row"""
        self.pdf.cell(self.pad_size, self.size)

    def print_horizontal_separator(self):
        """Print line breaker between two rows of questions"""
        self.pdf.cell(self.size, self.size)
        self.pdf.ln()

    def print_question_row(self, data, offset, num_problems):
        """Print a single row of questions (total question in a row is set by num_x_cell)"""
        for x in range(0, num_problems):
            self.print_top_row(str(x + 1 + offset))
            self.print_edge_vertical_separator()
        self.pdf.ln()
        for x in range(0, num_problems):
            if data[x + offset][1] == '/':
                self.print_second_row_division(data[x + offset][0], data[x + offset][2])
            else:
                self.print_second_row(data[x + offset][0])
            self.print_middle_vertical_separator()
        self.pdf.ln()
        for x in range(0, num_problems):
            if data[x + offset][1] == '/':
                self.print_third_row_division()
            else:
                self.print_third_row(data[x + offset][2], data[x + offset][1])
            self.print_middle_vertical_separator()
        self.pdf.ln()
        for x in range(0, num_problems):
            if data[x + offset][1] == '/':
                self.print_bottom_row_division()
            else:
                self.print_bottom_row()
            self.print_edge_vertical_separator()
        self.pdf.ln()

    def make_answer_page(self, data):
        """Print answer sheet"""
        self.pdf.add_page(orientation='L')
        self.pdf.set_font(self.font_1, size=self.large_font_size)
        self.pdf.cell(self.large_pad_size, self.large_pad_size, txt='Answers', new_x=XPos.LEFT, new_y=YPos.NEXT, align='C')

        for i in range(len(data)):
            self.pdf.set_font(self.font_1, size=self.small_font_size)
            self.pdf.cell(self.pad_size * 2, self.pad_size, txt=f'{i + 1}:', border='TLB', align='R')  # Increased padding
            self.pdf.set_font(self.font_2, size=self.small_font_size)
            self.pdf.cell(self.pad_size * 2, self.pad_size, txt=str(data[i][3]), border='TB', align='R')  # Increased padding
            self.pdf.cell(self.tiny_pad_size, self.pad_size, border='TRB', align='R')
            self.pdf.cell(self.tiny_pad_size, self.pad_size, align='C')
            if i >= 9 and (i + 1) % 10 == 0:
                self.pdf.ln()


def main(operation_config, question_count, filename):
    """main function"""
    new_pdf = MathWorksheetGenerator(operation_config, question_count)
    seed_question = new_pdf.get_list_of_questions(question_count)
    new_pdf.make_question_page(seed_question)
    new_pdf.make_answer_page(seed_question)
    new_pdf.pdf.output(filename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Generate Mixed Math Exercise Worksheet with Different Difficulty Levels'
    )
    parser.add_argument(
        '--addition_max',
        type=int,
        default=99,
        help='Maximum number for addition problems (default: 99)'
    )
    parser.add_argument(
        '--subtraction_max',
        type=int,
        default=99,
        help='Maximum number for subtraction problems (default: 99)'
    )
    parser.add_argument(
        '--multiplication_max',
        type=int,
        default=15,
        help='Maximum number for multiplication problems (default: 15)'
    )
    parser.add_argument(
        '--division_max',
        type=int,
        default=99,
        help='Maximum number for division problems (default: 99)'
    )
    parser.add_argument(
        '-q',
        '--question_count',
        type=int,
        default=80,
        help='Total number of questions (default: 80)'
    )
    parser.add_argument(
        '--output',
        metavar='filename.pdf',
        default='worksheet.pdf',
        help='Output file to the given filename (default: worksheet.pdf)'
    )
    args = parser.parse_args()

    operation_config = {
        '+': args.addition_max,
        '-': args.subtraction_max,
        'x': args.multiplication_max,
        '/': args.division_max
    }

    main(operation_config, args.question_count, args.output)