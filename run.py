"""
A module for creating .pdf math worksheets
"""

__author__ = 'januschung'

import argparse
import random
from fpdf import FPDF
from functools import reduce
from typing import List, Tuple

QuestionInfo = Tuple[int, str, int, int]


class MathWorksheetGenerator:
    """class for generating math worksheet of specified size and main_type"""
    def __init__(self, type_: str, max_number: int, question_count: int):
        self.main_type = type_
        self.max_number = max_number
        self.question_count = question_count
        self.pdf = FPDF()

        self.small_font_size = 10
        self.middle_font_size = 15
        self.large_font_size = 30
        self.size = 21
        self.tiny_pad_size = 2
        self.pad_size = 10
        self.large_pad_size = 30
        self.num_x_cell = 4
        self.num_y_cell = 2
        self.font_1 = 'Times'
        self.font_2 = 'Arial'

    # From https://stackoverflow.com/questions/6800193/what-is-the-most-efficient-way-of-finding-all-the-factors-of-a
    # -number-in-python
    def factors(self, n: int):
        return set(reduce(list.__add__,
                          ([i, n//i] for i in range(1, int(n**0.5) + 1) if n % i == 0)))

    def division_helper(self, num) -> [int, int, int]:
        # prevent num = 0 or divisor = 1 or divisor = dividend
        factor = 1
        while not num or factor == 1 or factor == num:
            num = random.randint(0, self.max_number)
        # pick a factor of num; answer will always be an integer
            if num:
                factor = random.sample(self.factors(num), 1)[0]
        answer = int(num / factor)
        return [num, factor, answer]

    def generate_question(self) -> QuestionInfo:
        """Generates each question and calculate the answer depending on the type_ in a list
        To keep it simple, number is generated randomly within the range of 0 to 100
        :return:  list of value1, main_type, value2, and answer for the generated question
        """
        num_1 = random.randint(0, self.max_number)
        num_2 = random.randint(0, self.max_number)
        if self.main_type == 'mix':
            current_type = random.choice(['+', '-', 'x', '/'])
        else:
            current_type = self.main_type

        if current_type == '+':
            answer = num_1 + num_2
        elif current_type == '-':
            #  avoid having a negative answer which is an advanced concept
            num_1, num_2 = sorted((num_1, num_2), reverse=True)
            answer = num_1 - num_2
        elif current_type == 'x':
            answer = num_1 * num_2
        elif current_type == '/':
            num_1, num_2, answer = self.division_helper(num_1)

        else:
            raise RuntimeError(f'Question main_type {current_type} not supported')
        return num_1, current_type, num_2, answer

    def get_list_of_questions(self, question_count: int) -> List[QuestionInfo]:
        """Generate all the questions for the worksheet in a list. Initially trying for unique questions, but
        allowing duplicates if needed (e.g. asking for 80 addition problems with max size 3 requires duplication)
        :return: list of questions
        """
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
        x_cor = self.pdf.get_x() - 3
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
        self.pdf.cell(self.large_pad_size, self.large_pad_size, txt='Answers', ln=1, align='C')

        for i in range(len(data)):
            self.pdf.set_font(self.font_1, size=self.small_font_size)
            self.pdf.cell(self.pad_size, self.pad_size, txt=f'{i + 1}:', border='TLB', align='R')
            self.pdf.set_font(self.font_2, size=self.small_font_size)
            self.pdf.cell(self.pad_size, self.pad_size, txt=str(data[i][3]), border='TB', align='R')
            self.pdf.cell(self.tiny_pad_size, self.pad_size, border='TRB', align='R')
            self.pdf.cell(self.tiny_pad_size, self.pad_size, align='C')
            if i >= 9 and (i + 1) % 10 == 0:
                self.pdf.ln()


def main(type_, size, question_count, filename):
    """main function"""
    new_pdf = MathWorksheetGenerator(type_, size, question_count)
    seed_question = new_pdf.get_list_of_questions(question_count)
    new_pdf.make_question_page(seed_question)
    new_pdf.make_answer_page(seed_question)
    new_pdf.pdf.output(filename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Generate Maths Addition/Subtraction/Multiplication Exercise Worksheet'
    )
    parser.add_argument(
        '--type',
        default='+',
        choices=['+', '-', 'x', '/', 'mix'],
        help='type of calculation: '
        '+: Addition; '
        '-: Subtraction; '
        'x: Multiplication; '
        '/: Division; '
        'mix: Mixed; '
        '(default: +)',
    )
    parser.add_argument(
        '--digits',
        default='2',
        choices=['1', '2', '3'],
        help='range of numbers: 1: 0-9, 2: 0-99, 3: 0-999' '(default: 2 -> 0-99)',
    )
    parser.add_argument(
        '-q',
        '--question_count',
        type=int,
        default='80',  # Must be a multiple of 40
        help='total number of questions' '(default: 80)',
    )
    parser.add_argument('--output', metavar='filename.pdf', default='worksheet.pdf',
                        help='Output file to the given filename '
                             '(default: worksheet.pdf)')
    args = parser.parse_args()

    # how many places, 1:0-9, 2:0-99, 3:0-999
    if args.digits == "1":
        size_ = 9
    elif args.digits == "3":
        size_ = 999
    else:
        size_ = 99

    main(args.type, size_, args.question_count, args.output)
