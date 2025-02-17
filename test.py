from transformers import AutoModelForCausalLM, AutoTokenizer, AutoModelForQuestionAnswering
import time
import torch
device = "cpu"  # for GPU usage or "cpu" for CPU usage

# tokenizer = AutoTokenizer.from_pretrained("HuggingFaceTB/cosmo-1b")
# model = AutoModelForCausalLM.from_pretrained("HuggingFaceTB/cosmo-1b").to(device)
# prompt = "Photosynthesis is"

# inputs = tokenizer(prompt, return_tensors="pt").to(device)

# start = time.time()
# output = model.generate(**inputs, max_length=300, do_sample=True, temperature=0.6, top_p=0.95, repetition_penalty=1.2)
# print(tokenizer.decode(output[0]))
# end = time.time()

# print("time passed: " + str((end - start)))

text = """BODY: 78% GOTTON, 22%
POLYESTER
SIDE PANELS & RUB TRIM: 975,
COTTON, 3% ELASTANE
CORPS: TE% COTON, 22%"""

prompt = """You will act as a professional clothing designer.
        based on the information tag given on the clothing please answer the following questions
        
        Is this piece of clothing easy to wash?

        Is this piece of clothing environmentally friendly?
        
        The following text enclosed in ``` is the clothing tag details: \n
        ```\n""" + text +"\n```"
# Use a pipeline as a high-level helper
from transformers import pipeline 


start = time.time()
tokenizer = AutoTokenizer.from_pretrained("facebook/MobileLLM-125M", use_fast=False)
model = AutoModelForCausalLM.from_pretrained("facebook/MobileLLM-125M", trust_remote_code=True)

inputs = tokenizer(prompt, return_tensors="pt").to(device)
# pipe = pipeline("text-generation", model="facebook/MobileLLM-125M", trust_remote_code=True)
out = model.generate(**inputs, min_length = 100, max_length=500, do_sample=True, temperature=0.6, top_p=0.95, repetition_penalty=1.2)
print(tokenizer.decode(out[0]))
end = time.time()

print("time passed: " + str((end - start)))