import argparse
import random
from fpdf import FPDF


class maths_worksheet_generator():
    pdf = FPDF()
    # Basic settings
    small_font_size = 10
    middle_font_size = 15
    large_font_size = 30
    size = 21
    tiny_pad_size = 2
    pad_size = 10
    large_pad_size = 30
    num_x_cell = 4
    num_y_cell = 2
    total_question = 80  # Must be a multiple of 40
    font_1 = 'Times'
    font_2 = 'Arial'

    def generate_question(self, type, size):
        # Generate each question and calculate the answer depending on the type in a list
        # To keep it simple, number is generated randomly within the range of 0 to 100
        num_1 = random.randint(0, size)
        num_2 = random.randint(0, size)
        if type == 'mix':
            type = random.choice(['+', '-', 'x'])
        if type == '+':
            answer = num_1 + num_2
        elif type == '-':
            #avoid having negative numbers which is an advanced concept
            #swap num_2 with num_1
            if num_2 > num_1:
                num_3 = num_1
                num_1 = num_2
                num_2 = num_3
            answer = num_1 - num_2
        elif type == 'x':
            answer = num_1 * num_2
        else:
            raise RuntimeError('Question type {} not supported'.format(type))
        return [num_1, type, num_2, answer]

    def get_list_of_questions(self, type, size):
        # Generate all the questions for the worksheet in a list
        questions = []
        while len(questions) < self.total_question:
            new_question = self.generate_question(type, size)
            if new_question not in questions:
                questions.append(new_question)
        return questions

    def make_question_page(self, data):
        # Prepare a single page of question
        total_page = int(self.total_question / (self.num_x_cell * self.num_y_cell))
        for page in range(0, total_page):
            self.pdf.add_page(orientation='L')
            self.print_question_row(data, (page) * (2 * self.num_x_cell))
            self.print_horizontal_seperator()
            self.print_question_row(data, (page) * (2 * self.num_x_cell) + self.num_x_cell)

    def print_top_row(self, question_num):
        # Helper function to print first row of a question
        self.pdf.set_font(self.font_1, size=self.middle_font_size)
        self.pdf.cell(self.pad_size, self.pad_size, txt=question_num, border='LT', ln=0, align='C')
        self.pdf.cell(self.size, self.pad_size, border='T', ln=0, align='C')
        self.pdf.cell(self.size, self.pad_size, border='T', ln=0, align='C')
        self.pdf.cell(self.pad_size, self.pad_size, border='TR', ln=0, align='C')

    def print_second_row(self, num):
        # Helper function to print second row of a question
        self.pdf.set_font(self.font_2, size=self.large_font_size)
        self.pdf.cell(self.pad_size, self.size, border='L', ln=0, align='C')
        self.pdf.cell(self.size, self.size, border=0, ln=0, align='C')
        self.pdf.cell(self.size, self.size, txt=str(num), border=0, ln=0, align='R')
        self.pdf.cell(self.pad_size, self.size, border='R', ln=0, align='C')

    def print_third_row(self, num, type):
        # Helper function to print third row of a question
        self.pdf.set_font(self.font_2, size=self.large_font_size)
        self.pdf.cell(self.pad_size, self.size, border='L', ln=0, align='C')
        self.pdf.cell(self.size, self.size, txt=type, border=0, ln=0, align='L')
        self.pdf.cell(self.size, self.size, txt=str(num), border=0, ln=0, align='R')
        self.pdf.cell(self.pad_size, self.size, border='R', ln=0, align='C')

    def print_bottom_row(self):
        # Helper function to print bottom row of question
        self.pdf.set_font(self.font_2, size=self.large_font_size)
        self.pdf.cell(self.pad_size, self.size, border='LB', ln=0, align='C')
        self.pdf.cell(self.size, self.size, border='TB', ln=0, align='C')
        self.pdf.cell(self.size, self.size, border='TB', ln=0, align='R')
        self.pdf.cell(self.pad_size, self.size, border='BR', ln=0, align='C')

    def print_edge_vertical_seperator(self):
        # Print space between question for the top or bottom row
        self.pdf.cell(self.pad_size, self.pad_size, border=0, ln=0)

    def print_middle_vertical_seperator(self):
        # Print space betwen question for the second or third row
        self.pdf.cell(self.pad_size, self.size, border=0, ln=0)

    def print_horizontal_seperator(self):
        # Print line breaker between two rows of questions
        self.pdf.cell(self.size, self.size, border=0, ln=0, align='C')
        self.pdf.ln()

    def print_question_row(self, data, offset):
        # Print a single row of questions (total question in a row is set by num_x_cell)
        for x in range(0, self.num_x_cell):
            self.print_top_row(str(x + 1 + offset))
            self.print_edge_vertical_seperator()
        self.pdf.ln()
        for x in range(0, self.num_x_cell):
            self.print_second_row(data[x + offset][0])
            self.print_middle_vertical_seperator()
        self.pdf.ln()
        for x in range(0, self.num_x_cell):
            self.print_third_row(data[x + offset][2], data[x + offset][1])
            self.print_middle_vertical_seperator()
        self.pdf.ln()
        for _ in range(0, self.num_x_cell):
            self.print_bottom_row()
            self.print_edge_vertical_seperator()
        self.pdf.ln()

    def make_answer_page(self, data):
        # Print answer sheet
        self.pdf.add_page(orientation='L')
        self.pdf.set_font(self.font_1, size=self.large_font_size)
        self.pdf.cell(self.large_pad_size, self.large_pad_size, txt='Answers', border=0, ln=1, align='C')

        for i in range(len(data)):
            self.pdf.set_font(self.font_1, size=self.small_font_size)
            self.pdf.cell(self.pad_size, self.pad_size, txt='{}:'.format(i+1), border='TLB', ln=0, align='R')
            self.pdf.set_font(self.font_2, size=self.small_font_size)
            self.pdf.cell(self.pad_size, self.pad_size, txt=str(data[i][3]), border='TB', ln=0, align='R')
            self.pdf.cell(self.tiny_pad_size, self.pad_size, border='TRB', ln=0, align='R')
            self.pdf.cell(self.tiny_pad_size, self.pad_size, border=0, ln=0, align='C')
            if (i+1) >= 10 and (i+1) % 10 == 0:
                self.pdf.ln()


def main(type, size):
    new_pdf = maths_worksheet_generator()
    seed_question = new_pdf.get_list_of_questions(type, size)
    new_pdf.make_question_page(seed_question)
    new_pdf.make_answer_page(seed_question)
    new_pdf.pdf.output("worksheet.pdf")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate Maths Addition/Subtraction/Multiplication Exercise Worksheet')
    parser.add_argument('--type', default='+', choices=['+', '-', 'x', 'mix'],
                        help='type of calculation: '
                             '+: Addition; '
                             '-: Substration; '
                             'x: Multipication; '
                             'mix: Mixed; '
                             '(default: +)')
    parser.add_argument('--digits', default='2', choices=['1', '2', '3'],
                        help='range of numbers: 1: 0-9, 2: 0-99, 3: 0-999'
                             '(default: 2 -> 0-99)')
    args = parser.parse_args()

    #how many places, 1:0-9, 2:0-99, 3:0-999
    if args.digits == "1":
        size = 9
    elif args.digits == "3":
        size = 999
    else:
        size = 99

    main(args.type, size)
