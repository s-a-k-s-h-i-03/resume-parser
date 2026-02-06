import cv2
import pytesseract
from PIL import Image
import numpy as np

# OPTIONAL (Windows only):
# Uncomment and update if Tesseract is not in PATH
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_text_from_image(image_path: str) -> str:
    """
    Extract text from image resume using OCR.
    Returns plain text string.
    """

    # Load image using OpenCV
    image = cv2.imread(image_path)

    if image is None:
        return ""

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Noise removal
    gray = cv2.medianBlur(gray, 3)

    # Thresholding for better OCR
    thresh = cv2.adaptiveThreshold(
    gray,
    255,
    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    cv2.THRESH_BINARY,
    11,
    2
)


    # Convert OpenCV image to PIL format
    pil_image = Image.fromarray(thresh)

    # OCR configuration
    custom_config = r"--oem 3 --psm 6 -c preserve_interword_spaces=1"

    text = pytesseract.image_to_string(
        pil_image,
        config=custom_config
    )

    return text.strip()
