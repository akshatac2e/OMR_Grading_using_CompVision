import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

class OMRGrader:
    def __init__(self, config):
        self.config = config
        self.roi_config = config['roi']
        self.exam_config = config['exam']
        self.processing_config = config['processing']

    def preprocess(self, image):
        """
        Applies Gaussian Adaptive Thresholding to the aligned image.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Gaussian Adaptive Thresholding
        # 255 is the max value
        # ADAPTIVE_THRESH_GAUSSIAN_C is the algorithm
        # THRESH_BINARY_INV is the type (we want bubbles to be white, background black)
        thresh = cv2.adaptiveThreshold(
            gray, 
            255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 
            self.processing_config['block_size'], 
            self.processing_config['c_value']
        )
        return thresh

    def grade_sheet(self, aligned_image):
        """
        Grades the aligned OMR sheet.
        """
        logger.info("Starting grading process...")
        
        thresh_img = self.preprocess(aligned_image)
        
        num_questions = self.exam_config['num_questions']
        options_per_q = self.exam_config['options_per_question']
        
        start_x = self.roi_config['start_x']
        start_y = self.roi_config['start_y']
        gap_x = self.roi_config['gap_x']
        gap_y = self.roi_config['gap_y']
        radius = self.roi_config['radius']

        user_answers = []
        results = [] # Store details for visualization

        for q in range(num_questions):
            q_y = start_y + q * gap_y
            
            # Store pixel counts for each option in this question
            option_counts = []
            
            for opt in range(options_per_q):
                opt_x = start_x + opt * gap_x
                
                # Create a mask for the current bubble
                mask = np.zeros(thresh_img.shape, dtype="uint8")
                cv2.circle(mask, (opt_x, q_y), radius, 255, -1)
                
                # Apply mask to thresholded image and count non-zero pixels
                # bitwise_and is not strictly necessary if we just want to count pixels in the ROI
                # but it helps visualize if needed. 
                # More efficient: just slice the ROI if it was a rectangle, but for circles mask is best.
                mask_pixels = cv2.bitwise_and(thresh_img, thresh_img, mask=mask)
                total_pixels = cv2.countNonZero(mask_pixels)
                
                option_counts.append(total_pixels)
                results.append({
                    'q': q,
                    'opt': opt,
                    'x': opt_x,
                    'y': q_y,
                    'pixels': total_pixels
                })

            # Determine the marked answer (index with max pixels)
            # Simple heuristic: The one with the most white pixels is the marked one.
            # In a more complex system, we might check if the max value exceeds a threshold 
            # to detect empty answers or double marking.
            max_pixels = max(option_counts)
            
            # Threshold to ensure it's actually marked (e.g., > 20% of area)
            # Area of circle = pi * r^2. 20^2 * pi ~= 1256. 
            # Let's say at least 500 pixels.
            if max_pixels > 300: 
                marked_idx = option_counts.index(max_pixels)
            else:
                marked_idx = None # Unanswered
            
            user_answers.append(marked_idx)

        return user_answers, results, thresh_img

    def calculate_score(self, user_answers):
        correct_answers = self.exam_config['answer_key']
        score = 0
        grading_details = []

        for i, (user_ans, correct_ans) in enumerate(zip(user_answers, correct_answers)):
            is_correct = (user_ans == correct_ans)
            if is_correct:
                score += 1
            
            grading_details.append({
                'question': i + 1,
                'user_ans': user_ans,
                'correct_ans': correct_ans,
                'is_correct': is_correct
            })
            
        return score, grading_details
