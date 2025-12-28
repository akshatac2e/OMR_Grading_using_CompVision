import unittest
import numpy as np
import cv2
from src.grader import OMRGrader

class TestOMRGrader(unittest.TestCase):
    def setUp(self):
        self.config = {
            'roi': {'start_x': 10, 'start_y': 10, 'gap_x': 20, 'gap_y': 20, 'radius': 5},
            'exam': {'num_questions': 1, 'options_per_question': 4, 'answer_key': [0]},
            'processing': {'block_size': 11, 'c_value': 2}
        }
        self.grader = OMRGrader(self.config)

    def test_grade_sheet_perfect_match(self):
        # Create a synthetic aligned image
        # White background
        img = np.ones((100, 100, 3), dtype=np.uint8) * 255
        
        # Draw a "filled" bubble at the first position (Answer A / index 0)
        # Center is (10, 10)
        cv2.circle(img, (10, 10), 5, (0, 0, 0), -1)
        
        user_answers, _, _ = self.grader.grade_sheet(img)
        
        self.assertEqual(user_answers[0], 0)

    def test_grade_sheet_empty(self):
        img = np.ones((100, 100, 3), dtype=np.uint8) * 255
        user_answers, _, _ = self.grader.grade_sheet(img)
        self.assertIsNone(user_answers[0])

if __name__ == '__main__':
    unittest.main()
