import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

class ImageAligner:
    def __init__(self, n_features=5000, match_ratio=0.75):
        self.n_features = n_features
        self.match_ratio = match_ratio
        self.orb = cv2.ORB_create(nfeatures=n_features)
        # BFMatcher with Hamming distance (suitable for binary descriptors like ORB)
        self.bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)

    def align_image(self, image, template):
        """
        Aligns the input image to the template using ORB feature matching and Homography.
        """
        logger.info("Starting image alignment...")
        
        # Convert to grayscale
        gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

        # Detect keypoints and descriptors
        kp1, des1 = self.orb.detectAndCompute(gray_img, None)
        kp2, des2 = self.orb.detectAndCompute(gray_template, None)

        if des1 is None or des2 is None:
            raise ValueError("Could not detect features in one of the images.")

        logger.info(f"Detected {len(kp1)} keypoints in image and {len(kp2)} in template.")

        # Match descriptors
        matches = self.bf.knnMatch(des1, des2, k=2)

        # Apply Lowe's ratio test
        good_matches = []
        for m, n in matches:
            if m.distance < self.match_ratio * n.distance:
                good_matches.append(m)

        logger.info(f"Found {len(good_matches)} good matches.")

        if len(good_matches) < 4:
            raise ValueError("Not enough matches found to compute homography.")

        # Extract location of good matches
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

        # Find Homography
        H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

        # Warp image
        height, width, channels = template.shape
        aligned_img = cv2.warpPerspective(image, H, (width, height))

        return aligned_img, H
