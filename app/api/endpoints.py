from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
import numpy as np
import cv2
import base64
import tempfile
from app.services.yolo_segmentation import segment_rooms

router = APIRouter()

@router.post("/segment-rooms/")
def segment_rooms_api(file: UploadFile = File(...)):
    # Save uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name

    # Run segmentation
    overlay, room_polygons = segment_rooms(tmp_path)

    # Encode overlay image as base64
    _, buffer = cv2.imencode('.png', overlay)
    overlay_base64 = base64.b64encode(buffer).decode('utf-8')

    # Convert polygons to JSON-serializable format
    polygons_json = [contour.squeeze().tolist() for contour in room_polygons if contour.shape[0] > 2]

    return JSONResponse({
        "overlay_image_base64": overlay_base64,
        "room_polygons": polygons_json
    })
