from ultralytics import YOLO
import cv2
import numpy as np
import random
from typing import List, Tuple

# Load the model once at module level for efficiency
model = YOLO("backend/checkpoints/best.pt")

def segment_rooms(image_path: str) -> Tuple[np.ndarray, List[np.ndarray]]:
    """
    Segments rooms in a floorplan image using YOLO.
    Args:
        image_path (str): Path to the input image.
    Returns:
        overlay (np.ndarray): Image with filled room contours.
        room_polygons (List[np.ndarray]): List of room contours (polygons).
    """
    # Perform inference
    results = model(image_path, device="cpu", batch=1)

    # Load original image
    image = cv2.imread(image_path)
    original_h, original_w = image.shape[:2]
    overlay = image.copy()
    room_polygons = []

    # Get segmentation masks
    masks = results[0].masks
    if masks is not None:
        mask_array = masks.data.cpu().numpy()  # shape: (num_masks, h_mask, w_mask)
        for mask in mask_array:
            # Resize mask to original image size
            resized_mask = cv2.resize(mask, (original_w, original_h), interpolation=cv2.INTER_NEAREST)
            # Convert to binary uint8
            binary_mask = (resized_mask > 0.5).astype(np.uint8) * 255
            # Find contours
            contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            room_polygons.extend(contours)
            # Random color for each room
            color = [random.randint(0, 255) for _ in range(3)]
            # Fill the contour with color
            cv2.drawContours(overlay, contours, -1, color, thickness=cv2.FILLED)
    return overlay, room_polygons
