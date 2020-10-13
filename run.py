"""
A module for creating .pdf math worksheets
"""

__author__ = 'januschung'

import argparse
import random
from typing import List, Tuple

from fpdf import FPDF

QuestionInfo = Tuple[int, str, int, int]


class MathWorksheetGenerator:
    """class for generating math worksheet of specified size and main_type"""
    def __init__(self, type_: str, size: int):
        self.main_type = type_
        self.size = size
        self.pdf = FPDF()

        self.small_font_size = 10
        self.middle_font_size = 15
        self.large_font_size = 30
        self.size_ = 21
        self.tiny_pad_size = 2
        self.pad_size = 10
        self.large_pad_size = 30
        self.num_x_cell = 4
        self.num_y_cell = 2
        self.total_question = 80  # Must be a multiple of 40
        self.font_1 = 'Times'
        self.font_2 = 'Arial'

    def generate_question(self) -> QuestionInfo:
        """Generates each question and calculate the answer depending on the type_ in a list
        To keep it simple, number is generated randomly within the range of 0 to 100
        :return:  list of value1, main_type, value2, and answer for the generated question
        """
        num_1 = random.randint(0, self.size)
        num_2 = random.randint(0, self.size)
        if self.main_type == 'mix':
            current_type = random.choice(['+', '-', 'x'])
        else:
            current_type = self.main_type

        if current_type == '+':
            answer = num_1 + num_2
        elif current_type == '-':
            #  avoid having a negative answer which is an advanced concept
            num_1, num_2 = sorted((num_1, num_2))
            answer = num_1 - num_2
        elif current_type == 'x':
            answer = num_1 * num_2
        else:
            raise RuntimeError('Question main_type {} not supported'.format(current_type))
        return num_1, current_type, num_2, answer

    def get_list_of_questions(self) -> List[QuestionInfo]:
        """Generate all the questions for the worksheet in a list. Initially trying for unique questions, but
        allowing duplicates if needed (e.g. asking for 80 addition problems with max size 3 requires duplication)
        :return: list of questions
        """
        questions = []
        duplicates = 0
        while len(questions) < self.total_question:
            new_question = self.generate_question()
            if duplicates < 10:
                if new_question not in questions:
                    questions.append(new_question)
                else:
                    duplicates += 1
            else:
                questions.append(new_question)
        return questions

    def make_question_page(self, data: List[QuestionInfo]):
        """Prepare a single page of questions"""
        total_page = int(self.total_question / (self.num_x_cell * self.num_y_cell))
        for page in range(total_page):
            self.pdf.add_page(orientation='L')
            self.print_question_row(data, page * (2 * self.num_x_cell))
            self.print_horizontal_separator()
            self.print_question_row(data, page * (2 * self.num_x_cell) + self.num_x_cell)

    def print_top_row(self, question_num: str):
        """Helper function to print first character row of a question row"""
        self.pdf.set_font(self.font_1, size=self.middle_font_size)
        self.pdf.cell(self.pad_size, self.pad_size, txt=question_num, border='LT', align='C')
        self.pdf.cell(self.size, self.pad_size, border='T', align='C')
        self.pdf.cell(self.size, self.pad_size, border='T', align='C')
        self.pdf.cell(self.pad_size, self.pad_size, border='TR', align='C')

    def print_second_row(self, num: int):
        """Helper function to print second character row of a question row"""
        self.pdf.set_font(self.font_2, size=self.large_font_size)
        self.pdf.cell(self.pad_size, self.size, border='L', align='C')
        self.pdf.cell(self.size, self.size, align='C')
        self.pdf.cell(self.size, self.size, txt=str(num), align='R')
        self.pdf.cell(self.pad_size, self.size, border='R', align='C')

    def print_third_row(self, num: int, current_type: str):
        """Helper function to print third character row of a question row"""
        self.pdf.set_font(self.font_2, size=self.large_font_size)
        self.pdf.cell(self.pad_size, self.size, border='L', align='C')
        self.pdf.cell(self.size, self.size, txt=current_type, align='L')
        self.pdf.cell(self.size, self.size, txt=str(num), align='R')
        self.pdf.cell(self.pad_size, self.size, border='R', align='C')

    def print_bottom_row(self):
        """Helper function to print bottom row of question"""
        self.pdf.set_font(self.font_2, size=self.large_font_size)
        self.pdf.cell(self.pad_size, self.size, border='LB', align='C')
        self.pdf.cell(self.size, self.size, border='TB', align='C')
        self.pdf.cell(self.size, self.size, border='TB', align='R')
        self.pdf.cell(self.pad_size, self.size, border='BR', align='C')

    def print_edge_vertical_separator(self):
        """Print space between question for the top or bottom row"""
        self.pdf.cell(self.pad_size, self.pad_size)

    def print_middle_vertical_separator(self):
        """Print space between question for the second or third row"""
        self.pdf.cell(self.pad_size, self.size)

    def print_horizontal_separator(self):
        """Print line breaker between two rows of questions"""
        self.pdf.cell(self.size, self.size, align='C')
        self.pdf.ln()

    def print_question_row(self, data: List[QuestionInfo], offset: int):
        """Print a single row of questions (total question in a row is set by num_x_cell)"""
        for x in range(self.num_x_cell):
            self.print_top_row(str(x + 1 + offset))
            self.print_edge_vertical_separator()
        self.pdf.ln()
        for x in range(self.num_x_cell):
            self.print_second_row(data[x + offset][0])
            self.print_middle_vertical_separator()
        self.pdf.ln()
        for x in range(self.num_x_cell):
            self.print_third_row(data[x + offset][2], data[x + offset][1])
            self.print_middle_vertical_separator()
        self.pdf.ln()
        for _ in range(self.num_x_cell):
            self.print_bottom_row()
            self.print_edge_vertical_separator()
        self.pdf.ln()

    def make_answer_page(self, data: List[QuestionInfo]):
        """Print answer sheet"""
        self.pdf.add_page(orientation='L')
        self.pdf.set_font(self.font_1, size=self.large_font_size)
        self.pdf.cell(self.large_pad_size, self.large_pad_size, txt='Answers', ln=1, align='C')

        for i in range(len(data)):
            self.pdf.set_font(self.font_1, size=self.small_font_size)
            self.pdf.cell(self.pad_size, self.pad_size, txt='{}:'.format(i + 1), border='TLB', align='R')
            self.pdf.set_font(self.font_2, size=self.small_font_size)
            self.pdf.cell(self.pad_size, self.pad_size, txt=str(data[i][3]), border='TB', align='R')
            self.pdf.cell(self.tiny_pad_size, self.pad_size, border='TRB', align='R')
            self.pdf.cell(self.tiny_pad_size, self.pad_size, align='C')
            if (i+1) >= 10 and (i+1) % 10 == 0:
                self.pdf.ln()


def main(type_, size):
    """main function"""
    new_pdf = MathWorksheetGenerator(type_, size)
    seed_question = new_pdf.get_list_of_questions()
    new_pdf.make_question_page(seed_question)
    new_pdf.make_answer_page(seed_question)
    new_pdf.pdf.output("worksheet.pdf")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Generate Maths Addition/Subtraction/Multiplication Exercise Worksheet')
    parser.add_argument('--type_', default='+', choices=['+', '-', 'x', 'mix'],
                        help='type_ of calculation: '
                             '+: Addition; '
                             '-: Subtraction; '
                             'x: Multiplication; '
                             'mix: Mixed; '
                             '(default: +)')
    parser.add_argument('--digits', default='2', choices=['1', '2', '3'],
                        help='range of numbers: 1: 0-9, 2: 0-99, 3: 0-999'
                             '(default: 2 -> 0-99)')
    args = parser.parse_args()

    # how many places, 1:0-9, 2:0-99, 3:0-999
    if args.digits == "1":
        size_ = 9
    elif args.digits == "3":
        size_ = 999
    else:
        size_ = 99

    main(args.type, size_)
