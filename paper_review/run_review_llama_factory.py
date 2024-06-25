from llmtuner import ChatModel
from llmtuner.extras.misc import torch_gc
import argparse
import json
from tqdm import tqdm
import os
import sys

def read_txt_file(path):
    with open(path, 'r') as f:
        content = f.read()
    return content

def read_json_file(path):
    with open(path, 'r') as f:
        data = json.load(f)
    return data

def save_output(output, save_dir, data_id):
    with open(save_dir + data_id + ".txt", 'w') as f:
        f.write(output)
    print(f"The summary review of paper {data_id} has been saved.")
    f.close()

def get_subfile(path):
    subfiles = [d for d in os.listdir(path) if os.path.isfile(os.path.join(path, d))]
    return subfiles

def infer_one(mmd_file_path,chat_model):
    system_prompt_dict = read_json_file(os.path.join(os.path.dirname(os.path.abspath(__file__)),"template.json"))
    instruction = system_prompt_dict['instruction_e']
    paper = read_txt_file(mmd_file_path)
    idx = paper.find("## References")
    paper = paper[:idx].strip()
    prompt = instruction + '\n' + paper
    
    messages = [
        {"role": "user", "content": prompt},
    ]

    response = chat_model.chat(messages)[0].response_text
    return response

def init_model_llama_factory():
    args_to_filter = ['--infer_type']
    sys.argv = [arg for i, arg in enumerate(sys.argv) if all(arg != filter_arg and (i == 0 or sys.argv[i - 1] != filter_arg) for filter_arg in args_to_filter)]
    chat_model = ChatModel()
    return chat_model


def run_review_llama_factory(mmd_file_path,args,chat_model):
    infer_modelname = args.model_name_or_path.split('/')[-2]
    infer_save_path = "./" + infer_modelname + '/'
    print(infer_modelname)
    if not os.path.exists(infer_save_path):
        os.mkdir(infer_save_path)
    res = infer_one(mmd_file_path,chat_model)
    return res
