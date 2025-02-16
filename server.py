import time
import socket
import cv2
import pytesseract
from PIL import Image
import easyocr
import math

pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'
HOST = "127.0.0.1"
PORT = 3222


def preprocess_image(src):
    """Applies various preprocessing techniques to enhance image quality for OCR"""
    # Read image and convert to grayscale
    image = cv2.imread(src)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Denoising using Non-Local Means (preserves edges better than median/Gaussian)
    denoised = cv2.fastNlMeansDenoising(gray, h=10, templateWindowSize=7, searchWindowSize=21)
    
    # Contrast Limited Adaptive Histogram Equalization (CLAHE)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    contrast_enhanced = clahe.apply(denoised)
    
    # Get current dimensions
    height, width = gray.shape
    current_max = max(height, width)
    max_size = 1000
    min_size = 300

    # Calculate scaling factor
    scale = 1.0
    if current_max > max_size:
        scale = max_size / current_max
    elif current_max < min_size:
        scale = min_size / current_max

    # Apply scaling with appropriate interpolation
    if scale != 1.0:
        interpolation = cv2.INTER_AREA if scale < 1 else cv2.INTER_CUBIC
        gray = cv2.resize(contrast_enhanced, None, fx=scale, fy=scale, 
                        interpolation=interpolation)
    
    # Adaptive thresholding for better handling of varying lighting conditions
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                  cv2.THRESH_BINARY, 21, 4)
    
    # Invert image if needed (OCR engines prefer black text on white background)
    inverted = cv2.bitwise_not(thresh)
    
    # Morphological operations to clean up the image
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
    processed = cv2.morphologyEx(inverted, cv2.MORPH_CLOSE, kernel)
    
    return processed


def run_socket_server():

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print(f"connected by {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                conn.sendall(data)

def read_image(src):
    image_processed = preprocess_image(src)

    text = pytesseract.image_to_string(image_processed, lang="eng", config="--psm 3")
    return text

def read_image_2(src):
    image = cv2.imread(src)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  
    # Get current dimensions
    height, width = gray.shape
    current_max = min(height, width)
    max_size = 1000
    min_size = 300

    # Calculate scaling factor
    scale = 1.0
    if current_max > max_size:
        scale = max_size / current_max
    elif current_max < min_size:
        scale = min_size / current_max

    # Apply scaling with appropriate interpolation
    if scale != 1.0:
        interpolation = cv2.INTER_AREA if scale < 1 else cv2.INTER_CUBIC
        resized = cv2.resize(gray, None, fx=scale, fy=scale, 
                        interpolation=interpolation)
    else:
        resized = gray

    print(resized.shape)

    # Apply Otsu's thresholding
    _, image_thresholded = cv2.threshold(resized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    text = pytesseract.image_to_string(image_thresholded, lang="eng", config="--psm 1")
    return text

def read_easyocr(src):
    reader = easyocr.Reader(["en"])
    text = reader.readtext(src,detail=0)
    return text
    

if __name__ == "__main__":        
    # run_socket_server()

    # text = read_image("./test/example.png")
    text2 = read_image_2("./test/example2.jpg")
    # text = read_easyocr("./test/example.png")
    # print(text)
    print("-----------------")
    print(text2)