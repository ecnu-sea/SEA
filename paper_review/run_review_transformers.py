import argparse
import json
from tqdm import tqdm
import os
import sys
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from paper_review.utils import *


def infer_one(mmd_file_path,chat_model,tokenizer):
    system_prompt_dict = read_json_file(os.path.join(os.path.dirname(os.path.abspath(__file__)),"template.json"))
    instruction = system_prompt_dict['instruction_e']
    paper = read_txt_file(mmd_file_path)
    idx = paper.find("## References")
    paper = paper[:idx].strip()
    
    messages = [
        {"role": "system", "content": instruction},
        {"role": "user", "content": paper},
    ]
    encodes = tokenizer.apply_chat_template(messages, return_tensors="pt")
    encodes = encodes.to(get_device())
    len_input = encodes.shape[1]
    generated_ids = chat_model.generate(encodes,max_new_tokens=8192,do_sample=True)
    response = tokenizer.batch_decode(generated_ids[: , len_input:])[0]
    return response

def get_device():
    cuda_visible_devices = os.getenv("CUDA_VISIBLE_DEVICES","0")
    # Get GPU device list
    device_ids = [int(id) for id in cuda_visible_devices.split(',')]
    device = torch.device("cpu")
    # Set the current device
    if torch.cuda.is_available():
        device = torch.device(f"cuda:{device_ids[0]}")
    else:
        device = torch.device("cpu")
    return device
    
def init_model_transformers(args):
    model_name = args.model_name_or_path
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    chat_model = AutoModelForCausalLM.from_pretrained(model_name)
    chat_model.to(get_device())
    return chat_model,tokenizer

def run_review_transformers(mmd_file_path,args,chat_model,tokenizer):
    infer_modelname = args.model_name_or_path.split('/')[-2]
    infer_save_path = "./" + infer_modelname + '/'
    print(infer_modelname)
    if not os.path.exists(infer_save_path):
        os.mkdir(infer_save_path)
    res = infer_one(mmd_file_path,chat_model,tokenizer)
    return res
