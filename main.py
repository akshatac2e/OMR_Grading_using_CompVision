import argparse
import os
import cv2
from src.utils import load_config, setup_logging
from src.aligner import ImageAligner
from src.grader import OMRGrader
from src.visualizer import draw_results, load_image
import logging

logger = logging.getLogger(__name__)

def main():
    setup_logging()
    
    parser = argparse.ArgumentParser(description="OMR Grading System")
    parser.add_argument("--config", default="config/config.yaml", help="Path to config file")
    parser.add_argument("--input", help="Path to input image (overrides config)")
    args = parser.parse_args()

    # 1. Load Configuration
    config = load_config(args.config)
    
    input_path = args.input if args.input else config['paths']['input_image']
    template_path = config['paths']['template_image']
    output_dir = config['paths']['output_dir']
    
    os.makedirs(output_dir, exist_ok=True)

    try:
        # 2. Load Images
        logger.info(f"Loading input: {input_path}")
        input_img = load_image(input_path)
        logger.info(f"Loading template: {template_path}")
        template_img = load_image(template_path)

        # 3. Alignment
        aligner = ImageAligner(
            n_features=config['processing']['orb_nfeatures'],
            match_ratio=config['processing']['match_ratio']
        )
        aligned_img, H = aligner.align_image(input_img, template_img)
        
        # Save aligned image for debug
        cv2.imwrite(os.path.join(output_dir, "debug_aligned.jpg"), aligned_img)

        # 4. Grading
        grader = OMRGrader(config)
        user_answers, pixel_details, thresh_img = grader.grade_sheet(aligned_img)
        
        # Save threshold image for debug
        cv2.imwrite(os.path.join(output_dir, "debug_threshold.jpg"), thresh_img)

        # 5. Scoring
        score, grading_details = grader.calculate_score(user_answers)
        
        total_q = config['exam']['num_questions']
        percentage = (score / total_q) * 100
        
        logger.info(f"GRADING COMPLETE")
        logger.info(f"Score: {score}/{total_q} ({percentage:.2f}%)")
        
        print("\n--- Detailed Results ---")
        print(f"{'Q#':<5} {'User':<10} {'Correct':<10} {'Status':<10}")
        print("-" * 40)
        for d in grading_details:
            status = "✅" if d['is_correct'] else "❌"
            user_char = chr(65 + d['user_ans']) if d['user_ans'] is not None else "N/A"
            corr_char = chr(65 + d['correct_ans'])
            print(f"{d['question']:<5} {user_char:<10} {corr_char:<10} {status:<10}")
        print("-" * 40)

        # 6. Visualization
        result_img = draw_results(aligned_img, grading_details, config['roi'])
        
        # Add score text
        cv2.putText(result_img, f"Score: {percentage:.0f}%", (50, 100), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 4)
        
        output_path = os.path.join(output_dir, "result.jpg")
        cv2.imwrite(output_path, result_img)
        logger.info(f"Result image saved to {output_path}")

    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    main()
