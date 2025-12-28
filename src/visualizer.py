import cv2
import numpy as np

def draw_results(image, grading_details, roi_config):
    """
    Draws the grading results on the image.
    Green circle for correct, Red for incorrect.
    """
    output_img = image.copy()
    
    start_x = roi_config['start_x']
    start_y = roi_config['start_y']
    gap_x = roi_config['gap_x']
    gap_y = roi_config['gap_y']
    
    for detail in grading_details:
        q_idx = detail['question'] - 1
        user_ans = detail['user_ans']
        correct_ans = detail['correct_ans']
        is_correct = detail['is_correct']
        
        y = start_y + q_idx * gap_y
        
        # Draw Correct Answer (Green Outline)
        cx_correct = start_x + correct_ans * gap_x
        cv2.circle(output_img, (cx_correct, y), 25, (0, 255, 0), 3)
        
        # If user was wrong, draw their answer in Red
        if not is_correct and user_ans is not None:
            cx_user = start_x + user_ans * gap_x
            cv2.circle(output_img, (cx_user, y), 25, (0, 0, 255), 3)
            
    return output_img

def load_image(path):
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(f"Image not found at {path}")
    return img
