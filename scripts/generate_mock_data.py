import cv2
import numpy as np
import os

def create_omr_template(width=600, height=800, num_questions=5, options=4):
    # Create white image
    img = np.ones((height, width, 3), dtype=np.uint8) * 255
    
    # Draw some fiducial markers (anchors) for ORB to catch onto
    # Top-left
    cv2.rectangle(img, (20, 20), (100, 100), (0, 0, 0), -1)
    cv2.rectangle(img, (30, 30), (90, 90), (255, 255, 255), -1)
    cv2.rectangle(img, (40, 40), (80, 80), (0, 0, 0), -1)
    
    # Top-right
    cv2.rectangle(img, (width-100, 20), (width-20, 100), (0, 0, 0), -1)
    cv2.rectangle(img, (width-90, 30), (width-30, 90), (255, 255, 255), -1)
    cv2.rectangle(img, (width-80, 40), (width-40, 80), (0, 0, 0), -1)
    
    # Bottom-left
    cv2.rectangle(img, (20, height-100), (100, height-20), (0, 0, 0), -1)
    cv2.rectangle(img, (30, height-90), (90, height-30), (255, 255, 255), -1)
    cv2.rectangle(img, (40, height-80), (80, height-40), (0, 0, 0), -1)

    # Bottom-right
    cv2.rectangle(img, (width-100, height-100), (width-20, height-20), (0, 0, 0), -1)
    cv2.rectangle(img, (width-90, height-90), (width-30, height-30), (255, 255, 255), -1)
    cv2.rectangle(img, (width-80, height-80), (width-40, height-40), (0, 0, 0), -1)

    # Draw Title
    cv2.putText(img, "OMR SHEET", (width//2 - 100, 150), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,0,0), 3)

    # Draw Bubbles
    start_y = 250
    gap_y = 60
    start_x = 150
    gap_x = 60
    
    bubble_coords = [] # Store (q_idx, opt_idx, x, y, r)

    for q in range(num_questions):
        y = start_y + q * gap_y
        cv2.putText(img, f"Q{q+1}", (50, y + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 2)
        
        row_coords = []
        for opt in range(options):
            x = start_x + opt * gap_x
            # Draw circle outline
            cv2.circle(img, (x, y), 20, (0, 0, 0), 2)
            cv2.putText(img, chr(65+opt), (x-10, y+10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 1)
            row_coords.append((x, y))
        bubble_coords.append(row_coords)

    return img, bubble_coords

def create_filled_sheet(template, bubble_coords, answers):
    filled = template.copy()
    
    for q_idx, ans_idx in enumerate(answers):
        if ans_idx is not None:
            x, y = bubble_coords[q_idx][ans_idx]
            # Simulate filling: Draw a filled circle, maybe slightly imperfect
            cv2.circle(filled, (x, y), 18, (0, 0, 0), -1)
            
    return filled

def apply_perspective_distortion(img):
    rows, cols, ch = img.shape
    
    # Define source points (corners of the image)
    pts1 = np.float32([[0, 0], [cols, 0], [0, rows], [cols, rows]])
    
    # Define destination points (simulate a slight tilt/rotation)
    # Squeeze the top, widen the bottom, shift a bit
    pts2 = np.float32([
        [cols*0.1, rows*0.1],       # Top-left moved in
        [cols*0.95, rows*0.05],     # Top-right moved in and up
        [cols*0.05, rows*0.9],      # Bottom-left moved in
        [cols*0.9, rows*0.95]       # Bottom-right moved in
    ])
    
    M = cv2.getPerspectiveTransform(pts1, pts2)
    dst = cv2.warpPerspective(img, M, (cols, rows), borderValue=(255,255,255))
    return dst

if __name__ == "__main__":
    # Ensure dirs exist
    os.makedirs("data/template", exist_ok=True)
    os.makedirs("data/inputs", exist_ok=True)

    # 1. Create Template
    template_img, coords = create_omr_template()
    cv2.imwrite("data/template/template.jpg", template_img)
    print("Template created at data/template/template.jpg")
    
    # Save coords for config (simplified print for now, will be used in config.yaml)
    print("Bubble Coords (approx):", coords)

    # 2. Create Filled Sheet (Perfect)
    # Answers: 0:A, 1:B, 2:A, 3:C, 4:D
    answers = [0, 1, 0, 2, 3] 
    filled_img = create_filled_sheet(template_img, coords, answers)
    
    # 3. Distort it to simulate mobile capture
    distorted_img = apply_perspective_distortion(filled_img)
    
    # Add some noise/blur
    distorted_img = cv2.GaussianBlur(distorted_img, (5, 5), 0)
    
    cv2.imwrite("data/inputs/sample_sheet.jpg", distorted_img)
    print("Sample input created at data/inputs/sample_sheet.jpg")
