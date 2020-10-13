"""
A module for creating .pdf math worksheets
"""

__author__ = 'januschung'

import argparse
import random
import sheetGenerator

from typing import List, Tuple

from fpdf import FPDF

def main(type_, size):
    """main function"""
    new_pdf = sheetGenerator.sheetGenerator(type_, size)
    seed_question = new_pdf.get_list_of_questions()
    new_pdf.make_question_page(seed_question)
    new_pdf.make_answer_page(seed_question)
    new_pdf.pdf.output("worksheet.pdf")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Generate Maths Addition/Subtraction/Multiplication Exercise Worksheet')
    parser.add_argument('--type', default='+', choices=['+', '-', 'x', 'mix'],
                        help='type of calculation: '
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
