from transformers import AutoModelForCausalLM, AutoTokenizer, AutoModelForQuestionAnswering
import time
import torch
device = "cpu"  # for GPU usage or "cpu" for CPU usage

text = """BODY: 78% GOTTON, 22%
POLYESTER
SIDE PANELS & RUB TRIM: 975,
COTTON, 3% ELASTANE
CORPS: TE% COTON, 22%"""

prompt = """
        based on the information tag given on the clothing please answer the following questions
        
        Is this piece of clothing easy to wash?

        Is this piece of clothing environmentally friendly?
        
        The following text enclosed in ``` is the clothing tag details: \n
        ```\n""" + text +"\n```"

from transformers import AutoModelForCausalLM, AutoTokenizer

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



