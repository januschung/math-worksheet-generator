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

    def test_generate_question_division(self):
        g = Mg(type_='/', max_number=9, question_count=10)
        question = g.generate_question()
        self.assertEqual(question[0] / question[2], question[3])

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

    def test_factors_two_digits(self):
        g = Mg(type_='x', max_number=9, question_count=2)
        expect_factors = {1, 2, 4, 13, 26, 52}
        self.assertEqual(expect_factors, g.factors(52))

    def test_factors_three_digits(self):
        g = Mg(type_='x', max_number=9, question_count=2)
        expect_factors = {1, 2, 3, 4, 6, 12, 73, 146, 219, 292, 438, 876}
        self.assertEqual(expect_factors, g.factors(876))

    def test_division_helper_zero_input(self):
        g = Mg(type_='x', max_number=9, question_count=2)
        division_info = g.division_helper(0)
        self.assertNotEqual(0, division_info[0])

    def test_division_helper_divisor_not_equal_one_nor_dividend(self):
        g = Mg(type_='x', max_number=9, question_count=2)
        division_info = g.division_helper(876)
        self.assertNotEqual(1, division_info[0])
        self.assertNotEqual(division_info[2], division_info[0])

    def test_division_helper_divisor_answer_type_is_int(self):
        g = Mg(type_='x', max_number=9, question_count=2)
        division_info = g.division_helper(876)
        self.assertIs(type(division_info[2]), int)


if __name__ == '__main__':
    unittest.main()
