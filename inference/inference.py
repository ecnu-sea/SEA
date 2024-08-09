from transformers import AutoModelForCausalLM, AutoTokenizer
import json
from tqdm import tqdm
import os

model_name = "/path/to/SEA-E/"
tokenizer = AutoTokenizer.from_pretrained(model_name)
chat_model = AutoModelForCausalLM.from_pretrained(model_name)
chat_model.to("cuda:0")


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

def infer_one(mmd_file_path):
    system_prompt_dict = read_json_file(os.path.join(os.path.dirname(os.path.abspath(__file__)),"template.json"))
    instruction = system_prompt_dict['instruction_e']
    paper = read_txt_file(mmd_file_path)
    idx = paper.find("## References")
    paper = paper[:idx].strip()
    # prompt = instruction + '\n' + paper
    
    messages = [
        {"role": "system", "content": instruction},
        {"role": "user", "content": paper},
    ]
    encodes = tokenizer.apply_chat_template(messages, return_tensors="pt")
    encodes = encodes.to("cuda:0")
    len_input = encodes.shape[1]
    generated_ids = chat_model.generate(encodes,max_new_tokens=8192,do_sample=True)
    response = tokenizer.batch_decode(generated_ids[: , len_input:])[0]
    return response
def run_review(mmd_file_path):
    infer_modelname = model_name.split('/')[-2]
    infer_save_path = "./" + infer_modelname + '/'
    print(infer_modelname)
    if not os.path.exists(infer_save_path):
        os.mkdir(infer_save_path)
    res = infer_one(mmd_file_path)
    return res


if __name__ == "__main__":
    review = run_review("/path/to")
    print(review)
