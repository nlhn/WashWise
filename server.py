
import cv2
import pytesseract
from PIL import Image
from transformers import pipeline
from transformers import AutoModelForCausalLM, AutoTokenizer
from flask import request, Flask

pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'
HOST = "127.0.0.1"
PORT = 3222

app = Flask(__name__)
 
# decorator to associate 
# a function with the url
@app.route("/")
def showHomePage():
      # response from the server
    return "This is home page"

@app.route("/debug", methods=["POST"])
def debug():
    text = request.form["sample"]
    print(text)
    return "received" 
   
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

    # pipe = pipeline('text-generation', model='EleutherAI/gpt-neo-125M')
    
    prompt = """
            based on the information tag given on the clothing please answer the following questions
            
            Is this piece of clothing easy to wash?

            Is this piece of clothing environmentally friendly?
            
            The following text enclosed in ``` is the clothing tag details: \n
        ```\n""" + text +"\n```"

    model_name = "Qwen/Qwen2.5-0.5B-Instruct"

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype="auto",
        device_map="auto"
    )
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    messages = [
        {"role": "system", "content": "You are a professional fashion specialist that focuses on clothing materials"},
        {"role": "user", "content": prompt}
    ]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=1024
    )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]

    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

    return response

def write_analysis_to_text(text):
    with open("a.txt", "w") as f:
        f.write(text)

if __name__ == "__main__":

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

    # app.run(host="0.0.0.0")