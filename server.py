
import socket
import cv2
import pytesseract
from PIL import Image
from transformers import pipeline
from transformers import AutoModelForCausalLM, AutoTokenizer

pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'
HOST = "127.0.0.1"
PORT = 3222

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

    
def run_analysis(text):
    prompt = """You will act as a professional clothing designer.
        based on the information tag given please provide a short analysis on this peice of clothing.
        ``` """ + text +" ```"
    device = 'cpu'
    # pipe = pipeline('text-generation', model='EleutherAI/gpt-neo-125M')
    
    message = [
        {"role":"user", "content": prompt}
    ]

    # analysis = pipe(prompt,do_sample=True, min_length=100, max_length=1000)

    tokenizer = AutoTokenizer.from_pretrained("facebook/MobileLLM-125M", use_fast=False)
    model = AutoModelForCausalLM.from_pretrained("facebook/MobileLLM-125M", trust_remote_code=True)

    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    # pipe = pipeline("text-generation", model="facebook/MobileLLM-125M", trust_remote_code=True)
    analysis = model.generate(**inputs, min_length = 100, max_length=300, do_sample=True, temperature=0.6, top_p=0.95, repetition_penalty=1.2)
    print(analysis)
    return analysis

def write_analysis_to_text(text):
    with open("a.txt", "w") as f:
        f.write(text)

if __name__ == "__main__":

    # text2 = read_image("./test/example2.jpg")
    # print(text)

    text2 = """BODY: 78% GOTTON, 22%
POLYESTER
SIDE PANELS & RUB TRIM: 975,
COTTON, 3% ELASTANE
CORPS: TE% COTON, 22%
"""
    print("-----------------")
    print(text2)

    print("-------------------")
    out = run_analysis(text2)

    write_analysis_to_text(out)