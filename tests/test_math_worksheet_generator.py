import math
import unittest

from run import MathWorksheetGenerator as Mg


class TestStringMethods(unittest.TestCase):

    def test_generate_question_addition(self):
        g = Mg(type_='+', max_number=9, question_count=10)
        question = g.generate_question()
        self.assertEqual(question[0] + question[2], question[3])

    def test_generate_question_subtraction(self):
        g = Mg(type_='-', max_number=9, question_count=10)
        question = g.generate_question()
        self.assertEqual(question[0] - question[2], question[3])
        # answer should be greater than 0
        self.assertGreaterEqual(question[3], 0)

    def test_generate_question_multiplication(self):
        g = Mg(type_='x', max_number=9, question_count=10)
        question = g.generate_question()
        self.assertEqual(question[0] * question[2], question[3])

    def test_generate_question_unsupport_type_(self):
        g = Mg(type_='p', max_number=9, question_count=10)
        with self.assertRaisesRegex(RuntimeError, expected_regex=r"Question main_type p not supported"):
            g.generate_question()

    def test_get_list_of_questions_correct_count(self):
        g = Mg(type_='x', max_number=9, question_count=10)
        question_list = g.get_list_of_questions(g.question_count)
        self.assertEqual(len(question_list), g.question_count)

    def test_make_question_page_page_count(self):
        g = Mg(type_='x', max_number=9, question_count=2)
        question_info = [[1, '+', 1, 2]] * g.question_count
        g.make_question_page(question_info)
        total_page = math.ceil(g.question_count / (g.num_x_cell * g.num_y_cell))
        self.assertEqual(total_page, g.pdf.page)


if __name__ == '__main__':
    unittest.main()
