from ultralytics import YOLO
import cv2
import numpy as np
import random
import matplotlib.pyplot as plt

# Load the model
model = YOLO("best.pt")

image_path = "download.png"  # Path to your image

# Perform inference
results = model(image_path, device="cpu", batch=1)

# Load original image
image = cv2.imread(image_path)
original_h, original_w = image.shape[:2]

# Copy to draw filled contours
overlay = image.copy()

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

        # Random color
        color = [random.randint(0, 255) for _ in range(3)]

        # Fill the contour with color
        cv2.drawContours(overlay, contours, -1, color, thickness=cv2.FILLED)

# Convert BGR to RGB for matplotlib
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
overlay_rgb = cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB)

# Display the images using matplotlib
plt.figure(figsize=(10, 5))

# Original Image
plt.subplot(1, 2, 1)
plt.imshow(image_rgb)
plt.title("Original Image")
plt.axis("off")

# Segmented Image
plt.subplot(1, 2, 2)
plt.imshow(overlay_rgb)
plt.title("Segmented Image (Filled Contours)")
plt.axis("off")

plt.tight_layout()
plt.show()